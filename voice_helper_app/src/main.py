import uvicorn
from fastapi import FastAPI


from core.log_config import logger
from db.clients import mongo
from view.api import render, receiving
from db.clients import elastic

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
    logger.info('Старт приложения')
    mongo.client = mongo.create_mongo_client()
    await mongo.check_mongo()
    elastic.es = elastic.create_es_client()
    await elastic.check_es()


@app.on_event('shutdown')
def shutdown():
    mongo.client.close()
    logger.info('Завершение приложения')


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=True)
