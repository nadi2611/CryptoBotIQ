import logging

from connectors.binance import BinanceClient
from connectors.bitmex import BitmexClient

from UI.ui_main import interface
import configparser

logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.ini')

    testnet_applied = eval(config.get('DataBase', 'TESTNET_APPLIED'))

    binance_secret_key = config.get('Credentials', 'BINANCE_SECRET_KEY')
    binance_public_key = config.get('Credentials', 'BINANCE_PUBLIC_KEY')

    bitmax_secret_key = config.get('Credentials', 'BITMAX_SECRET_KEY')
    bitmax_public_key = config.get('Credentials', 'BITMAX_PUBLIC_KEY')

    binance = BinanceClient(binance_public_key,
                            binance_secret_key,
                            testnet=True, futures=True)
    bitmex = BitmexClient(bitmax_public_key, bitmax_secret_key, testnet=True)

    root = interface(bitmex, binance)
    root.mainloop()

