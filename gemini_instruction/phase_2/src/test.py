import asyncio
import websockets

async def simulate_edge_device():
    uri = "ws://localhost:8000/ws/v1/vehicle/car_unit_01"
    async with websockets.connect(uri) as websocket:
        for i in range(10):
            # Giả lập gói tin khung hình nhị phân (binary data)
            fake_frame_bytes = b"\xFF\xD8\xFF\xE0" + b"\x00" * 1024 
            await websocket.send(fake_frame_bytes)
            
            response = await websocket.recv()
            print(f"Server response: {response}")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(simulate_edge_device())