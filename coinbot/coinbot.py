import commandbot
import stocks

class Account(object):
    def __init__(self, user_id, starting_cash):
        self.user_id = user_id
        self.cash = starting_cash
        self.bitcoin = 0


class CoinBot(commandbot.CommandBot):
    def __init__(self, api_key, channel):
        super(CoinBot, self).__init__(api_key, channel, "cb", description="A bot for playing hangmanbot!")

        # Game data
        self.stocks = stocks.Stocks()

        # Commands
        self.command_system.add_command("join", self.add_user, "Create an account", requires_user=True)
        self.command_system.add_command("buy", self.buy, "Buy some coin <$ amount>", requires_user=True, has_args=True)
        self.command_system.add_command("sell", self.sell, "Sell some coin <btc amount>", requires_user=True, has_args=True)
        self.command_system.add_command("price", self.check_price, "Check price")

    def add_user(self, slack_user):
        if slack_user.id in self.user_accounts:
            self.saypush("You are already playing stupid\n")
            return
        self.user_accounts[slack_user.id] = Account(slack_user.id, self.initial_cash)
        self.saypush("Welcome {user}, you have been given ${cash}, don't spend it all at once!\n".format(user=slack_user.name, cash=self.initial_cash))

    def check_user(self, slack_user):
        if slack_user.id not in self.user_accounts:
            self.add_user(slack_user)

    def buy(self, slack_user, args):
        self.check_user(slack_user)

        if len(args) == 0:
            self.saypush("You have to give an amount in $")
            return

        account = self.user_accounts[slack_user.id]

        buy_dollars = 0
        try:
            buy_dollars = float(args[0])
        except ValueError:
            if args[0].lower() == "all":
                buy_dollars = account.cash
            else:
                self.saypush("{} is not a valid $ value".format(args[0]))
                return

        if buy_dollars <= 0:
            self.saypush("{} is not a valid $ value".format(args[0]))
            return

            buy_dollars = round(buy_dollars, 2)

        if buy_dollars > account.cash:
            self.saypush("You don't have {}".format(buy_dollars))
            return

        btc_bought = buy_dollars / self.stocks.get_price_bitcoin()
        btc_bought /= 1 + self.transaction_fee

        self.saypush("Buying {} btc for ${}, including a {}% transaction fee".format(btc_bought, buy_dollars, 100 * self.transaction_fee))
        account.cash -= buy_dollars
        account.bitcoin += btc_bought


    def sell(self, slack_user, args):
        self.check_user(slack_user)

        self.check_user(slack_user)

        if len(args) == 0:
            self.saypush("You have to give an amount in $")
            return

        account = self.user_accounts[slack_user.id]

        sell_btc = 0
        try:
            sell_btc = float(args[0])
        except ValueError:
            if args[0].lower() == "all":
                sell_btc = account.bitcoin
            else:
                self.saypush("{} is not a valid btc value".format(args[0]))
                return

        if sell_btc <= 0:
            self.saypush("{} is not a valid btc value".format(args[0]))
            return

        if sell_btc > account.bitcoin:
            self.saypush("You don't have {}".format(sell_btc))
            return

        dollars_received = sell_btc / self.stocks.get_price_bitcoin()
        dollars_received /= 1 + self.transaction_fee

        self.saypush("Selling {} btc for ${}, including a {}% transaction fee".format(sell_btc, dollars_received, 100 * self.transaction_fee))
        account.cash += dollars_received
        account.bitcoin -= sell_btc

    def check_price(self):
        price = self.stocks.get_price_bitcoin()
        self.saypush("1 btc = ${price}".format(price=price))

