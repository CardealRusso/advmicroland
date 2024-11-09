[adventure.land](https://adventure.land/) running on [micropython](https://github.com/micropython/micropython) with _thread

Toy project

```py
from src.game_client import *

initbot(
  server="usd1",
  user="USERCODE",
  character="CHARACTERCODE",
  auth="AUTHCODE"
)

while running():
  cardeal = get_entity("Cardeal")
  if cardeal:
    move(cardeal)
```

https://github.com/user-attachments/assets/74cd17b5-a643-49f7-8da0-0e2477623d2d

Currently has:
- auth
- entities (players and monsters)
- move
- get_entity
