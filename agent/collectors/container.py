import os
from datetime import datetime

def is_docker():
    # Check for /.dockerenv or cgroup
    if os.path.exists('/.dockerenv'):
        return True
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read() or 'containerd' in f.read()
    except Exception:
        return False

def is_kubernetes():
    return os.path.exists('/var/run/secrets/kubernetes.io') or \
           os.environ.get('KUBERNETES_SERVICE_HOST') is not None

def collect_docker_info():
    try:
        import docker
        client = docker.from_env()
        containers = []
        for c in client.containers.list(all=True):
            try:
                stats = c.stats(stream=False)
                containers.append({
                    'id': c.id,
                    'name': c.name,
                    'image': c.image.tags,
                    'status': c.status,
                    'created': c.attrs.get('Created'),
                    'ports': c.attrs.get('NetworkSettings', {}).get('Ports'),
                    'mounts': c.attrs.get('Mounts'),
                    'labels': c.labels,
                    'cpu_percent': stats['cpu_stats']['cpu_usage']['total_usage'] if 'cpu_stats' in stats else None,
                    'mem_usage': stats['memory_stats']['usage'] if 'memory_stats' in stats else None,
                    'networks': c.attrs.get('NetworkSettings', {}).get('Networks'),
                    'processes': c.top()['Processes'] if hasattr(c, 'top') else None,
                })
            except Exception as e:
                containers.append({'id': c.id, 'error': str(e)})
        images = [img.tags for img in client.images.list()]
        return {'containers': containers, 'images': images}
    except ImportError:
        return {'error': 'docker-py not installed'}
    except Exception as e:
        return {'error': str(e)}

def collect_k8s_info():
    # Stub: Full k8s info requires kubernetes Python client and config
    try:
        from kubernetes import client, config
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        pod_list = []
        for pod in pods.items:
            pod_list.append({
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'node': pod.spec.node_name,
                'status': pod.status.phase,
                'containers': [c.name for c in pod.spec.containers],
                'host_ip': pod.status.host_ip,
                'pod_ip': pod.status.pod_ip,
            })
        return {'pods': pod_list}
    except ImportError:
        return {'error': 'kubernetes Python client not installed'}
    except Exception as e:
        return {'error': str(e)}

def collect_container_info():
    """
    Collect Docker/Podman/K8s events, running containers/images, resource usage, and environment.
    Returns a dict.
    """
    result = {'timestamp': datetime.utcnow().isoformat(), 'container': {}}
    result['container']['is_docker'] = is_docker()
    result['container']['is_kubernetes'] = is_kubernetes()
    if result['container']['is_docker']:
        result['container']['docker_info'] = collect_docker_info()
    if result['container']['is_kubernetes']:
        result['container']['k8s_info'] = collect_k8s_info()
    # Podman and other runtimes can be added similarly
    return result
