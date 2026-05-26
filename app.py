import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
# Permite requisições do seu site estático
CORS(app)

# Configuração do Banco de Dados (pega da variável de ambiente no Render, ou usa SQLite localmente para testes)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
# Correção necessária para o Render (troca postgres:// por postgresql://)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Presente
class Presente(db.Model):
    id = db.Column(db.String(100), primary_key=True) # Ex: 'liquidificador-oster'
    nome = db.Column(db.String(200), nullable=False)
    confirmado = db.Column(db.Boolean, default=False)

# Rota 1: Listar todos os presentes
@app.route('/presentes', methods=['GET'])
def get_presentes():
    presentes = Presente.query.all()
    resultado = [
        {"id": p.id, "nome": p.nome, "confirmado": p.confirmado} 
        for p in presentes
    ]
    return jsonify(resultado)

# Rota 2: Confirmar um presente
@app.route('/presentes/<string:presente_id>/confirmar', methods=['POST'])
def confirmar_presente(presente_id):
    presente = Presente.query.get(presente_id)
    
    if not presente:
        # Se o presente não existir no banco ainda, criamos ele já confirmado
        novo_presente = Presente(id=presente_id, nome=presente_id.replace('-', ' ').title(), confirmado=True)
        db.session.add(novo_presente)
        db.session.commit()
        return jsonify({"mensagem": "Presente criado e confirmado com sucesso!"}), 201

    if presente.confirmado:
        return jsonify({"erro": "Presente já foi confirmado por outro convidado."}), 400

    # Se já existir e não estiver confirmado, atualiza o status
    presente.confirmado = True
    db.session.commit()
    return jsonify({"mensagem": "Presente confirmado com sucesso!"}), 200


# Rota para resetar os testes
@app.route('/resetar-testes', methods=['GET'])
def resetar_testes():
    # Opção A: Apenas desmarcar os confirmados
    presentes = Presente.query.all()
    for p in presentes:
        p.confirmado = False
    
    Presente.query.delete()

    db.session.commit()
    return jsonify({"mensagem": "Banco de dados resetado com sucesso!"}), 200

# Cria as tabelas antes da primeira requisição, se não existirem
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)