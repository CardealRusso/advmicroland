import asyncio
import uwebsockets

async def recv_msgs():
  while True:
    print(f'Received: {await ws.recv()}')

async def main():
  global ws
  ws = await uwebsockets.connect('wss://usd1.adventure.land:2053/socket.io/?EIO=4&transport=websocket')
  asyncio.create_task(recv_msgs())
  while True:
    #Keep one async thread open
    await asyncio.sleep(100)

asyncio.run(main())
