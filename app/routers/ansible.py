from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Response, status, HTTPException, Depends, Request, APIRouter, Query, File, UploadFile, Form
# from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import SessionLocal, engine, get_db, conn, cursor
import paramiko
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import text
from .. schemas import HostResponse, HostCreateSchema, HostFileSchema, CreateHostGroup, DeleteHostGroup
import os
from pydantic import BaseModel, Field
import io

router = APIRouter(
    prefix="/api/v1/ansible",
    tags=['ansible']
)


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
        result = await connect_and_execute_paaswd(host, credentials, command)
        results.append(result)
    
    # Возвращаем результаты выполнения команд на всех серверах
    return {"results": results}

# Маршрут FastAPI для выполнения команды через SSH на нескольких серверах
@router.get("/execwithCert")
async def execute(
    hosts: str = Query(..., description="Список хостов через запятую, без пробела"),
    username: str = Query(..., description=""),
    port: int = 22,
    command: str = 'ls -la'
):
    # Преобразуем строку хостов в список
    host_list = hosts.split(',')

    # # Создаем словарь для параметров подключения
    # credentials = {
    #     'port': ports,
    #     'username': 'root',  # Убедитесь, что username правильный
    #     # 'password': passwords
    # }
    
    # Инициализируем список для результатов
    results = []
    
    # Проходим по каждому хосту и выполняем команду
    for host in host_list:
        result = await connect_with_local_certificate(host, port, username, command)
        results.append(result)
    
    # Возвращаем результаты выполнения команд на всех серверах
    print(results)
    return {"results": results}

@router.post("/uploadfileWithCertificate")
async def upload_file_to_linux_with_certificate(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    ports: int = 22,
    username: str = Form(...),
    # passwd: str = Form(...),
    ipadress: str = Form(...),
    ):
    host_list = ipadress.split(',')
    # Извлекаем хосты и их данные из базы данных
    # hosts = db.query(models.Hosts.id, models.Hosts.ipadress, models.Hosts.port, models.Hosts.username, models.Hosts.password).all()
    # host_list = [host[1] for host in hosts]
    # ports = hosts[0][2]  # Извлекаем порт для первого хоста (если у всех хостов один порт)
    # username = hosts[0][3]  # Извлекаем имя пользователя для первого хоста
    # passwd = hosts[0][4]  # Извлекаем пароль

    # print(f"Порты: {ports}, Имя пользователя: {username}, Пароль: {passwd}, IP адреса: {ipadress_list}")

    # Сохраняем файл временно на сервере
    local_file_path = f"./{file.filename}"
    with open(local_file_path, "wb") as f:
        f.write(await file.read())

    # Создаем словарь для параметров подключения
    credentials = {
        'port': ports,
        'username': username,
        # 'password': passwd,
    }

    # Инициализируем список для результатов
    results = []

    # Последовательная отправка файла на каждый хост
    for host in host_list:
        print(f"Отправка файла на сервер {host}")
        
        # Важно использовать await для последовательного выполнения
        result = await upload_file_to_server_with_cert(host, credentials, local_file_path)
        
        # Добавляем результат в список
        results.append(result)
        print(f"Загрузка на {host} завершена с результатом: {result}")

    # Удаляем файл после завершения отправки
    os.remove(local_file_path)
    print(result)
    # Возвращаем результаты отправки файла на все сервера
    return {"results": results}

