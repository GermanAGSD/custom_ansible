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


router = APIRouter(
    prefix="/api/v1/ws",
    tags=['ws']
)