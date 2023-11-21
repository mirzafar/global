import ujson
from sanic import Request, Websocket

from utils.strs import StrUtils

rooms = dict()


async def chat_messages(request: Request, ws: Websocket):
    while True:
        data = ujson.loads(await ws.recv())
        chat_id = StrUtils.to_str(data.get('chat_id'))
        if not chat_id:
            continue

        action = StrUtils.to_str(data.pop('action', None))
        users = rooms[chat_id] if chat_id in rooms else []
        if action == 'open':
            if ws not in users:
                users.append(ws)

            rooms[chat_id] = users

        elif action in ['close', 'error']:
            if ws in users:
                users.remove(ws)

            if users:
                rooms[chat_id] = users
            else:
                rooms.pop(chat_id, None)

        elif action == 'message':
            data['is_me'] = False

            for user in users:
                if not user == ws:
                    await user.send(ujson.dumps(data))
