from elasticsearch import AsyncElasticsearch
import uvicorn
from fastapi import FastAPI

from core.configs import settings
from db.clients import mongo, redis
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
    mongo.client = mongo.create_mongo_client()
    redis.redis_message = redis.create_redis_message()
    elastic.es = AsyncElasticsearch(hosts=[f'{settings.elastic_host}:{settings.elastic_port}'])


@app.on_event('shutdown')
def shutdown():
    mongo.client.close()
    redis.redis_message.close()


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=True)
