import _thread
import time
import json
import uwebsockets.client

class Entity:
  def __init__(self, data):
    self.update(data)
  
  def update(self, data):
    for key, value in data.items():
      setattr(self, key, value)
  
  def __getitem__(self, key):
    return getattr(self, key)

class _GameClient:
  def __init__(self, server, user, character, auth, width=1440, height=900, scale="2"):
    self.server = server
    self.user = user
    self.character = character
    self.auth = auth
    self.width = width
    self.height = height
    self.scale = scale
    
    self.websocket = uwebsockets.client.connect(
      f'wss://{server}.adventure.land:2053/socket.io/?EIO=4&transport=websocket'
    )
    print("Connected")
    print("Sending hello to server..")
    self.websocket.send("40")
    
    self.entities = {}
    self.player = None
    self.sent_auth = False
    self.sent_loaded = False
    self._running = True
    
    _thread.start_new_thread(self.main_loop, ())
    print("Waiting for player data...")
    while not self.player:
      time.sleep(0.1)

  def main_loop(self):
    while self._running:
      resp = self.websocket.recv()
      if resp:
        if resp == "2":
          self.websocket.send("3")
        if resp.startswith("42["):
          data = json.loads(resp[2:-1])
          if data[0] == "welcome" and not self.sent_loaded:
            self._send_screen_info()
          elif not self.sent_auth:
            self._send_auth()
          elif data[0] == "entities" and self.sent_auth:
            self._update_entities(data[1])
            if self.player is None:
              self.websocket.send('42["use",{"item":"hp"}]')
          elif data[0] == "player" and self.sent_auth:
            if not self.player:
              self.player = Entity(data[1])
            else:
              self.player.update(data[1])

  def _send_screen_info(self):
    print("Sending screen info...")
    screen_info = {
      "success": 1,
      "width": self.width,
      "height": self.height,
      "scale": self.scale
    }
    self.websocket.send(f'42["loaded",{json.dumps(screen_info)}]')
    self.sent_loaded = True

  def _send_auth(self):
    print("Sending auth...")
    auth_data = {
      "user": self.user,
      "character": self.character,
      "code_slot": self.character,
      "auth": self.auth,
      "width": self.width,
      "height": self.height,
      "scale": self.scale
    }
    self.websocket.send(f'42["auth", {json.dumps(auth_data)}]')
    self.sent_auth = True

  def _update_entities(self, data):
    for entity_list in [data.get("players", []), data.get("monsters", [])]:
      for entity in entity_list:
        self.entities[entity["id"]] = Entity(entity)

_client = None

def initbot(server, user, character, auth, **kwargs):
  global _client
  _client = _GameClient(server, user, character, auth, **kwargs)

def get_entity(entity_id):
  return _client.entities.get(entity_id)

def move(*args):
  if len(args) == 2:
    x, y = args
  else:
    x, y = args[0].x, args[0].y

  move_message = f'42["move",{{"x":{_client.player.x},"y":{_client.player.y},"going_x":{x},"going_y":{y},"m":0}}]'
  _client.websocket.send(move_message)

def running():
  time.sleep(0.5)
  return _client._running
