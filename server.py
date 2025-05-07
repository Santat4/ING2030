# server.py
from flask import Flask, jsonify
from WebScrapping import saldo_inicial, scraping_emails, calcular_total
app = Flask(__name__)

@app.route('/balance')
def balance():
    saldo_inicial("01/04/2025", "00:00", "+150000", "Cantidad Inicial", "****2094")
    scraping_emails()
    saldo = calcular_total()
    print("\n", "BALANCE: " + saldo, "\n")
    return jsonify({'balance': saldo})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
