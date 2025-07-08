from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

# conexao com o banco de dados 'gradtrack'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://gradtrack_n8vr_user:KnykSEUszpW4zdXvVZ6IyYgIY9wOmXlY@dpg-d1mmoobipnbc73c4ns8g-a.oregon-postgres.render.com/gradtrack_n8vr?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# pasta que guardara os comprovantes localmente
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'comprovantes_aluno1')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
base_path = app.config['UPLOAD_FOLDER']

# total de horas de atividades complementares a serem cumpridas
TOTAL_HORAS = 90

''' Informações da tabela de atividades do banco de dados '''
class Atividade(db.Model):
    __tablename__ = 'atividades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)             # atividade
    tempo_minimo = db.Column(db.String(100))                     # tempo minimo a ser cumprido
    tempo_contado = db.Column(db.String(100))                    # tempo creditado
    tempo_maximo = db.Column(db.String(100))                     # tempo maximo creditado
    comprovante = db.Column(db.String(200))                      # tipo de comprovante necessario

''' Informações da tabela de eventos do banco de dados '''
class Evento(db.Model):
    __tablename__ = 'prazos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)           # evento 
    data = db.Column(db.Date, nullable=False)                    # data de realizacao
    
    # conversao para dicionario para a leitura pelo json no calendario
    def to_dict(self):
        return { 'id': self.id, 'titulo': self.titulo, 'data': self.data.isoformat(), }

''' Informações da tabela de comprovantes do aluno x do banco de dados '''
class Comprovante(db.Model):
    __tablename__ = 'comprovantes_aluno1'
    id = db.Column(db.Integer, primary_key=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)                # id da atividade na tabela das atividades
    horas = db.Column(db.Integer, nullable=False)                                                       # horas cumpridas pelo aluno
    arquivo_nome = db.Column(db.String(255), nullable=False)                                            # titulo do arquivo
    arquivo_caminho = db.Column(db.Text, nullable=False)                                                # localizacao do arquivo localmente

    atividade = db.relationship('Atividade', backref=db.backref('comprovantes_aluno1', lazy=True))

''' Conversao da tabela de atividades para utf-8 '''
def codificarAtividade(atividades):
    for a in atividades:
        a.nome = a.nome.encode('latin1').decode('utf-8')
        a.minimo = a.tempo_minimo.encode('latin1').decode('utf-8')
        a.contado = a.tempo_contado.encode('latin1').decode('utf-8')
        a.maximo = a.tempo_maximo.encode('latin1').decode('utf-8')
        a.comprovante = a.comprovante.encode('latin1').decode('utf-8')

''' Conversao da tabela de eventos para utf-8 '''
def codificarEvento(eventos):
    for e in eventos:
        e.titulo = e.titulo.encode('latin1').decode('utf-8')

''' Conversao da tabela de comprovantes para utf-8 '''
def codificarComprovante(comprovantes):
    for c in comprovantes:
        c.arquivo_nome = c.arquivo_nome.encode('latin1').decode('utf-8')
        c.arquivo_caminho = c.arquivo_caminho.encode('latin1').decode('utf-8')

'''
    Rota para pagina inicial

    Exibe: possiveis atividades complementares e prazos da universidade

    Consulta: 
        tabela no banco de dados com todas as atividades que garantem horas complementares
        tabela no banco de dados com todos os prazos da universidade
'''
@app.route('/')
def index():
    atividades = Atividade.query.all()
    codificarAtividade(atividades)

    eventos = Evento.query.all()
    codificarEvento(eventos)
    
    return render_template('index.html', atividades=atividades, eventos=[e.to_dict() for e in eventos])

'''
    Rota para pagina de atividades

    Exibe: todas as possiveis atividades complementares

    Consulta: tabela no banco de dados com todas as atividades que garantem horas complementares
'''
@app.route('/atividades')
def atividades():
    atividades = Atividade.query.all()

    codificarAtividade(atividades)

    return render_template('atividades.html', atividades=atividades)

'''
    Rota para pagina de comprovantes

    Exibe: 
        cards com todos os comprovantes carregados pelo aluno
        total de horas complementares cumpridas
        horas complementares cumpridas por atividade

    Consulta: tabela no banco de dados com todos os comprovantes carregados pelo aluno
'''
@app.route('/comprovantes')
def comprovantes():
    atividades = Atividade.query.all()
    codificarAtividade(atividades)
    
    ja_cumpridas = db.session.query(func.sum(Comprovante.horas)).scalar()
    nao_cumpridas = TOTAL_HORAS - ja_cumpridas

    subquery = (
        db.session.query(
            Comprovante.atividade_id.label('atividade_id'),
            func.sum(Comprovante.horas).label('total_horas')
        )
        .group_by(Comprovante.atividade_id)
        .subquery()
    )

    atividades_com_horas = (
        db.session.query( Atividade.id, Atividade.nome, subquery.c.total_horas )
        .join(subquery, Atividade.id == subquery.c.atividade_id)
        .all()
    )

    dados = []
    for id, nome, total in atividades_com_horas:
        comprovantes = Comprovante.query.filter_by(atividade_id=id).all()
        codificarComprovante(comprovantes)
        dados.append({ 'id': id, 'nome': nome, 'total_horas': total, 'comprovantes': comprovantes })

    return render_template('comprovantes.html', dados=dados, ja_cumpridas=ja_cumpridas, nao_cumpridas=nao_cumpridas)

'''
    Rota para pagina do calendario institucional

    Exibe: calendario com as atividades da universidade

    Consulta: tabela no banco de dados com todos os prazos institucionais
'''
@app.route('/calendario')
def calendario():
    eventos = Evento.query.all()
    codificarEvento(eventos)
    
    return render_template('calendario.html', eventos=[e.to_dict() for e in eventos])

'''
    Upload dos comprovantes 

    Cria localmente a pasta para a atividade (caso nao exista) e adiciona o comprovante 
    conforme o indicado pelo usuario.

    Adiciona o novo upload na tabela de comprovantes do aluno no banco de dados, com: 
    nome da atividade, horas realizadas, nome do arquivo do comprovante e caminho para
    acessar o comprovante
'''
@app.route('/upload', methods=['POST'])
def upload_file():
    # informacoes carregadas pelo aluno
    atividade_id = request.form.get('activitySelect')
    horas = int(request.form.get('newActivityHours'))
    file = request.files.get('receiptFile')

    nome_arquivo=file.filename
    atividade = Atividade.query.get(atividade_id)
    nome_atividade = atividade.nome.encode('latin1').decode('utf-8')

    # salvar o comprovante localmente
    pasta_destino = os.path.join(base_path, nome_atividade)
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_destino, file.filename)
    file.save(caminho_arquivo)

    # registro do comprovante no banco
    caminho_banco = f'comprovantes_aluno1/{atividade.nome}/{nome_arquivo}'
    comprovante = Comprovante( atividade_id=atividade_id, horas=horas, arquivo_nome=nome_arquivo, arquivo_caminho=caminho_banco )
    db.session.add(comprovante)
    db.session.commit()

    return redirect(url_for('comprovantes'))

if __name__ == '__main__':
    app.run(debug=True)
