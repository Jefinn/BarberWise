import mysql.connector # type: ignore

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'barberwise'
}

# Conectando ao banco
try:
    connection = mysql.connector.connect(**config)
    print("Conexão bem-sucedida!")
except mysql.connector.Error as err:
    print(f"Erro: {err}")
finally:
    if connection.is_connected():
        connection.close()