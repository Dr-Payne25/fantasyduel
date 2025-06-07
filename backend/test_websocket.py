#!/usr/bin/env python3
import asyncio
import json

import websockets


async def test_websocket():
    uri = "ws://localhost:8000/ws/test-draft-id"
    print(f"Connecting to {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")

            # Send a ping message
            message = json.dumps({"type": "ping", "draftId": "test-draft-id"})
            print(f"Sending: {message}")
            await websocket.send(message)

            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received: {response}")

            # Keep connection open for a bit
            await asyncio.sleep(2)
            print("Closing connection...")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
