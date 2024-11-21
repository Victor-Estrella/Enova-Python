#-----------------------Imports-----------------------#
from flask import Flask, render_template, jsonify
import numpy as np
from datetime import datetime, timedelta
from flask_cors import CORS
#-----------------------Imports-----------------------#

app = Flask(__name__)
CORS(app)

#Esta função gera uma lista de datas aleatórias dentro de um intervalo.
def gerar_datas(inicio, fim, n):
    return [inicio + timedelta(days=np.random.randint(0, (fim - inicio).days)) for _ in range(n)]

#Esta função gera dados simulados para análise de eficiência.
def gerar_dados_simulados(n, inicio, fim):
    datas = gerar_datas(inicio, fim, n)
    nr_producao_energia = np.round(np.random.uniform(1000, 5000, n), 2)
    nr_consumo_energia = np.round(np.random.uniform(800, 4500, n), 2)
    nr_eficiencia = np.round((nr_producao_energia / nr_consumo_energia) * 100, 2)

    return {
        'datas': [d.strftime('%Y-%m-%d') for d in datas],
        'producoes': nr_producao_energia.tolist(),
        'consumos': nr_consumo_energia.tolist(),
        'eficiencia': nr_eficiencia.tolist()
    }

#Rota principal que exibe o gráfico.
@app.route('/eolica')
def eolica():
    # Gerar dados simulados
    n = 100
    inicio = datetime(2023, 1, 1)
    fim = datetime(2024, 1, 1)
    dados = gerar_dados_simulados(n, inicio, fim)

    # Passa os dados para o template
    return render_template('eolica.html', dados=dados)

#Rota principal que exibe o gráfico.
@app.route('/solar')
def solar():
    # Gerar dados simulados
    n = 100
    inicio = datetime(2023, 1, 1)
    fim = datetime(2024, 1, 1)
    dados = gerar_dados_simulados(n, inicio, fim)

    # Passa os dados para o template
    return jsonify(dados)


#Rota principal que exibe o gráfico.
@app.route('/manutencao')
def manutencao():
    # Gerar dados simulados
    n = 100
    inicio = datetime(2023, 1, 1)
    fim = datetime(2024, 1, 1)
    dados = gerar_dados_simulados(n, inicio, fim)

    # Passa os dados para o template
    return render_template('manutencao.html', dados=dados)

#Rota para retornar os dados em formato JSON.
@app.route('/')
def dados():
    n = 100
    inicio = datetime(2023, 1, 1)
    fim = datetime(2024, 1, 1)
    dados = gerar_dados_simulados(n, inicio, fim)
    return jsonify(dados)

if __name__ == '__main__':
    app.run(debug=True)
