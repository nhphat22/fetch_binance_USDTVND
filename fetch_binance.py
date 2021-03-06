import sqlite3
import requests
import logging_handler

def fetch_binance():
    data = {
        "page": 1,
        "rows": 10,
        "payTypes": [],
        "asset": "USDT",
        "tradeType": "BUY",
        "fiat": "VND",
        "publisherType": "merchant"
    }
    r = requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
                    json=data)
    return r

def setup_mysql(logger):
    try:
        connection = sqlite3.connect('database.db')
        logger.info('CONNECTION SUCCESS')

        cur = connection.cursor()
        cur.execute('''Create table if not exists transaction_records
                    (id integer primary key autoincrement, 
                    price_avg float,
                    price_sum float, 
                    time datetime default current_timestamp)   
                    ''')

        logger.info(connection.commit)
        return connection
    except NameError:
        logger.error(NameError)
    pass

def calculation(arr):
    summary = sum(arr)
    avg = summary / len(arr)
    return summary, avg
    
if __name__ == '__main__':
    logger = logging_handler.setup_logging()
    connection = setup_mysql(logger=logger)

    response = fetch_binance()
    try:
        logger.info(response)
        data = response.json()['data']

        arr = [float(v['adv']['price']) for v in data]

        # calculation
        price_sum, price_avg = calculation(arr)

        connection.execute(
            "Insert into transaction_records(price_avg, price_sum) values (?,?)", (price_avg, price_sum))
        connection.commit()
    except NameError:
        logger.error(response)
    pass