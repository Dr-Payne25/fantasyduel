#!/usr/bin/env python3
import asyncio
import json

import websockets


async def test_frontend_behavior():
    """Test WebSocket behavior similar to the frontend"""
    draft_id = "test-draft-1"
    uri = f"ws://localhost:8000/ws/{draft_id}"

    print(f"[WS] Attempting to connect to draft: {draft_id}")
    print(f"[WS] Connecting to: {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[WS] Connected successfully to draft: {draft_id}")
            print("[WS] WebSocket readyState: OPEN")

            # Send initial ping message
            message = json.dumps({"type": "ping", "draftId": draft_id})
            print("[WS] Sending initial ping message")
            print(f"[WS] Sending message: {message}")
            await websocket.send(message)

            # Keep receiving messages
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"[WS] Message received: {response}")
                except asyncio.TimeoutError:
                    print("[WS] No message received in 5 seconds")
                    break

    except websockets.exceptions.ConnectionClosed as e:
        print(f"[WS] Disconnected - Code: {e.code}, Reason: {e.reason}")
        print(f"[WS] Was clean close: {e.code == 1000}")
    except Exception as e:
        print(f"[WS] WebSocket error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_frontend_behavior())