@router.post("/uploadfile")
async def upload_file_to_linux(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    ports: int = 22,
    username: str = None,
    passwd: str = Form(...),
    ipadress: str = Form(...),
    ):
    host_list = ipadress.split(',')
    # Извлекаем хосты и их данные из базы данных
    # hosts = db.query(models.Hosts.id, models.Hosts.ipadress, models.Hosts.port, models.Hosts.username, models.Hosts.password).all()
    # host_list = [host[1] for host in hosts]
    # ports = hosts[0][2]  # Извлекаем порт для первого хоста (если у всех хостов один порт)
    # username = hosts[0][3]  # Извлекаем имя пользователя для первого хоста
    # passwd = hosts[0][4]  # Извлекаем пароль

    # print(f"Порты: {ports}, Имя пользователя: {username}, Пароль: {passwd}, IP адреса: {ipadress_list}")

    # Сохраняем файл временно на сервере
    local_file_path = f"./{file.filename}"
    with open(local_file_path, "wb") as f:
        f.write(await file.read())

    # Создаем словарь для параметров подключения
    credentials = {
        'port': ports,
        'username': username,
        'password': passwd,
    }

    # Инициализируем список для результатов
    results = []

    # Последовательная отправка файла на каждый хост
    for host in host_list:
        print(f"Отправка файла на сервер {host}")
        
        # Важно использовать await для последовательного выполнения
        result = await upload_file_to_server(host, credentials, local_file_path)
        
        # Добавляем результат в список
        results.append(result)
        print(f"Загрузка на {host} завершена с результатом: {result}")

    # Удаляем файл после завершения отправки
    os.remove(local_file_path)

    # Возвращаем результаты отправки файла на все сервера
    return {"results": results}

@router.get("/hosts")
def get_hosts(db: Session = Depends(get_db)):
     # Выбираем только нужные поля из таблицы hosts
        # Выполняем запрос с соединением таблиц
    hosts = db.query(
        models.Hosts.ipadress,
        models.Hosts.port,
        models.Hosts.username,
        models.Hosts.password,
        models.Type.grouptype,
        models.Type.description
    ).outerjoin(models.Type, models.Hosts.grouptype_id == models.Type.id).all()

    # if hosts.grouptype == null:
        
    return hosts

@router.get("/host_group", response_model=List[schemas.HostType])
def get_type(db: Session = Depends(get_db)):
     # Выбираем только нужные поля из таблицы hosts
    type = db.query(models.Type.id, models.Type.grouptype, models.Type.description).all()
    return type

@router.get("/host_group_network")
def get_network_host(db: Session = Depends(get_db)):
    # Фильтрация записей по значению hosttype (например, "Network")
    cursor.execute("""
    SELECT hosts.*
    FROM hosts
    JOIN type ON hosts.grouptype_id = type.id
    WHERE type.grouptype = 'Network'
""")
    type = cursor.fetchall()
    return type

@router.get("/host_group_linux")
def get_linux_host(db: Session = Depends(get_db)):
    # Фильтрация записей по значению hosttype (например, "Network")
    cursor.execute("""
    SELECT hosts.*
    FROM hosts
    JOIN type ON hosts.grouptype_id = type.id
    WHERE type.grouptype = 'Linux Hosts'
""")
    type = cursor.fetchall()
    return type
    
@router.post("/create_host_group")
def create_host_group(host_group: CreateHostGroup, db: Session = Depends(get_db)):
    try:
        new_group = models.Type(
            grouptype=host_group.grouptype,
            description=host_group.description
        )

        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return {"message": "Group Type created successfully", "host": new_group}
    except Exception as e:
        db.rollback()  # Откат транзакции при ошибке
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")    

@router.delete('/delete_group_type')
def delete_group_type(del_group: DeleteHostGroup, db: Session = Depends(get_db)):
    try:
        
        group = db.query(models.Type).filter(models.Type.id == del_group.id).first()
    
        if not group:
            raise HTTPException(status_code=404, detail="Host not found")
           
        db.delete(group)
        db.commit()
        # db.refresh(group)
        return {"message": "Group deleted", "group": group}
    except Exception as e:
        db.rollback()  # Откат транзакции при ошибке
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")  
# Обработчик POST-запроса
@router.post("/hosts")
def create_host(host_data: HostCreateSchema, db: Session = Depends(get_db)):
    try:
        # Хеширование пароля перед сохранением
        # hashed_password = bcrypt.hash(host_data.password)

        # Создание нового объекта хоста
        new_host = models.Hosts(
            ipadress=host_data.ipadress,
            port=host_data.port,
            username=host_data.username,
            password=host_data.password,  # Храним хешированный пароль
            grouptype_id=host_data.grouptype_id
        )

        # Добавляем объект в базу данных и сохраняем изменения
        db.add(new_host)
        db.commit()
        db.refresh(new_host)  # Обновляем объект с новыми данными (например, ID)

        return {"message": "Host created successfully", "host": new_host}

    except Exception as e:
        db.rollback()  # Откат транзакции при ошибке
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")    




