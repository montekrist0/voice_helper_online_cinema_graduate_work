from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# TODO нужно через base directory доставать
templates = Jinja2Templates(directory="/app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
