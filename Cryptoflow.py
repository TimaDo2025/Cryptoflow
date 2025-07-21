import requests
import time
import logging
from statistics import mean, stdev

ETHERSCAN_API_KEY = "your_etherscan_api_key"
ETHERSCAN_URL = "https://api.etherscan.io/api"

# Настройка логирования
logging.basicConfig(filename="anomalies.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Храним последние n транзакций
TX_HISTORY_LIMIT = 50
tx_values = []

def get_latest_transactions(address="0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"):
    """Получить последние входящие транзакции адреса."""
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }
    response = requests.get(ETHERSCAN_URL, params=params)
    data = response.json()
    if data["status"] == "1":
        return data["result"][:10]
    return []

def detect_anomaly(value_ether):
    """Простая аномалия на основе статистики."""
    global tx_values
    if len(tx_values) < TX_HISTORY_LIMIT:
        tx_values.append(value_ether)
        return False

    avg = mean(tx_values)
    deviation = stdev(tx_values)
    threshold = avg + 3 * deviation

    is_anomaly = value_ether > threshold
    tx_values.pop(0)
    tx_values.append(value_ether)

    return is_anomaly

def monitor():
    print("⛓️  Monitoring Ethereum transaction flow for anomalies...")
    seen_tx = set()
    while True:
        txs = get_latest_transactions()
        for tx in txs:
            if tx["hash"] in seen_tx:
                continue
            seen_tx.add(tx["hash"])

            value_ether = int(tx["value"]) / 1e18
            if detect_anomaly(value_ether):
                msg = f"🚨 Anomaly detected! TxHash: {tx['hash']} Value: {value_ether:.4f} ETH"
                print(msg)
                logging.info(msg)

        time.sleep(15)  # 15 секунд между проверками

if __name__ == "__main__":
    monitor()
