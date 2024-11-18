import async_websocket_client, asyncio, game_utils, json

async def recv_msgs():
  while True:
    id, data = game_utils.parse_socketio(await ws.recv())
    if id == 0: await ws.send('40')
    if id == 2: await ws.send('3')
    if id == 42:
      if data[0] == 'welcome':
        screen_info = {"success": 1, "width": 1440, "height": 900, "scale": 1}
        await ws.send(f'42["loaded",{json.dumps(screen_info)}]')

    print(id, data)

async def main():
  global ws
  ws = async_websocket_client.AsyncWebsocketClient()
  await ws.handshake("wss://usd1.adventure.land:2053/socket.io/?EIO=4&transport=websocket")
  asyncio.create_task(recv_msgs())
  while True:
    await asyncio.sleep(100)

asyncio.run(main())
