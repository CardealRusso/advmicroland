import asyncio
import json
import .uwebsockets.uwebsockets
import time

class Entity:
  def __init__(self, data, entity_type):
    self.entity_type = entity_type
    self.update(data)
  
  def update(self, data):
    for key, value in data.items():
      setattr(self, key, value)
  
  def __getitem__(self, key):
    return getattr(self, key)

class Character:
  def __init__(self):
    self._client = None
  
  def init(self, client):
    self._client = client
  
  def __getattr__(self, name):
    return getattr(self._client.character, name)

class _GameClient:
  def __init__(self, server, user, charcode, auth, width=1440, height=900, scale="2"):
    self.server = server
    self.user = user
    self.charcode = charcode
    self.auth = auth
    self.width = width
    self.height = height
    self.scale = scale
    self.entities = {}
    self.character = None
    self.sent_auth = False
    self.sent_loaded = False
    self._running = True
    self._last_player_update = 0
    self.websocket = None
    self.character_event = asyncio.Event()

  def _create_task(self, coro):
    """Helper method to create and run a task in the event loop"""
    loop = asyncio.get_event_loop()
    return loop.create_task(coro)

  async def connect(self):
    while not self.character:
      await self._send_auth()
      await self._send_screen_info()
      await asyncio.sleep(5)
    print("[aml] character loaded")

  async def update_player_data(self):
    if self._running:
      if time.time() - self._last_player_update > 2:
        self.websocket.send('42["property",{"afk":false}]')
        self.websocket.send('42["property",{"afk":true}]')
        self._last_player_update = time.time()

  async def main_loop(self):
    self.websocket = uwebsockets.client.connect(
      f'wss://{self.server}.adventure.land:2053/socket.io/?EIO=4&transport=websocket'
    )
    self.websocket.send("40")
    while self._running:
      asyncio.create_task(self.update_player_data())
      resp = self.websocket.recv()
      if resp:
        if resp == "2":
          self.websocket.send("3")
        if resp.startswith("42["):
          data = json.loads(resp[2:-1])
          if data[0] == "game_error" or data[0] == "game_log":
            print(f'[{data[0]}] {data[1]}')
          if data[0] == "welcome" and not self.sent_loaded:
            await self._send_screen_info()
          elif not self.sent_auth:
            await self._send_auth()
          elif data[0] == "entities" and self.sent_auth:
            self._update_entities(data[1])
          elif data[0] == "player" and self.sent_auth:
            self._last_player_update = time.time()
            if not self.character:
              self.character = Entity(data[1], "player")
              self.character_event.set()
            else:
              self.character.update(data[1])
          elif data[0] == "death" and self.sent_auth:
            entity_id = data[1].get("id")
            if entity_id and entity_id in self.entities:
              del self.entities[entity_id]
      await asyncio.sleep_ms(20)

  async def _send_screen_info(self):
    print("[aml] sending screen info")
    screen_info = {"success": 1, "width": self.width, "height": self.height, "scale": self.scale}
    self.websocket.send(f'42["loaded",{json.dumps(screen_info)}]')
    self.sent_loaded = True

  async def _send_auth(self):
    print("[aml] sending auth")
    auth_data = {
      "user": self.user, "character": self.charcode, "code_slot": self.charcode, "auth": self.auth,
      "width": self.width, "height": self.height, "scale": self.scale
    }
    self.websocket.send(f'42["auth", {json.dumps(auth_data)}]')
    self.sent_auth = True

  def _update_entities(self, data):
    for player in data.get("players", []):
      self.entities[player["id"]] = Entity(player, "player")
    
    for monster in data.get("monsters", []):
      self.entities[monster["id"]] = Entity(monster, "monster")

    entities_to_remove = []
    for entity_id, entity in self.entities.items():
      if hasattr(entity, 'hp') and entity.hp <= 0:
        entities_to_remove.append(entity_id)
        continue

      if self.character and distance(self.character, entity) > 400:
        entities_to_remove.append(entity_id)

    for entity_id in entities_to_remove:
      del self.entities[entity_id]

_client = None
character = Character()

async def initbot(server, user, charcode, auth, **kwargs):
    await _client.connect()

def run_bot(server, user, charcode, auth, **kwargs):
    global _client
    _client = _GameClient(server, user, charcode, auth, **kwargs)
    character.init(_client)
    asyncio.create_task(_client.main_loop())
    asyncio.run(initbot(server, user, charcode, auth, **kwargs))

def get_entity(entity_id):
  return _client.entities.get(entity_id)

def get_nearest_monster():
  monsters = [e for e in _client.entities.values() if e.entity_type == 'monster']
  if not monsters:
    return None
  return min(monsters, key=lambda m: distance(character, m))

def get_targeted_monster():
  if not hasattr(character, 'target'):
    return False
  monster = get_entity(character.target)
  if not monster or monster.entity_type != 'monster':
    return False
  if not hasattr(monster, 'hp') or monster.hp <= 0:
    return False
  return monster

def is_in_range(entity):
  return distance(character, entity) <= character.range

async def _attack_async(entity):
  _client.websocket.send(f'42["attack",{{"id":"{entity.id}"}}]')

async def _move_async(*args):
  x, y = (args[0].x, args[0].y) if len(args) == 1 else args
  move_message = f'42["move",{{"x":{character.x},"y":{character.y},"going_x":{x},"going_y":{y},"m":0}}]'
  _client.websocket.send(move_message)

async def _use_hp_or_mp_async():
  if character.hp <= 0.75 * character.max_hp:
    _client.websocket.send('42["use",{"item":"hp"}]')
  elif character.mp <= 0.75 * character.max_mp:
    _client.websocket.send('42["use",{"item":"mp"}]')

async def _running_async():
  await asyncio.sleep_ms(50)
  return _client._running

def attack(entity):
  return asyncio.run(_attack_async(entity))

def move(*args):
  return asyncio.run(_move_async(*args))

def use_hp_or_mp():
  return asyncio.run(_use_hp_or_mp_async())

def running():
  return asyncio.run(_running_async())

def distance(entity1, entity2):
  return int(((entity1.x - entity2.x) ** 2 + (entity1.y - entity2.y) ** 2) ** 0.5)

def is_moving(entity):
  return getattr(entity, 'moving', False)
