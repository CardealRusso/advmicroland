[adventure.land](https://adventure.land/) running on [micropython](https://github.com/micropython/micropython) with asyncio

Toy project

Currently has:
- auth
- entities (players and monsters)
- move
- attack
- use_hp_or_mp
- get_entity
- get_nearest_monster
- get_targeted_monster
- distance
- is_moving

```py
from src.game_client import *

run_bot("usd1", "USERCODE", "CHARACTERCODE", "AUTHCODE")

while running():
  cardeal = get_entity("Cardeal")
  if cardeal:
    move(cardeal)
```

https://github.com/user-attachments/assets/74cd17b5-a643-49f7-8da0-0e2477623d2d

```py
from src.game_client import *

run_bot("usd1", "USERCODE", "CHARACTERCODE", "AUTHCODE")

while running():
  use_hp_or_mp()

  leader = get_entity("Cardeal")
  target = get_targeted_monster() or get_nearest_monster()

  if leader and leader.id != character.id and (distance(character, leader) > 200 or (is_moving(leader) and not is_in_range(leader))):
    move(leader)
  else:
    if target and distance(character, target) < 200:
      if is_in_range(target):
        attack(target)
      else:
        move(target)

```

https://github.com/user-attachments/assets/2b123a82-7ec6-4e75-bd43-2d8037059218
