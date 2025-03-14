from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pg8000
from functools import wraps
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

def get_db_connection():
    return pg8000.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PSW'],
        port=int(app.config['DB_PORT']),
        database=app.config['DB_NAME']
    )

def get_fabricas():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT fabrica FROM insp_final_checklist ORDER BY fabrica")
            return [fabrica[0] for fabrica in cursor.fetchall()]

# Adicione uma rota de health check
@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    fabricas = get_fabricas()
    return render_template('index.html', fabricas=fabricas)

@app.route('/consultar', methods=['POST'])
def consultar():
    data = request.get_json()
    data_inicio = data.get('data_inicio')
    data_fim = data.get('data_fim')
    fabrica = data.get('fabrica')
    aprovacao = data.get('aprovacao')

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                base_query = """
                    SELECT SUM(metro_quadrado) 
                    FROM insp_final_checklist
                    WHERE data BETWEEN %s AND %s
                """
                params = [data_inicio, data_fim]

                if fabrica and fabrica != "Todas":
                    base_query += " AND fabrica = %s"
                    params.append(fabrica)

                if aprovacao == "Todas":
                    # Consulta para total
                    cursor.execute(base_query, params)
                    resultado_total = cursor.fetchone()[0] or 0

                    # Consulta para "Sim"
                    sim_query = base_query + """ AND (a_peca_foi_aprovada = 'Sim' 
                                OR a_peca_foi_aprovada IS NULL 
                                OR a_peca_foi_aprovada = 'Condicional')"""
                    cursor.execute(sim_query, params)
                    resultado_sim = cursor.fetchone()[0] or 0

                    # Consulta para "Não"
                    nao_query = base_query + """ AND (a_peca_foi_aprovada = 'Não' 
                                OR a_peca_foi_aprovada = 'Bloqueio' 
                                OR a_peca_foi_aprovada = 'Liberado Din')"""
                    cursor.execute(nao_query, params)
                    resultado_nao = cursor.fetchone()[0] or 0

                    return jsonify({
                        'success': True,
                        'resultado': resultado_total,
                        'resultado_sim': resultado_sim,
                        'resultado_nao': resultado_nao,
                        'data_inicio': data_inicio,
                        'data_fim': data_fim,
                        'fabrica': fabrica,
                        'aprovacao': aprovacao
                    })
                else:
                    if aprovacao == "Sim":
                        base_query += """ AND (a_peca_foi_aprovada = 'Sim' 
                                    OR a_peca_foi_aprovada IS NULL 
                                    OR a_peca_foi_aprovada = 'Condicional')"""
                    else:  # Não
                        base_query += """ AND (a_peca_foi_aprovada = 'Não' 
                                    OR a_peca_foi_aprovada = 'Bloqueio' 
                                    OR a_peca_foi_aprovada = 'Liberado Din')"""
                    
                    cursor.execute(base_query, params)
                    resultado = cursor.fetchone()[0] or 0

                    return jsonify({
                        'success': True,
                        'resultado': resultado,
                        'data_inicio': data_inicio,
                        'data_fim': data_fim,
                        'fabrica': fabrica,
                        'aprovacao': aprovacao
                    })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False)