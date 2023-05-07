import uvicorn
from fastapi import FastAPI

from view.api import render, receiving

app = FastAPI(
    title='API голосового помощника',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    description='...',
    version='1.0.0',
)

app.include_router(render.router, tags=['Render template'])
app.include_router(receiving.router, prefix='/api/v1/message', tags=['Message'])


@app.on_event('startup')
async def startup():
    pass


@app.on_event('shutdown')
def shutdown():
    pass


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=True)
