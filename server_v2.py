from flask import Flask, jsonify
from WebScrapping import saldo_inicial, scraping_emails, calcular_total
import logging

app = Flask(__name__)

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/balance')
def balance():
    try:
        # Establecer saldo inicial si no existe
        saldo_inicial("01/04/2025", "00:00", "+150000", "Cantidad Inicial", "****2094")
        
        # Ejecutar scraping
        scraping_emails()
        
        # Calcular y devolver balance
        saldo = calcular_total()
        logger.info(f"Balance calculado: {saldo}")
        return jsonify({'balance': saldo, 'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error en la ruta /balance: {str(e)}")
        return jsonify({'error': str(e), 'status': 'failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)