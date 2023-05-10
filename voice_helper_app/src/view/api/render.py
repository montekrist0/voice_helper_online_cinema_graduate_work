from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.configs import settings

templates = Jinja2Templates(directory=settings.base_dir + '/templates')

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse('index_ws.html', {'request': request})
