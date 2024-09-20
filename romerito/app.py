from flask import Flask, render_template \
    , url_for, request, redirect

from flask_login import LoginManager \
    , login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import User
from flask_mysqldb import MySQL


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERMEGADIFICIL'
login_manager.init_app(app)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_banco'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

conexao = MySQL(app)
def obter_conexao():
    return conexao.connection.cursor()

#######################################################################

@app.route('/')
def index():
    conn = obter_conexao()
    conn = conexao.connection.cursor()
    conn.execute("SELECT * FROM usuarios")
    usuarios = conn.fetchall()  
    conn.close()  
    conn.close()    
    return render_template('pages/index.html')

#######################################################################

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['pass']
        
        user = User.get_by_email(email)

        if user and check_password_hash(user.senha, senha):
            
            login_user(user)

            return redirect(url_for('ver_tarefa'))

    return render_template('pages/login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        senha = generate_password_hash(request.form['pass'])

        conn = conexao.connection.cursor()
        #conexao = obter_conexao()
        INSERT = 'INSERT INTO usuarios(email,senha) VALUES (%s, %s)'
        
        try:
            conn.execute(INSERT, (email, senha)) 
            conexao.connection.commit()  
        except Exception as e:
            print(f"An error occurred: {e}")  
            conexao.connection.rollback()  
        finally:
            conn.close()  

        return redirect(url_for('index'))

    return render_template('pages/cadastro.html')

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))

#######################################################################

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_tarefa():
    if request.method == 'POST':
        titulo = request.form['nome']
        conteudo = request.form['conteudo']
        
        # Conexão ao banco de dados
        conn = conexao.connection.cursor()
        
        # Corrigindo a consulta SQL
        conn.execute("INSERT INTO tarefas (titulo, conteudo) VALUES (%s, %s)", (titulo, conteudo))
        
        # Salva as mudanças
        conexao.connection.commit()
        conn.close()
        
        return redirect(url_for('ver_tarefa')) 

    return render_template('pages/criar-tarefa.html')

@app.route('/tarefas')
@login_required
def ver_tarefa():
    cursor = conexao.connection.cursor()  
    cursor.execute("SELECT * FROM tarefas") 
    tarefas = cursor.fetchall() 
    cursor.close() 

    return render_template('pages/tarefas.html', tarefas=tarefas)



@app.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    conn = conexao.connection.cursor()
    conn.execute("DELETE FROM tarefas WHERE id = %s", (id,))
    conexao.connection.commit()
    conn.close()
    return redirect(url_for('ver_tarefa'))