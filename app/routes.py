from app import app
from flask import Flask, render_template, request, url_for, redirect, session, jsonify # type: ignore 
from functools import wraps
import mysql.connector # type: ignore
from datetime import datetime, timedelta
import json

# Configurações da conexão
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'barberwise'
}

# Test de conecta ao banco
try:
    connection = mysql.connector.connect(**config)
    print("Conexão bem-sucedida!")
except mysql.connector.Error as err:
    print(f"Erro: {err}")
finally:
    if connection.is_connected():
        connection.close()

#Requisição de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#Rota de login
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
        cursor = connection.cursor(dictionary=True)

        try:
            # Consulta na tabela de clientes
            sql_cliente = "SELECT * FROM clientes WHERE email = %s AND senha = %s"
            valores = (email, senha)
            cursor.execute(sql_cliente, valores)
            usuarioCliente = cursor.fetchone()

            if usuarioCliente:
                session['user_logged_in'] = True
                return redirect(url_for('painelCliente'))

            # Consulta na tabela de barbeiros
            sql_barbeiro = "SELECT * FROM barbeiro WHERE email = %s AND senha = %s"
            cursor.execute(sql_barbeiro, valores)
            usuarioBarbeiro = cursor.fetchone()

            if usuarioBarbeiro:
                 session['barbeiro_id'] = usuarioBarbeiro['id']  # 🔥 ID salvo ANTES do redirect
                 session['user_logged_in'] = True
                 return redirect(url_for('painelBarbeiro'))


            else:
                return jsonify({'status': 'error', 'message': 'Credenciais inválidas'}), 401
            
            #return redirect(url_for('painelBarbeiro'))
        
        except Exception as e:
            return f"Erro ao acessar banco de dados: {e}"
        finally:
            cursor.close()
            connection.close()

    # Para requisições GET, renderiza a página de login
    return render_template('login.html')


#Etapas de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


# Cadastro de usuário
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    tipo_user = request.form.get('tipo_user')
    
    if not tipo_user:
        return render_template('cadastro.html', mensagem_erro="O tipo de usuário não foi informado!")
    
    tipo_user = tipo_user.strip().lower()  # Normaliza o valor
    print(f"Tipo de usuário normalizado: '{tipo_user}'")  # Para depuração

    nome = request.form.get('nome')
    email = request.form.get('email')
    
    # Verifica se o tipo de usuário é 'barbeiro'
    if tipo_user == 'barbeiro':
        localidade = request.form.get('localidade')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')

        # Verifica se as senhas coincidem
        if senha != confirma_senha:
            print("As senhas não coincidem!")
            return render_template('cadastro.html', mensagem_erro="As senhas não coincidem!")

        # Conexão com o banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        try:
            sql = "SELECT * FROM barbeiro WHERE email = %s"
            cursor.execute(sql, (email,))
            barbeiro = cursor.fetchone()
            if barbeiro:
                return render_template('cadastro.html', mensagem_erro="Barbeiro já cadastrado!")
            else:
                print("Barbeiro não cadastrado!")
                
            # Inserção no banco (barbeiro)
            sql = "INSERT INTO barbeiro (nome, email, tipo_user, localidade, telefone, senha ) VALUES (%s, %s, %s, %s, %s, %s)"
            valores = (nome, email, tipo_user, localidade, telefone, senha)
            cursor.execute(sql, valores)
            connection.commit()
            
            print("Barbeiro cadastrado com sucesso!")
            return render_template('login.html', mensagem_sucesso="Usuário barbeiro cadastrado com sucesso!")
        
        except Exception as e:
            connection.rollback()
            return f"Erro: {e}"
        finally:
            cursor.close()
            connection.close()

    # Verifica se o tipo de usuário é 'cliente'
    elif tipo_user == 'cliente':
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')

        # Verifica se as senhas coincidem
        if senha != confirma_senha:
            print("As senhas não coincidem!")
            return render_template('cadastro.html', mensagem_erro="As senhas não coincidem!")

        # Conexão com o banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        try:
            sql = "SELECT * FROM clientes WHERE email = %s"
            cursor.execute(sql,(email,))
            cliente = cursor.fetchone()
            if cliente:
                return render_template('cadastro.html', mensagem_erro="Cliente já cadastrado!")
            else:
                print("Cliente não cadastrado!")
                
            # Inserção no banco (clientes)
            sql = "INSERT INTO clientes (nome, email, tipo_user, telefone, senha) VALUES (%s, %s, %s, %s, %s)"
            valores = (nome, email, tipo_user, telefone, senha)
            cursor.execute(sql, valores)
            connection.commit()
            
            print("Cliente cadastrado com sucesso!")
            return render_template('login.html', mensagem_sucesso="Usuário cliente cadastrado com sucesso!")
        
        except Exception as e:
            connection.rollback()
            return render_template('cadastro.html', mensagem_erro=f"Erro ao cadastrar usuário: {e}")
        
        finally:
            cursor.close()
            connection.close()

    # Caso o tipo de usuário não seja válido
    else:
        print(f"Tipo de usuário inválido: '{tipo_user}'")  # Para depuração
        return render_template('cadastro.html', mensagem_erro="Tipo de usuário inválido!")


