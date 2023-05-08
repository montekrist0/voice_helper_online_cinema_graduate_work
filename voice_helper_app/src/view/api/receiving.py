from fastapi import (APIRouter,
                     Depends)

from services.handlers import (CommandHandler,
                               get_command_handler)
from view.models.message import Message

router = APIRouter()


@router.post('/', summary='Сообщение от помощника')
async def receiving_message(data: Message,
                            command_handler: CommandHandler = Depends(get_command_handler)):
    print(data)
