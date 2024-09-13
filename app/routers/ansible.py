from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Response, status, HTTPException, Depends, Request, APIRouter, Query, File, UploadFile
from random import choice, randrange
import asyncio
import time, json
from sqlalchemy import func
# from ..database import conn, cursor, get_db
from ..database import get_db
from sqlalchemy.orm import Session
import psycopg2
from .. import models
from concurrent.futures import ThreadPoolExecutor
import paramiko
import os
router = APIRouter(
    prefix="/api/v1/ansible",
    tags=['ansible']
)


def connect_and_execute_certificate(hostname, credentials, command, id_rsa_key):
    private_key_path = id_rsa_key
    client = paramiko.SSHClient()
    # Автоматическое добавление удаленного ключа в known_hosts
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
            # Создание объекта ключа и передача контрольной фразы
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password=passphrase)
        
        # Подключение с использованием ключа
        client.connect(
            hostname, port=credentials['port'], 
            username=credentials['username'], 
            pkey=private_key
        )
        
        print("Подключено успешно!")

        # Выполнение команды
        stdin, stdout, stderr = client.exec_command(command)
        
        # Чтение стандартного вывода и ошибок
        output = stdout.read().decode().strip()
        error_output = stderr.read().decode().strip()
        # Возвращаем как результат стандартный вывод и ошибки
        return {
            'hostname': hostname,
            'status': 'success',
            'output': output,
            'errors': error_output if error_output else None
        }

    except Exception as e:
        # В случае ошибки возвращаем информацию о ней
        return {
            'hostname': hostname,
            'status': 'error',
            'error': str(e)
        }

    finally:
        client.close()



# Функция для подключения и выполнения команды на сервере
def connect_and_execute_paaswd(hostname, credentials, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Автоматически добавлять ключи хоста
    
    try:
        # Подключение к серверу
        client.connect(
            hostname=hostname,
            port=credentials['port'],
            username=credentials['username'],
            password=credentials['password']
        )
        
        # Выполнение команды
        stdin, stdout, stderr = client.exec_command(command)
        
        # Чтение стандартного вывода и ошибок
        output = stdout.read().decode().strip()
        error_output = stderr.read().decode().strip()

        # Возвращаем как результат стандартный вывод и ошибки
        return {
            'hostname': hostname,
            'status': 'success',
            'output': output,
            'errors': error_output if error_output else None
        }

    except Exception as e:
        # В случае ошибки возвращаем информацию о ней
        return {
            'hostname': hostname,
            'status': 'error',
            'error': str(e)
        }

    finally:
        client.close()

# Функция для отправки файла на сервер через SFTP в стандартный путь (/tmp)
def upload_file_to_server(hostname, credentials, local_file_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Подключение к серверу
        client.connect(
            hostname=hostname,
            port=credentials['port'],
            username=credentials['username'],
            password=credentials['password']
        )
        
        # Инициализация SFTP-клиента
        sftp = client.open_sftp()
        print("Подключение успешно")
        # Стандартный путь для загрузки файлов — /tmp
        # remote_file_path = f"/tmp/{os.path.basename(local_file_path)}"
        remote_file_path = f"/{os.path.basename(local_file_path)}"
        # Отправка файла
        sftp.put(local_file_path, remote_file_path)
        
        # Закрываем SFTP-соединение
        sftp.close()

        return {
            'hostname': hostname,
            'status': 'success',
            'message': f"File {local_file_path} successfully uploaded to {remote_file_path}"
        }

    except Exception as e:
        return {
            'hostname': hostname,
            'status': 'error',
            'error': str(e)
        }

    finally:
        client.close()

# Маршрут FastAPI для выполнения команды через SSH на нескольких серверах
@router.get("/execPasswd")
async def execute(
    hosts: str = Query(..., description="Список хостов через запятую, без пробела"), 
    ports: int = 22, 
    passwords: str = Query(...), 
    command: str = 'ls -la'
):
    # Преобразуем строку хостов в список
    host_list = hosts.split(',')

    # Создаем словарь для параметров подключения
    credentials = {
        'port': ports,
        'username': 'root',  # Убедитесь, что username правильный
        'password': passwords
    }
    
    # Инициализируем список для результатов
    results = []
    
    # Проходим по каждому хосту и выполняем команду
    for host in host_list:
        result = connect_and_execute_paaswd(host, credentials, command)
        results.append(result)
    
    # Возвращаем результаты выполнения команд на всех серверах
    return {"results": results}

# Маршрут FastAPI для выполнения команды через SSH на нескольких серверах
@router.get("/execwithCert")
async def execute(
    hosts: str = Query(..., description="Список хостов через запятую, без пробела"), 
    ports: int = 22, 
    passphrase: str = Query(...),
    pkkey: UploadFile = File(...),
    command: str = 'ls -la'
):
    # Преобразуем строку хостов в список
    host_list = hosts.split(',')

    # Создаем словарь для параметров подключения
    credentials = {
        'port': ports,
        'username': 'root',  # Убедитесь, что username правильный
        'password': passwords
    }
    
    # Инициализируем список для результатов
    results = []
    
    # Проходим по каждому хосту и выполняем команду
    for host in host_list:
        result = connect_and_execute_paaswd(host, credentials, command, pkkey, passphrase)
        results.append(result)
    
    # Возвращаем результаты выполнения команд на всех серверах
    return {"results": results}


# Маршрут для загрузки файла и отправки его на сервер
@router.post("/uploadfile")
async def upload_file_to_linux(
    hosts: str = Query(..., description="Список хостов через запятую"),
    ports: int = 22,
    passwords: str = Query(...),
    file: UploadFile = File(...)
):
    # Преобразуем строку хостов в список
    host_list = hosts.split(',')

    # Сохраняем файл временно на сервере
    local_file_path = f"./{file.filename}"
    with open(local_file_path, "wb") as f:
        f.write(await file.read())
    
    # Создаем словарь для параметров подключения
    credentials = {
        'port': ports,
        'username': 'root',  # Убедитесь, что username правильный
        'password': passwords
    }
    
    # Инициализируем список для результатов
    results = []
    
    # Отправляем файл на каждый хост в стандартный путь (/tmp)
    for host in host_list:
        result = upload_file_to_server(host, credentials, local_file_path)
        results.append(result)

    # Удаляем файл после отправки (если не нужен)
    os.remove(local_file_path)
    
    # Возвращаем результаты отправки файла на все сервера
    return {"results": results}