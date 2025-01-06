from app import app
from flask import Flask, render_template, request # type: ignore 
import mysql.connector # type: ignore

# Configurações da conexão
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

#Etapas de login
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        print(f"Email: {email}")
        print(f"Senha: {senha}")

        # Conexão com o banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        try:
            # Consulta no banco
            sql = "SELECT * FROM clientes WHERE email = %s AND senha = %s"
            valores = (email, senha)
            cursor.execute(sql, valores)
            usuario = cursor.fetchone()

            if usuario:
                # Usuário encontrado
                return render_template('page_clientes.html', usuario=usuario)
            else:
                # Usuário ou senha inválidos
                return render_template('login.html', mensagem_erro="Usuário ou senha inválidos!")
        except Exception as e:
            return f"Erro ao acessar banco de dados: {e}"
        finally:
            cursor.close()
            connection.close()
    else:
        # Para requisições GET, renderiza a página de login
        return render_template('login.html')


#Etapas de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastrar',  methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    tipo_user = request.form['tipo_user']

    if tipo_user == 'barbeiro':
        localidade = request.form['localidade']
        telefone = request.form['telefone']
        senha = request.form['senha']
        confirma_senha = request.form['confirma_senha']

        if senha != confirma_senha:
            return "As senhas não coincidem!"

        # Conexão com o banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        try:
            # Inserção no banco
            sql = "INSERT INTO barbeiro (nome, email, tipo_user, localidade, telefone, senha ) VALUES (%s, %s, %s, %s, %s, %s)"
            valores = (nome, email, tipo_user, localidade, telefone, senha)
            cursor.execute(sql, valores)
            connection.commit()
            print("Usuário cadastrado com sucesso!")
            return "Usuário cadastrado com sucesso!"
           
        except Exception as e:
            connection.rollback()
            return f"Erro: {e}"
        finally:
            cursor.close()
            connection.close()

    if tipo_user == 'cliente':
        telefone = request.form['telefone']
        senha = request.form['senha']
        confirma_senha = request.form['confirma_senha']

        if senha != confirma_senha:
            return "As senhas não coincidem!" 

        # Conexão com o banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        try:
            # Inserção no banco
            sql = "INSERT INTO clientes (nome, email, tipo_user, telefone, senha) VALUES (%s, %s, %s, %s, %s)"
            valores = (nome, email, tipo_user, telefone, senha)
            cursor.execute(sql, valores)
            connection.commit()
            return "Usuário cadastrado com sucesso!"
        except Exception as e:
            connection.rollback()
            return f"Erro: {e}"
        finally:
            cursor.close()
            connection.close()
    else:
        return "Tipo de usuário inválido!"