#Painel do cliente
@app.route('/painelCliente')
@login_required
def painelCliente():
    return render_template('painelCliente.html')


#Rota de Barbearia selecionada
@app.route('/get_barbers', methods=['GET'])
def get_barbers():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nome AS name FROM barbeiro")
        barbers = cursor.fetchall()
        return jsonify(barbers)
    except Exception as e:
        print(f"Erro ao buscar barbearias: {e}")
        return jsonify([]), 500
    finally:
        cursor.close()
        connection.close()

#Rota de agendamento
@app.route('/confirm_agd', methods=['POST'])
def confirm_agd():
    try:
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Content-Type deve ser application/json'}), 415

        data = request.get_json()
        cliente_id = data.get('cliente_id')
        data_agendamento = data.get('data')
        horario_agd = data.get('horario_agd')
        barbeiro_id = data.get('barbeiro_id')  # Obtém o ID do barbeiro

        print(f"Recebido - cliente_id: {cliente_id}, data: {data_agendamento}, horario_agd: {horario_agd}, barbeiro_id: {barbeiro_id}")

        if not cliente_id or not data_agendamento or not horario_agd or not barbeiro_id:
            return jsonify({'status': 'error', 'message': 'Dados incompletos!'}), 400

        # Verificar se cliente_id é um número inteiro válido
        if not cliente_id.isdigit():
            return jsonify({'status': 'error', 'message': 'cliente_id inválido!'}), 400
        cliente_id = int(cliente_id)

        try:
            data_agendamento = datetime.strptime(data_agendamento, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Formato de data inválido! Use YYYY-MM-DD.'}), 400

        try:
            horario_agd = datetime.strptime(horario_agd, '%H:%M').strftime('%H:%M:%S')
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Formato de horario_agd inválido! Use HH:MM.'}), 400

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Verificar se o cliente existe
        cursor.execute("SELECT 1 FROM clientes WHERE id = %s", (cliente_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Cliente não encontrado!'}), 400

        # Verificar se o barbeiro existe
        cursor.execute("SELECT 1 FROM barbeiro WHERE id = %s", (barbeiro_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Barbeiro não encontrado!'}), 400

        # Verifica se o horário já está agendado para a data
        cursor.execute("SELECT 1 FROM agendamentos_barberwise WHERE data = %s AND horario_agd = %s", (data_agendamento, horario_agd))
        if cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Horário já está agendado!'}), 400

        # Inserir o novo agendamento, caso o horário esteja livre
        cursor.execute(
            "INSERT INTO agendamentos_barberwise (cliente_id, data, horario_agd, barbeiro_id) VALUES (%s, %s, %s, %s)",
            (cliente_id, data_agendamento, horario_agd, barbeiro_id)
        )
        connection.commit()

        return jsonify({'status': 'success', 'message': 'Agendamento confirmado!'})

    except mysql.connector.Error as err:
        print("Erro MySQL:", err)
        return jsonify({'status': 'error', 'message': f'Erro ao confirmar agendamento no MySQL: {err}'}), 500

    except Exception as e:
        print("Erro Geral:", e)
        return jsonify({'status': 'error', 'message': f'Erro inesperado: {e}'}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()



# Função para converter objetos datetime e timedelta para strings
def convert_to_serializable(obj):
    if isinstance(obj, (datetime, timedelta)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# Rota de busca de agendamentos
@app.route('/get_agendamentos', methods=['GET'])
def get_agendamentos():
    try:
        # Obtendo os parâmetros corretamente
        barbeiro_id = request.args.get('barbeiro_id', type=int)
        data = request.args.get('data')

        # Debugging: verificar informações recebidas
        print("Barbeiro ID:", barbeiro_id)
        print("Data:", data)
        
        # Debugging: verificar parâmetros recebidos
        print("Parâmetros recebidos:", request.args.to_dict())

        if not barbeiro_id or not data:
            return jsonify({'status': 'error', 'message': 'Barbeiro ID e Data são obrigatórios!'}), 400

        # Conectando ao banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT a.id, c.nome AS cliente_nome, c.telefone, c.email, a.horario_agd, a.status
        FROM agendamentos_barberwise a
        JOIN clientes c ON a.cliente_id = c.id
        WHERE a.barbeiro_id = %s AND a.data = %s
        ORDER BY a.horario_agd
        """
        cursor.execute(query, (barbeiro_id, data))
        agendamentos = cursor.fetchall()

        cursor.close()
        connection.close()

        # Convertendo objetos datetime e timedelta para strings
        agendamentos_serializable = json.loads(json.dumps(agendamentos, default=convert_to_serializable))

        return jsonify({'status': 'success', 'agendamentos': agendamentos_serializable})

    except mysql.connector.Error as err:
        print("Erro MySQL:", err)
        return jsonify({'status': 'error', 'message': f'Erro ao buscar agendamentos no MySQL: {err}'}), 500
    except Exception as e:
        print("Erro Geral:", e)
        return jsonify({'status': 'error', 'message': f'Erro inesperado: {e}'}), 500
    

@app.route('/get_barbeiro_id', methods=['GET'])
def get_barbeiro_id():
    if 'barbeiro_id' in session:
        return jsonify({'barbeiro_id': session['barbeiro_id']})
    else:
        return jsonify({'error': 'Barbeiro ID não encontrado na sessão'}), 404
    

#Rota de busca de cliente
@app.route('/get_cliente', methods=['GET'])
def get_cliente():
    try:
        cliente_id = request.args.get('cliente_id')  # Pega o ID do cliente da requisição
        
        if not cliente_id:
            return jsonify({'status': 'error', 'message': 'Cliente ID não fornecido!'}), 400

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        # Consulta SQL para buscar os dados do cliente pelo ID
        query = "SELECT nome, telefone, email FROM clientes WHERE id = %s"
        cursor.execute(query, (cliente_id,))
        cliente = cursor.fetchone()  # Obtém um único resultado

        if cliente:
            return jsonify({'status': 'success', 'data': cliente})
        else:
            return jsonify({'status': 'error', 'message': 'Cliente não encontrado!'}), 404

    except mysql.connector.Error as err:
        print("Erro MySQL:", err)
        return jsonify({'status': 'error', 'message': f'Erro ao buscar cliente no MySQL: {err}'}), 500

    except Exception as e:
        print("Erro Geral:", e)
        return jsonify({'status': 'error', 'message': f'Erro inesperado: {e}'}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

                 
#Painel do barbeiro
@app.route('/painelBarbeiro')
@login_required
def painelBarbeiro():
    return render_template('painelBarbeiro.html')