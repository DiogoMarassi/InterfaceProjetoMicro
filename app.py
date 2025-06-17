from flask import Flask, render_template
from flask import Flask, render_template, request, redirect, url_for
from services.movimento_service import carregar_movimentos, adicionar_movimento, remover_movimento, editar_movimento, listar_movimentos
from services.mqtt_service import publicar_gesto
from services.significados_service import listar_significados
app = Flask(__name__)

# Integração com o Home Assistant
@app.route('/executar/<gesto>')
def executar(gesto):
    gesto = gesto
    publicar_gesto(gesto)
    return f"Gesto '{gesto}' enviado via MQTT!"

# Página inicial
@app.route('/index')
def home():
    return render_template('index.html')

# Página inicial
@app.route('/mov-pre-definidos')
def mov_pre_definidos():
    return render_template('mov-pre-definidos.html')

# Seleção do tipo de gesto
@app.route('/tipo-gesto')
def tipo_gesto():
    return render_template('tipo-gesto.html')

# Início da gravação
@app.route('/gravacao-iniciou')
def gravacao_iniciou():
    return render_template('gravacao-iniciou.html')

# Tela de gravação
@app.route('/gravar')
def gravar():
    return render_template('gravar.html')

@app.route('/finalizar')
def finalizar():
    gesto = request.args.get('gesto', '') 
    return render_template('finalizar.html', gesto=gesto)

# Lista de movimentos
@app.route('/movimentos')
def movimentos():
    dados = carregar_movimentos()
    return render_template("movimentos.html", movimentos=dados)

# CRUD DO MOVIMENTO
@app.route('/cadastrar', methods=['POST'])
def cadastrarMovimento():
    gesto = request.form['gesto']
    significado = request.form['significado']

    try:
        adicionar_movimento(gesto, significado)
        return redirect(url_for('movimentos'))
    except ValueError as e:
        return render_template(
            'finalizar.html',
            erro=str(e),
            gesto=gesto,
            significado=significado,
        )

@app.route('/remover/<gesto>')
def removerMovimento(gesto):
    remover_movimento(gesto)
    return redirect(url_for('movimentos'))

@app.route('/editar/<gesto>', methods=['GET', 'POST'])
def editarMovimento(gesto):
    print("Entrou na rota editar")
    movimentos = listar_movimentos()
    significados = listar_significados()
    print("Significados:", significados)

    movimento = next((m for m in movimentos if m['gesto'] == gesto), None)

    if movimento is None:
        return f"Gesto '{gesto}' não encontrado.", 404

    if request.method == 'POST':
        novo_gesto = request.form['novo_gesto']
        novo_significado = request.form['significado']

        try:
            editar_movimento(gesto, novo_gesto, novo_significado)
            return redirect(url_for('movimentos'))
        except ValueError as e:
            return render_template(
                'editarMovimento.html',
                gesto=novo_gesto,
                significado=novo_significado,
                significados=significados,
                erro=str(e)
            )

    return render_template(
        'editarMovimento.html',
        gesto=movimento['gesto'],
        significado=movimento['significado'],
        significados=significados
    )


if __name__ == '__main__':
    app.run(debug=True)
