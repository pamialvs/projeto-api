#importações
from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

#cria aplicação flask
app = Flask(__name__)
CORS(app)

#funcao para iniciar o bd SQLite
def init_db():
    #abre uma conexão com o bd
    with sqlite3.connect('database.db') as conn:
        conn.execute(""" CREATE TABLE IF NOT EXISTS livros(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            autor TEXT NOT NULL,
            imagem_url TEXT NOT NULL
            )
            """)
    print("Banco de dados inicicalizado com sucesso!")
    
init_db()

@app.route('/')
def homepage():
    return {
        "mensagem": "Bem-vindo à Biblioteca Vai na Web!",
        "instruções": {
            "cadastrar_livro": "Envie um POST para /doar com os dados do livro",
            "listar_livros": "Acesse GET /livros para ver todos os livros cadastrados",
        }
    }

#rota para cadastrar um novo livro POST
@app.route('/doar', methods=['POST'])
def doar():
    dados = request.get_json()
    
    titulo = dados.get("titulo")
    categoria = dados.get("categoria")
    autor = dados.get("autor")
    imagem_url = dados.get("imagem_url")
    #verificar se todos os campos forsm preenchidos
    if not all([titulo, categoria, autor, imagem_url]):
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    
    #conectar ao bd e inserir as informações do livro
    with sqlite3.connect('database.db') as conn:
        conn.execute(""" INSERT INTO livros (titulo, categoria, autor, imagem_url)
                     VALUES(?,?,?,?)
                     """, (titulo, categoria, autor, imagem_url))
        #salvar
        conn.commit
        return jsonify({'mensagem': 'Livros cadastrados com sucesso!'}), 201
#rota para listar os livros GET
@app.route('/livros', methods=['GET'])
def listar_livros():
    with sqlite3.connect('database.db') as conn:
        livros = conn.execute("SELECT * FROM livros").fetchall()
        
        livros_listados = []
        
        for livro in livros:
            dici_livros ={
                "id": livros[0],
                "titulo": livros[1],
                "categoria": livros[2],
                "autor": livros[3],
                "imagem_url": livros[4],
            }
            livros_listados.append(dici_livros)
        #retorna a lista no formato json
        return jsonify(livros_listados)

#rota para deletar um livro pelo ID DELETE
@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    #conectar ao db e criar um cursor para executar os comandos
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id))
        conn.commit()
    #verifica se o livro foi encontrado
    if cursor.rowcount == 0:
        return jsonify({"erro": "Livro não encontrado"}), 400

    return jsonify({"mensagem": "Livro excluído com sucesso"}), 200

#inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)