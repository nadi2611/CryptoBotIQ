import logging

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient

from interface.root_component import Root


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

    binance = BinanceFuturesClient("4197cc87601e6fd6ea73912920fe0a24f085dc590757560ec67651e643e1e2c6", "67fa734bc9f08f8d0e5499a30529a1a1cc7386b3ed52b287db314221fae3af6b", True)
    bitmex = BitmexClient("skpzrUOATohVu89EXatPDgnf", "wmjL4btPTWLb5kV1OQPwvzGmYeN5e6zDbadeseLGoZyGYgiF", True)

    root = Root(binance, bitmex)
    root.mainloop()
