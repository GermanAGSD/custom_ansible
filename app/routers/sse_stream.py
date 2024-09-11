from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Response, status, HTTPException, Depends, Request, APIRouter
from random import choice, randrange
import asyncio
import time, json
from sqlalchemy import func
# from ..database import conn, cursor, get_db
from ..database import get_db
from sqlalchemy.orm import Session
import psycopg2
from .. import models 

# Это я просто для своего знания делаю, для того чтобы тоже пройти, это
# Для теста мини сервис
# Николай со мной согласиться нужно понимать все с двух сторон, не только с клиента
# Поэтому как и Николай тоже так делает или делал, все с двух сторон, чтобы полностью 
# понимать

router = APIRouter(
    prefix="/api/v1/stream",
    tags=['stream']
)


MESSAGE_STREAM_DELAY = 10  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 9000  # milisecond


# Глобальная переменная массив вне функции
hostarray = []
duplicates = []
# функция для нахождения одинаковых парраметров и обрыв одного из клиентов
# Например так делают в сервере iiko или rkeeper если у тебя одна лицензия то ты и тд и тп

def find_duplicates():
    # set хранит уникальные значения
    seen = set()
    for n in hostarray:
        if n in seen:
            print("Duplicates: " + n)
            duplicates.append(n)
        else:
            seen.add(n)

def funchostarrays(value: str):
    # hostarray = []    
    hostarray.append(value)
    print(hostarray)
    return hostarray

@router.get("/testduplicates")
async def testduplicates():
    # funchostarrays(value)
    return duplicates

@router.get("/testarray")
async def arraytest(value: str = None):
    if value:
        funchostarrays(value)
    return hostarray


# @app.get("/products")
# async def test_sqlachemy(db: Session = Depends(get_db)):
#     products = db.query(models.Product).all()
#     return products
# @router.get("/test_func")

def regist_queue(db: Session = Depends(get_db)):
    devices = db.query(models.Device).filter(models.Device.parrametr)
    # query = """ SELECT parrametr FROM devices """
    # # with conn.cursor() as cursor:
    # try:
    #     cursor.execute(query)
    #     parrametr = cursor.fetchall()
    #     parrametr_values = [item['parrametr'] for item in parrametr]
    # except psycopg2.errors.UniqueViolation:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate key value violates unique constraint")
    # except psycopg2.errors.InFailedSqlTransaction:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Duplicate key value violates unique constraint")
    #     # finally:
    return devices

@router.get("/stream")
async def stream(event: EventSourceResponse, request: Request, host: str):
    
    funchostarrays(host)
    async def event_generator():
        # event.listen_for_disconnect        
        while True:
            # if  request.co:
            #     client_ip = request.client
            #     print(f"Client {client_ip} disconnected from the stream")
            #     break
            
            if event_generator():

                yield {
                    # "event": random_string(),
                    "event": "setvol",
                    "id": randrange(1,100),
                    # "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": randrange(1,100),
                }
            await asyncio.sleep(MESSAGE_STREAM_DELAY)
    
    valid_host = regist_queue()
    find_duplicates()
    if host not in valid_host:
        raise HTTPException(status_code=400, detail="Устройство не зарегистрированно")
    # print(hostarray)

    return EventSourceResponse(event_generator())
