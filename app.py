from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'chave_secreta'

if __name__ == '__main__':
    app.run(debug=True)         

# Função para inicializar o banco de dados
def init_db():
    conn = sqlite3.connect('ponto.db')
    cursor = conn.cursor()

    # Criação da tabela 'usuarios' se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    # Criação da tabela 'registros' se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            entrada1 DATETIME,
            saida1 DATETIME,
            entrada2 DATETIME,
            saida2 DATETIME,
            data DATE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    conn.close()

# Inicialize o banco de dados ao iniciar a aplicação
init_db()

# Página de login
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome'].lower()
        senha = request.form['senha']

        conn = sqlite3.connect('ponto.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE nome = ?', (nome,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario and check_password_hash(usuario[2], senha):
            session['usuario_id'] = usuario[0]
            return redirect(url_for('registro_ponto'))
        else:
            flash('Usuário ou senha incorretos!')

    return render_template('login.html')

# Página de cadastro de usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome'].lower()
        senha = request.form['senha']

        hashed_password = generate_password_hash(senha, method='pbkdf2:sha256')

        conn = sqlite3.connect('ponto.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE nome = ?', (nome,))
        if cursor.fetchone():
            flash('Usuário já cadastrado!')
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO usuarios (nome, senha) VALUES (?, ?)', (nome, hashed_password))
        conn.commit()
        conn.close()

        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('login'))

    return render_template('register.html')

# Página de registro de ponto
@app.route('/registro', methods=['GET', 'POST'])
def registro_ponto():
    if request.method == 'POST':
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            flash('Você precisa estar logado para registrar ponto.')
            return redirect(url_for('login'))

        tipo_registro = request.form.get('tipo_registro')
        data_atual = date.today()

        if tipo_registro not in ['entrada1', 'saida1', 'entrada2', 'saida2']:
            flash('Tipo de registro inválido!')
            return redirect(url_for('registro_ponto'))

        conn = sqlite3.connect('ponto.db')
        cursor = conn.cursor()

        # Verifica se já existe um registro para o dia
        cursor.execute('SELECT * FROM registros WHERE usuario_id = ? AND data = ?', (usuario_id, data_atual))
        registro = cursor.fetchone()

        if registro:
            # Atualiza o registro existente
            coluna = {
                'entrada1': 'entrada1',
                'saida1': 'saida1',
                'entrada2': 'entrada2',
                'saida2': 'saida2'
            }.get(tipo_registro)

            if coluna:
                if (registro[2] and tipo_registro == 'entrada1') or \
                   (registro[3] and tipo_registro == 'saida1') or \
                   (registro[4] and tipo_registro == 'entrada2') or \
                   (registro[5] and tipo_registro == 'saida2'):
                    flash(f'{tipo_registro.replace("entrada", "Entrada ").replace("saida", "Saída ")} já registrada!')
                else:
                    cursor.execute(f'UPDATE registros SET {coluna} = ? WHERE usuario_id = ? AND data = ?',
                                   (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), usuario_id, data_atual))
                    flash(f'Ponto {tipo_registro} registrado com sucesso!')
            else:
                flash('Tipo de registro inválido!')
        else:
            # Cria um novo registro para o dia
            cursor.execute('''
                INSERT INTO registros (usuario_id, entrada1, saida1, entrada2, saida2, data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (usuario_id, None, None, None, None, data_atual))
            
            coluna = {
                'entrada1': 'entrada1',
                'saida1': 'saida1',
                'entrada2': 'entrada2',
                'saida2': 'saida2'
            }.get(tipo_registro)

            if coluna:
                cursor.execute(f'UPDATE registros SET {coluna} = ? WHERE usuario_id = ? AND data = ?',
                               (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), usuario_id, data_atual))
                flash(f'Ponto {tipo_registro} registrado com sucesso!')
            else:
                flash('Tipo de registro inválido!')

        conn.commit()
        conn.close()

        return redirect(url_for('registro_ponto'))

    usuario_id = session.get('usuario_id')
    data_atual = date.today()

    conn = sqlite3.connect('ponto.db')
    cursor = conn.cursor()
    cursor.execute('SELECT entrada1, saida1, entrada2, saida2 FROM registros WHERE usuario_id = ? AND data = ?',
                   (usuario_id, data_atual))
    registros_do_dia = cursor.fetchone()
    conn.close()

    if registros_do_dia:
        # Corrigido para lidar com registros nulos
        registros_do_dia = [(datetime.strptime(r, '%Y-%m-%d %H:%M:%S').strftime('%H:%M') if r else '') for r in registros_do_dia]
    else:
        registros_do_dia = ['', '', '', '']  # Inicialize com strings vazias para entradas e saídas

    return render_template('registro.html', registros=registros_do_dia)

# Rota para logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario_id', None)
    flash('Você saiu com sucesso.')
    return redirect(url_for('login'))
