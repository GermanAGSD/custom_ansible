import paramiko

# Параметры подключения
hostname = '10.99.12.1'
port = 22
username = 'badm'
private_key_path = 'badm_key'

# Создание клиента SSH
client = paramiko.SSHClient()

# Автоматическое добавление удаленного ключа в known_hosts
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Подключение к серверу
try:
    client.connect(hostname, port=port, username=username, key_filename=private_key_path)
    print("Подключено успешно!")

    # Выполнение команды
    stdin, stdout, stderr = client.exec_command('ls -la')
    print(stdout.read().decode())

finally:
    # Закрытие подключения
    client.close()
