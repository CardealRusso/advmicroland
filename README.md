[adventure.land](https://adventure.land/) running on [micropython](https://github.com/micropython/micropython) with _thread

Toy project

```py
from src.game_client import GameClient

client = GameClient(
  uri="wss://usd1.adventure.land:2053/socket.io/?EIO=4&transport=websocket",
  user="USERCODE",
  character="CHARACTERCODE",
  auth="AUTHCODE"
)

while client.running():
  cardeal = client.entities["players"].get("Cardeal")
  if cardeal and client.player:
    client.move(x=cardeal["x"], y=cardeal["y"])
```
