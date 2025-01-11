from website import *
from dotenv import load_dotenv
load_dotenv()

import threading, os

from waitress import serve
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


app = create_app(crawling=False)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080) # Stable run
    # app.run('0.0.0.0', 8080, False) # Debug


