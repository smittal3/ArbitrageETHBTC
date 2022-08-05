import alpaca_trade_api as alpaca
import requests
import asyncio
import config

ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'
DATA_URL = 'https://data.alpaca.markets'
rest_api = alpaca.REST(config.API_KEY, config.SECRET_KEY, ALPACA_BASE_URL)

# wait time between trades
waitTime = 3
min_arb_percent = 0.3

prices = {
    'ETH/USD' : 0,
    'BTC/USD' : 0,
    'ETH/BTC' : 0
}

# Get quote data from alpaca
async def get_quote(symbol: str):
  try:
    # make the request
    quote = requests.get('{0}/v1beta2/crypto/latest/trades?symbols={1}'.format(DATA_URL, symbol), headers=HEADERS)
    prices[symbol] = quote.json()['trades'][symbol]['p']
    # Status code 200 means the request was successful
    if quote.status_code != 200:
        print("Undesirable response from Alpaca! {}".format(quote.json()))
        return False
  except Exception as e:
    print("There was an issue getting trade quote from Alpaca: {0}".format(e))
    return False
  
  # Place an order
def post_alpaca_order(symbol, qty, side):
  try:
    order = requests.post(
      '{0}/v2/orders'.format(ALPACA_BASE_URL), headers=HEADERS, json={
      'symbol': symbol,
      'qty': qty,
      'side': side,
      'type': 'market',
      'time_in_force': 'gtc',
    })
    return order
  except Exception as e:
    print("There was an issue posting order to Alpaca: {0}".format(e))
    return False
  
# Check for arbitrage conditions and execute trades
async def check_arb():
  ETH = prices['ETH/USD']
  BTC = prices['BTC/USD']
  ETHBTC = prices['ETH/BTC']
  DIV = ETH / BTC
  
  spread = abs(DIV - ETHBTC)
  BUY_ETH = 1000 / ETH
  BUY_BTC = 1000 / BTC
  BUY_ETHBTC = BUY_BTC / ETHBTC
  SELL_ETHBTC = BUY_ETH / ETHBTC
  
  # Indicates 
  if DIV > ETHBTC * (1 + min_arb_percent/100):
    order = post_alpaca_order()