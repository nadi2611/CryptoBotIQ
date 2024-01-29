import logging

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient

from interface.root_component import Root
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

    binance = BinanceFuturesClient(binance_public_key, binance_secret_key, testnet_applied)
    bitmex = BitmexClient(bitmax_public_key, bitmax_secret_key, testnet_applied)

    root = Root(binance, bitmex)
    root.mainloop()
