from flask import Flask, render_template

app = Flask(__name__)

# Página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Lista de movimentos
@app.route('/movimentos.html')
def movimentos():
    return render_template('movimentos.html')

# Seleção do tipo de gesto
@app.route('/tipo-gesto.html')
def tipo_gesto():
    return render_template('tipo-gesto.html')

# Início da gravação
@app.route('/gravacao-iniciou.html')
def gravacao_iniciou():
    return render_template('gravacao-iniciou.html')

# Tela de gravação
@app.route('/gravar.html')
def gravar():
    return render_template('gravar.html')

# Conclusão da gravação
@app.route('/finalizar.html')
def finalizar():
    return render_template('finalizar.html')

if __name__ == '__main__':
    app.run(debug=True)