# Обработчик POST-запроса
# @router.get("/execWithcert")
async def connect_with_local_certificate(hostname, port, username, command):
    """
    Connects to the remote host using a certificate file in the same directory as the script.

    Args:
        hostname (str): The hostname or IP address of the remote server.
        port (int): The port number to connect to (e.g., 22 for SSH).
        username (str): The username for SSH login.
        certificate_file (str): The name of the private key file located in the same directory as the script.
        command (str): The command to execute on the remote server.
        passphrase (str, optional): The passphrase for the private key (if encrypted). Default is None.

    Returns:
        dict: A dictionary containing the command's output or an error message.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    certificate_file = 'badm_key'  # The private key file in the same directory
    passphrase=None
    try:
        # Get the full path of the certificate in the current directory
        cert_path = os.path.join(os.path.dirname(__file__), certificate_file)

        # Load the private key from the certificate file in the current directory
        private_key = paramiko.RSAKey.from_private_key_file(cert_path, password=passphrase)

        # Connect to the remote host
        client.connect(
            hostname, 
            port=port, 
            username=username, 
            pkey=private_key
        )

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        errors = stderr.read().decode().strip()

        return {
            'hostname': hostname,
            'status': 'success',
            'output': output,
            'errors': errors if errors else None
        }

    except Exception as e:
        return {
            'hostname': hostname,
            'status': 'error',
            'error': str(e)
        }

    finally:
        client.close()

# # Example usage
# hostname = '10.0.2.42'
# port = 22
# username = 'badm'
# # certificate_file = 'badm_key'  # The private key file in the same directory
# command = 'export'

# result = connect_with_local_certificate(hostname, port, username, command)
# print(result)


# Функция для подключения и выполнения команды на сервере
async def connect_and_execute_paaswd(hostname, credentials, command):
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
async def upload_file_to_server(hostname, credentials, local_file_path):
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

# Функция для отправки файла на сервер через SFTP в стандартный путь (/tmp)
async def upload_file_to_server_with_cert(hostname, credentials, local_file_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    certificate_file = 'badm_key'  # The private key file in the same directory
    passphrase=None
    try:

        # Get the full path of the certificate in the current directory
        cert_path = os.path.join(os.path.dirname(__file__), certificate_file)
        # Подключение с использованием сертификата
        private_key = paramiko.RSAKey.from_private_key_file(cert_path, password=passphrase)
        # Подключение к серверу
        client.connect(
            hostname=hostname,
            port=credentials['port'],
            username=credentials['username'],
            pkey=private_key,
            # password=credentials['password']
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
# Функция для подключения и загрузки файла на сервер по SFTP
# async def upload_file_to_server_with_cert(hostname, port, username, local_file_path):
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     certificate_file = 'badm_key'  # The private key file in the same directory
#     passphrase=None
#     remote_file_path = f"/{os.path.basename(local_file_path)}"
#     try:
#         # Get the full path of the certificate in the current directory
#         cert_path = os.path.join(os.path.dirname(__file__), certificate_file)
#         # Подключение с использованием сертификата
#         private_key = paramiko.RSAKey.from_private_key_file(cert_path, password=passphrase)
        
#         client.connect(
#             hostname, 
#             port=port, 
#             username=username, 
#             pkey=private_key
#         )

#         # Подключаем SFTP сессию
#         sftp = client.open_sftp()
        
#         # Отправка файла
#         sftp.put(local_file_path, remote_file_path)
#         sftp.close()

#         return {'hostname': hostname, 'status': 'success', 'message': f'File uploaded to {hostname}'}
#     except Exception as e:
#         return {'hostname': hostname, 'status': 'error', 'error': str(e)}
#     finally:
#         client.close()