import sqlite3

def init_db():
    conn = sqlite3.connect('ponto.db')
    cursor = conn.cursor()

    # Criação da tabela 'usuarios'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    # Criação da tabela 'registros'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            entrada1 DATETIME,
            saida1 DATETIME,
            entrada2 DATETIME,
            saida2 DATETIME,
            data DATE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE (usuario_id, data)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso.")

if __name__ == '__main__':
    init_db()
