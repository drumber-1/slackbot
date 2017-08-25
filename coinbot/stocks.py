import utils


class StockReturnCodes:
    Good, NoFundsError, MiscError = range(3)


class Account(object):
    def __init__(self, user_id, starting_cash):
        self.user_id = user_id
        self.cash = starting_cash
        self.bitcoin = 0


class Transaction(object):
    def __init__(self, cash, coin, code):
        self.cash = cash
        self.coin = coin
        self.error = code


class Stocks(object):

    def __init__(self):
        self.accounts = {}
        self.transaction_fee_fraction = 0.03
        self.initial_cash = 100

    def add_account(self, id):
        if id in self.accounts:
            return False
        else:
            self.accounts[id] = Account(id, self.initial_cash)
            return True

    def buy(self, id, cash_value):
        account = self.accounts[id]
        if cash_value > account.cash:
            return Transaction(0, 0, StockReturnCodes.NoFundsError)
        btc_value = cash_value / self.get_price_bitcoin()
        transaction_fee_btc = btc_value * self.transaction_fee_fraction

        account.cash -= cash_value
        account.bitcoin += btc_value - transaction_fee_btc
        return StockReturnCodes.Good
        #return "You bought {} btc ( {} btc - {} btc transaction fee ) for $ {}".format(btc_value - transaction_fee_btc, btc_value, transaction_fee_btc, cash_value)

    def get_price_bitcoin(self):
        url = 'https://api.coindesk.com/v1/bpi/currentprice/{}.json'.format("USD")
        data = utils.get_url_response(url)
        price = data['bpi']["USD"]['rate']

        return float(price.replace(",", ""))
