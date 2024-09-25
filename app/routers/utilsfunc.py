from passlib.context import CryptContext
import paramiko
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



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
