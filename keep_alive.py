from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "Bot is alive!"  # 이 텍스트가 웹에서 떠야 해요


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    Thread(target=run).start()
