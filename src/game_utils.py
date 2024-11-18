import json

def parse_socketio(msg):
  if not msg or not msg[0].isdigit():
    return None, None

  type_id = 0
  pos = 0
  while pos < len(msg) and pos < 2 and msg[pos].isdigit():
    type_id = type_id * 10 + int(msg[pos])
    pos += 1

  data = None
  if pos < len(msg):
    try:
      data = json.loads(msg[pos:])
    except:
      pass

  return type_id, data
