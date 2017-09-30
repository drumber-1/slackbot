import utils
import json
import os


class StockReturnCodes:
    Good, NoFundsError, NoAccountError, MiscError = range(4)


class Account(object):
    def __init__(self, name, starting_cash, data=None):
        self.name = name
        self.cash = starting_cash
        self.bitcoin = 0
        if not data == None:
            self.load(data)

    def load(self, data):
        self.name = data["name"]
        self.cash = data["cash"]
        self.bitcoin = data["bitcoin"]


class Transaction(object):
    def __init__(self, cash, coin, fee, code):
        self.cash = cash
        self.coin = coin
        self.error = code
        self.transaction_fee = fee


class Stocks(object):

    def __init__(self, save_file):
        self.accounts = {}
        self.transaction_fee_fraction = 0.03
        self.initial_cash = 100

        self.save_file = save_file

    def add_account(self, id, name):
        if id in self.accounts:
            return False
        else:
            self.accounts[id] = Account(name, self.initial_cash)
            return True

    def buy(self, id, cash_value):
        if id not in self.accounts:
            return Transaction(0, 0, 0, StockReturnCodes.NoAccountError)
        account = self.accounts[id]
        if cash_value > account.cash:
            return Transaction(0, 0, 0, StockReturnCodes.NoFundsError)
        cash_value = round(cash_value, 2)
        btc_value = cash_value / self.get_price_bitcoin()
        transaction_fee_btc = btc_value * self.transaction_fee_fraction

        account.cash -= cash_value
        account.bitcoin += btc_value - transaction_fee_btc
        return Transaction(-cash_value, btc_value - transaction_fee_btc, transaction_fee_btc, StockReturnCodes.Good)

    def sell(self, id, btc_value):
        if id not in self.accounts:
            return Transaction(0, 0, StockReturnCodes.NoAccountError)
        account = self.accounts[id]
        transaction_fee_btc = btc_value * self.transaction_fee_fraction
        if btc_value > account.bitcoin:
            return Transaction(0, 0, 0, StockReturnCodes.NoFundsError)
        cash_value = (btc_value - transaction_fee_btc) * self.get_price_bitcoin()
        cash_value = round(cash_value, 2)

        account.cash += cash_value
        account.bitcoin -= btc_value
        return Transaction(cash_value, -btc_value, transaction_fee_btc, StockReturnCodes.Good)

    def get_price_bitcoin(self):
        url = 'https://api.coindesk.com/v1/bpi/currentprice/{}.json'.format("USD")
        data = utils.get_url_response(url)
        price = data['bpi']["USD"]['rate']

        return float(price.replace(",", ""))

    def save_to_file(self):
        fout = open(self.save_file, 'w')
        data = {}
        for key, value in self.accounts.items():
            data[key] = value.__dict__
        json.dump(data, fout, indent=4)

    def load_from_file(self):
        if not os.path.isfile(self.save_file):
            return

        fin = open(self.save_file, 'r')
        data = json.load(fin)
        for key, value in data.items():
            self.accounts[key] = Account("blank", 0, data=value)

    def sorted_user_ids(self):
        sorted_ids = sorted(self.accounts.keys(), key=self.account_worth, reverse=True)
        return sorted_ids

    def account_worth(self, id):
        return self.accounts[id].cash + self.accounts[id].bitcoin * self.get_price_bitcoin()

    def account_summary_string(self, id):
        return "{} : ${} (${} + {} btc)".format(self.accounts[id].name, self.account_worth(id), self.accounts[id].cash, self.accounts[id].bitcoin)


