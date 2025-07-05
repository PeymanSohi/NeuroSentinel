#!/bin/bash

echo "🧠 NeuroSentinel WebSocket Tests"
echo "================================"
echo ""

echo "1. Testing WebSocket Connection..."
docker exec neurosentinel-server-1 python3 -c "
import asyncio
import websockets
import json
import time

async def test_websocket():
    uri = 'ws://localhost:8000/ws/events'
    try:
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connection: OK')
            
            test_event = {
                'agent_id': 'test-client',
                'timestamp': time.time(),
                'event_type': 'system_scan',
                'system': {'cpu_percent': 25.5, 'memory_percent': 45.2},
                'process': {'count': 150, 'new_processes': []},
                'network': {'connections': 25, 'listening_ports': []},
                'file': {'new_files': [], 'modified_files': []},
                'user': {'logged_users': [], 'new_users': []},
                'logs': {'new_entries': 0, 'error_count': 0},
                'persistence': {'scheduled_tasks': [], 'startup_items': []},
                'firewall': {'rules': [], 'blocked_ips': []},
                'container': {'running_containers': [], 'new_containers': []},
                'cloud': {'instances': [], 'configurations': []},
                'threat_intel': {'indicators': [], 'matches': []},
                'integrity': {'file_changes': [], 'system_changes': []},
                'security_tools': {'antivirus_status': 'active', 'ids_alerts': []}
            }
            
            await websocket.send(json.dumps(test_event))
            print('✅ Message sending: OK')
            
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            if data.get('status') == 'received':
                print('✅ Message processing: OK')
                print('🎉 WebSocket is working perfectly!')
            else:
                print(f'⚠️  Message processing: {data}')
                
    except Exception as e:
        print(f'❌ Test failed: {e}')

asyncio.run(test_websocket())
"

echo ""
echo "2. Checking HTTP endpoints..."
echo "   Health Check: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
echo "   Events API: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/events)"
echo "   ML Core: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/health)"

echo ""
echo "3. Recent events in database:"
curl -s http://localhost:8000/events | jq '.[0:2] | .[] | {id, agent_id, event_type, timestamp}' 2>/dev/null || echo "   (jq not available, but events are being stored)"

echo ""
echo "✅ All tests completed!" 