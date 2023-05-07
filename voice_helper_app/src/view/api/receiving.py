from fastapi import APIRouter

from view.models.message import Message


router = APIRouter()


@router.post('/', summary='Сообщение от помощника')
async def receiving_message(data: Message):
    print(data)