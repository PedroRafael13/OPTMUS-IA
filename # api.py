# api.py

from flask import Flask, jsonify
from flask_cors import CORS

# Inicializa a aplicação Flask
app = Flask(__name__)

# Habilita o CORS para permitir a comunicação com o frontend
CORS(app)

# Cria uma rota de teste para a raiz da API
@app.route("/")
def index():
    return jsonify({"message": "API do RADAR OPTMUS está no ar!"})

# Executa o servidor quando o script é chamado
if __name__ == '__main__':
    # O host='0.0.0.0' permite que a API seja acessível na sua rede local
    app.run(host='0.0.0.0', port=5000, debug=True)