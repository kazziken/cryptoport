from crypt import methods
from itsdangerous import _json

import requests
from collections import defaultdict
from datetime import datetime
from psycopg2 import pool
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

# from logic import BOUGHT, SOLD
from logic import format_db_row_to_transaction

app = Flask(__name__)
cors = CORS(app) #so our app supports Cross Origin Requests

#pool we use to communicate b/w our DB and Flask App
postgreSQL_pool = pool.SimpleConnectionPool(
    1, 1000, database="exampledb", user="docker", password="docker", host="0.0.0.0"
)
app.config['postgreSQL_pool'] = postgreSQL_pool

#first endpoint
@app.route("/")
def healthcheck():
    return "I am alive"

@app.route("/transactions", methods=["POST"])
def new_transaction():
    name = request.json["name"]
    symbol = request.json["symbol"]
    type = request.json["type"]
    amount = request.json["amount"]

    time_transacted = datetime.fromtimestamp(request.json["time_transacted"])
    time_created = datetime.fromtimestamp(request.json["time_created"])
    price_purchased_at = float(request.json["price_purchased_at"])
    no_of_coins = float(request.json["no_of_coins"])

    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()

    insert_statement = f"INSERT INTO transaction (name,symbol,type,amount,times_transacted, time_created, price_purchased_at, no_of_coins) VALUES ('{name}, {symbol}, {type}, {amount}, {time_transacted}, {time_created}, {price_purchased_at}, {no_of_coins}')"
    cur.execute(insert_statement)
    conn.commit()

    return jsonify(request.json)

app.run(debug=True, port=5000)


@app.route("/transactions")
@cross_origin
def get_transactions():
    cur = postgreSQL_pool.getconn().cursor()
    cur.execute("SELECT * from TRANSACTION")
    rows = cur.fetchall()

    return jsonify(
        [
            format_db_row_to_transaction(row)
            for row in rows
        ]
    )