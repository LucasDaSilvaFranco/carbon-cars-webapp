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
                query = """
                    SELECT SUM(metro_quadrado) 
                    FROM insp_final_checklist
                    WHERE data BETWEEN %s AND %s
                """
                params = [data_inicio, data_fim]

                if fabrica and fabrica != "Todas":
                    query += " AND fabrica = %s"
                    params.append(fabrica)

                if aprovacao and aprovacao != "Todas":
                    query += " AND a_peca_foi_aprovada = %s"
                    params.append(aprovacao)

                cursor.execute(query, params)
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