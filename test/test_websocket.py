#!/usr/bin/env python3
"""
WebSocket Test Script for NeuroSentinel
Tests the WebSocket connection to the server
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket():
    """Test WebSocket connection to NeuroSentinel server"""
    
    uri = "ws://localhost:8000/ws/events"
    
    print("🔌 Testing WebSocket Connection")
    print("=" * 50)
    print(f"📍 Connecting to: {uri}")
    print(f"⏰ Time: {datetime.now()}")
    print()
    
    try:
        # Connect to WebSocket
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            print("📡 Waiting for messages...")
            print()
            
            # Send a test message
            test_message = {
                "type": "test",
                "message": "WebSocket test from client",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"📤 Sending test message: {json.dumps(test_message, indent=2)}")
            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent successfully!")
            print()
            
            # Wait for messages for 10 seconds
            timeout = 10
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"📥 Received message: {message}")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(message)
                        print(f"📋 Parsed JSON: {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"⚠️  Message is not valid JSON: {message}")
                    
                    print()
                    
                except asyncio.TimeoutError:
                    # No message received within 1 second
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("❌ WebSocket connection closed by server")
                    break
            
            print("⏰ Test completed (10 seconds timeout)")
            
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid WebSocket URI")
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_http_endpoints():
    """Test HTTP endpoints to verify server is running"""
    
    import requests
    
    print("🌐 Testing HTTP Endpoints")
    print("=" * 30)
    
    endpoints = [
        ("http://localhost:8000/health", "Health Check"),
        ("http://localhost:8000/events", "Events Endpoint"),
        ("http://localhost:9000/health", "ML Core Health"),
        ("http://localhost:9000/models", "ML Models")
    ]
    
    for url, description in endpoints:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {description}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📊 Items: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"   📊 Keys: {list(data.keys())}")
                except:
                    print(f"   📊 Response: {response.text[:100]}...")
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: {e}")
        print()

if __name__ == "__main__":
    print("🧠 NeuroSentinel WebSocket Test")
    print("=" * 40)
    print()
    
    # Test HTTP endpoints first
    test_http_endpoints()
    
    # Test WebSocket
    asyncio.run(test_websocket()) 