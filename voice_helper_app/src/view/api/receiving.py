import orjson

from fastapi import (APIRouter, WebSocket,
                     Depends)

from services.handlers import (CommandHandler,
                               get_command_handler)
from view.models.message import Message

router = APIRouter()


# @router.post('/', summary='Сообщение от помощника')
# async def receiving_message(data: Message,
#                             command_handler: CommandHandler = Depends(get_command_handler)):
#
#     await command_handler.handle(data.dict()['text'])


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket,
                             command_handler: CommandHandler = Depends(get_command_handler)):
    await websocket.accept()
    while True:
        user_txt = await websocket.receive_text()
        user_txt = orjson.loads(user_txt)
        result = await command_handler.handle(user_txt)
        await websocket.send_text(f"{result}")
