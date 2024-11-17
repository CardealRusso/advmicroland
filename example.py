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
