from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_app, db
from models import Usuario, registrar_entrada, registrar_saida, Produto  # 👈 Import do modelo Produto
import os

# -------------------
# Configuração de diretórios
# -------------------
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "../frontend")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=TEMPLATE_DIR)
init_app(app)

# -------------------
# Rotas de páginas
# -------------------
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register_page")
def register_page():
    return render_template("criar_conta.html")

@app.route("/produtos")
def produtos_page():
    return render_template("produtos.html")

@app.route("/clientes")
def clientes_page():
    return render_template("clientes.html")

@app.route("/estoque")
def estoque_page():
    return render_template("estoque.html")

@app.route("/faturamento")
def faturamento_page():
    return render_template("faturamento.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

# -------------------
# Rotas de login e registro
# -------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify(status="erro", mensagem="Preencha todos os campos"), 400

    if Usuario.query.filter_by(email=email.lower()).first():
        return jsonify(status="erro", mensagem="E-mail já cadastrado"), 400

    try:
        user = Usuario(
            nome=nome.lower(),
            perfil="cliente",
            email=email.lower(),
            senha_hash=generate_password_hash(senha)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(status="ok", mensagem="Conta criada com sucesso!")
    except Exception as e:
        db.session.rollback()
        return jsonify(status="erro", mensagem=str(e))

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify(status="erro", mensagem="Preencha todos os campos"), 400

    user = Usuario.query.filter_by(email=email.lower()).first()
    if not user:
        return jsonify(status="erro", mensagem="Conta não encontrada"), 401

    if not check_password_hash(user.senha_hash, senha):
        return jsonify(status="erro", mensagem="Senha incorreta"), 401

    return jsonify(status="ok", mensagem="Login realizado com sucesso")

# -------------------
# Teste de conexão ao DB
# -------------------
@app.route("/teste_db")
def teste_db():
    try:
        db.session.execute("SELECT 1")
        return "✅ Conectado ao banco!"
    except Exception as e:
        return f"❌ Erro ao conectar: {e}"

# -------------------
# Rotas de estoque
# -------------------
@app.route("/estoque/entrada", methods=["POST"])
def entrada_estoque():
    data = request.get_json()
    produto_id = data["produto_id"]
    quantidade = data["quantidade"]
    usuario_id = data["usuario_id"]

    try:
        total = registrar_entrada(produto_id, quantidade, usuario_id)
        return {"status": "ok", "estoque_atual": float(total)}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}, 400

@app.route("/pedido/confirmar", methods=["POST"])
def confirmar_pedido():
    data = request.get_json()
    item_id = data["item_pedido_id"]
    usuario_id = data["usuario_id"]

    try:
        total = registrar_saida(item_id, usuario_id)
        return {"status": "ok", "estoque_atual": float(total)}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}, 400

# -------------------
# Rotas de produtos (NOVAS)
# -------------------

# 👉 Cadastrar produto
@app.route("/produtos/salvar", methods=["POST"])
def salvar_produto():
    data = request.get_json()

    nome = data.get("nome")
    formato = data.get("formato")
    preco = data.get("preco")
    estoque = data.get("estoque")

    if not nome or preco is None or estoque is None:
        return jsonify(status="erro", mensagem="Preencha todos os campos"), 400

    try:
        novo_produto = Produto(
            nome=nome,
            formato=formato,
            preco=preco,
            estoque=estoque
        )
        db.session.add(novo_produto)
        db.session.commit()
        return jsonify(status="ok", mensagem="Produto salvo com sucesso!")
    except Exception as e:
        db.session.rollback()
        return jsonify(status="erro", mensagem=str(e)), 500

# 👉 Listar produtos
@app.route("/produtos/listar", methods=["GET"])
def listar_produtos():
    try:
        produtos = Produto.query.all()
        lista = [
            {
                "id": p.id,
                "nome": p.nome,
                "formato": p.formato,
                "preco": p.preco,
                "estoque": p.estoque
            } for p in produtos
        ]
        return jsonify(lista)
    except Exception as e:
        return jsonify(status="erro", mensagem=str(e)), 500

# -------------------
# Rodar app
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
