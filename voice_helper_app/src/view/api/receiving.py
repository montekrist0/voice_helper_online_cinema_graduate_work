import orjson

from fastapi import APIRouter, WebSocket, Depends

from services.cmd_handler import CommandHandler, get_command_handler
from services.movies_storage_handler import ElasticSeeker, get_response_maker

router = APIRouter()


# TODO:
#  - удалить ненужные пустые файлы и директории


@router.websocket('/')
async def websocket_endpoint(
    websocket: WebSocket,
    command_handler: CommandHandler = Depends(get_command_handler),
    response_maker: ElasticSeeker = Depends(get_response_maker),
):
    await websocket.accept()
    while True:
        user_txt = orjson.loads(await websocket.receive_text())
        user_query_object = await command_handler.handle_user_query(user_txt)
        if not user_query_object:
            await websocket.close()
        user_query_object.answer = await response_maker.execute_user_command(
            command=user_query_object.final_cmd, keyword=user_query_object.key_word
        )

        await websocket.send_text(user_query_object.answer)
