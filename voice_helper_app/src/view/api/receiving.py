import orjson

from fastapi import APIRouter, WebSocket, Depends

from services.handlers import CommandHandler, get_command_handler

router = APIRouter()


# TODO:
#  - попробовать запилить обращение по типу Алисы
#  - разобраться почему отваливается вебсокет
#  - убрать ненужные mount-volume (redis)
#  - удалить ненужные пустые файлы и директории

@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket, command_handler: CommandHandler = Depends(get_command_handler)):
    await websocket.accept()
    while True:
        user_txt = await websocket.receive_text()
        user_txt = orjson.loads(user_txt)
        result = await command_handler.handle_user_query(user_txt)
        await websocket.send_text(f'{result}')
