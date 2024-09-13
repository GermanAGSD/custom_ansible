import paramiko

# Параметры подключения (одинаковые для обоих серверов)
common_credentials = {
    'port': 22,
    'username': 'root',
    'password': 'cszc6791'
}

# Хосты (IP-адреса или имена хостов)
servers = ['172.30.30.19', '172.30.30.18']

# Функция для подключения и выполнения команды на сервере
def connect_and_execute(hostname, credentials, command):
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
        print(f"Подключено к {hostname}")

        # Выполнение команды
        stdin, stdout, stderr = client.exec_command(command)
        print(f"Результаты команды на {hostname}:")
        output = stdout.read().decode()
        print(stdout.read().decode())

    except Exception as e:
        print(f"Не удалось подключиться к {hostname}: {e}")

    finally:
        client.close()
    return 

# Команда для выполнения
command = 'ls -la'

# Подключение к каждому серверу
for server in servers:
    connect_and_execute(server, common_credentials, command)
