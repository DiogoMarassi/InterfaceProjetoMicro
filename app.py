from flask import Flask, render_template, jsonify
from flask import Flask, render_template, request, redirect, url_for
from services.movimento_service import carregar_movimentos, adicionar_movimento, remover_movimento, editar_movimento, listar_movimentos
from services.mqtt_service import publicar_gesto, solicitar_clima, solicitar_rotinas, atualizar_rotinas, publicar_spotify, refresh_playlist, enviar_gesto_mqtt, enviar_lingua, envia_lista_para_sabre, iniciar_mqtt_em_thread
from services.significados_service import listar_significados
from services.playlists_service import listar_playlists
from services.historico_service import salvar_historico, listar_historico
import ast
app = Flask(__name__)

# Integração com o Home Assistant
@app.route('/executar/<gesto>')
def executar(gesto):
    gesto = "\"" + gesto + "\""
    publicar_gesto(gesto)
    return f"Gesto '{gesto}' enviado via MQTT!"

@app.route('/registrar-gesto', methods=['POST'])
def registrar():
    dados = request.json
    print("Recebido:", dados)
    # Chame sua função Python aqui
    salvar_historico(dados['gesto'])
    return {"status": "ok"}

@app.route('/ver_historico')
def ver_historico():
    historico = listar_historico()
    return render_template('historico.html', historico=historico)

@app.route('/ver_gravacao')
def ver_gravacao():
    return render_template('visualizar-gravacao.html')

# Página inicial
@app.route('/index')
def home():
    dados = carregar_movimentos()
    return render_template('index.html', movimentos=dados)

# Página inicial
@app.route('/ver_tempo')
def ver_tempo():
    try:
        clima = solicitar_clima()
        return render_template('ver-tempo.html', clima=clima)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

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
    significados = listar_significados()
    gesto = request.args.get('gesto', '')
    playlists = listar_playlists()
    return render_template('finalizar.html', gesto=gesto, significados=significados, playlist_json=playlists)

# Lista de movimentos
@app.route('/movimentos')
def movimentos():
    dados = carregar_movimentos()
    return render_template("movimentos.html", movimentos=dados)

def extrair_iniciais(texto):
    partes = texto.split(",")
    iniciais = [p.strip()[0].upper() for p in partes if p.strip()]
    return "".join(iniciais).lower()

# CRUD DO MOVIMENTO
@app.route('/cadastrar', methods=['POST'])
def cadastrarMovimento():
    gesto = request.form['gesto']
    significado = request.form['significado']
    genero = request.form['genero']
    print(genero)

    significados = listar_significados()
    playlists = listar_playlists()

    # ENVIAR GESTOS PARA O SABRE/COMANDO/GESTO
    print("Estou trabalhando com o gesto abaixo:")
    print(gesto)
    print(type(gesto))
    dados_para_enviar_gesto = extrair_iniciais(gesto)
    print(dados_para_enviar_gesto)
    enviar_gesto_mqtt(dados_para_enviar_gesto)
    print("saiu do mqtt")

    # ----- NOVO TRECHO: capturar e exibir idioma selecionado -----
    idioma = request.form.get('idioma')  # retorna None se não enviado

    try:
        lista_gestos = [g.strip().capitalize() for g in gesto.split(',') if g.strip()]
        if significado != 'toca_playlist':
            genero = ''
        adicionar_movimento(lista_gestos, significado, genero, idioma)
        jsonGestos = listar_movimentos()

        gestosFormatados = [''.join(g[0] for g in item['gesto']).lower() for item in jsonGestos]
        print("json gestos --------------------------------")
        print(gestosFormatados)
        print(type(gestosFormatados))

        envia_lista_para_sabre(gestosFormatados)
        return redirect(url_for('home', gesto=gesto, significado=significado, significados=significados))
    except ValueError as e:
        return render_template(
            'finalizar.html',
            erro=str(e),
            significado=significado,
            significados=significados,
            playlist_json=playlists
        )


@app.route('/remover/<gesto>')
def removerMovimento(gesto):
    remover_movimento(gesto)
    return redirect(url_for('home'))

@app.route('/tocar_playlist/<genero>')
def tocarPlaylist(genero):
    publicar_spotify(genero)
    return genero

@app.route('/ver_rotinas')
def ver_rotinas():
    rotinas_atualizadas = solicitar_rotinas()
    atualizar_rotinas(rotinas_atualizadas)
    return render_template(
        'index.html', sucesso = True)

@app.route('/editar/<gesto>', methods=['GET', 'POST'])
def editarMovimento(gesto):
    print("Entrou na rota editar")
    gesto = ast.literal_eval(gesto)
    movimentos = listar_movimentos()
    significados = listar_significados()

    movimento = next((m for m in movimentos if m['gesto'] == gesto), None)

    if movimento is None:
        return f"Gesto '{gesto}' não encontrado.", 404

    if request.method == 'POST':
        novo_gesto = request.form['novo_gesto']
        novo_significado = request.form['significado']

        significado_antigo = movimento['significado']  # <- Pegando o significado atual (antigo)

        try:
            print("gesto enviado")
            print(gesto)
            print(type(gesto)) # Envio uma lista de gestos
            editar_movimento(gesto, novo_gesto, significado_antigo, novo_significado)
            return redirect(url_for('home', gesto=gesto, significados=significados) )
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

import ast

@app.route('/testarMovimento/<gesto>')
def testarMovimento(gesto):
    from ast import literal_eval

    movimentos = carregar_movimentos()

    print("Gesto recebido:", gesto)
    print("MOVIMENTOS ---------------------")
    print(movimentos)

    
    try:
        # Converte string para lista
        gesto_lista = literal_eval(gesto)
    except Exception:
        return "Formato de gesto inválido.", 400

    print("Gesto como lista:", gesto_lista)

    # Normaliza a entrada
    gesto_normalizado = [g.lower() for g in gesto_lista]

    # Busca movimento com a mesma sequência de gestos (case-insensitive)
    movimento = next(
        (m for m in movimentos if [s.lower() for s in m["gesto"]] == gesto_normalizado),
        None
    )

    print("Movimento encontrado:", movimento)

    if not movimento:
        return f"Gesto '{gesto}' não encontrado.", 404

    significado = movimento.get("significado")
    genero = movimento.get("genero")
    lingua = movimento.get("idioma")

    try:
        if significado.lower() in ("toca_playlist", "toca_musica"):
            publicar_spotify(genero)
        elif significado.lower() == "notifica_tempo":
            print("LINGUA ---------------------")
            print(lingua)
            enviar_lingua(lingua)
        elif significado.lower() == "refresh_rotinas":
            solicitar_rotinas()
        elif significado.lower() == "refresh_playlist":
            refresh_playlist()
        else:
            publicar_gesto(f'"{significado}"')
        return redirect(url_for('home'))
    except Exception as e:
        return f"Erro ao testar gesto: {str(e)}", 500





if __name__ == '__main__':
    iniciar_mqtt_em_thread()
    app.run(debug=True)
