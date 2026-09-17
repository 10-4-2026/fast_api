import asyncio
import json
import websockets

async def simulate_edge_device():
    uri = "ws://127.0.0.1:8000/ws/v1/vehicle/car_unit_01"
    
    async with websockets.connect(uri, origin="http://127.0.0.1:8000") as websocket:
        # Test 1: Gửi telemetry bình thường
        print("--- Gửi Telemetry bình thường (Speed = 60) ---")
        await websocket.send(json.dumps({"speed": 60, "engine_temp": 85}))
        res = await websocket.recv()
        print(f"Server response: {res}\n")

        # Test 2: Gửi telemetry quá tốc độ -> Nhận Cảnh báo
        print("--- Gửi Telemetry vượt tốc độ (Speed = 120) ---")
        await websocket.send(json.dumps({"speed": 120, "engine_temp": 95}))
        res = await websocket.recv()
        print(f"Server response: {res}\n")

        # Test 3: Gửi Binary Frame (Ảnh/Video Stream)
        print("--- Gửi Frame hình ảnh (Bytes) ---")
        fake_frame_bytes = b"\xFF\xD8\xFF\xE0" + b"\x00" * 512
        await websocket.send(fake_frame_bytes)
        res = await websocket.recv()
        print(f"Server response: {res}\n")

if __name__ == "__main__":
    asyncio.run(simulate_edge_device())