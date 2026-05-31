from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)
logging.getLogger('werkzeug').disabled = True
app.logger.disabled = True

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080, use_reloader=False)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
