import commandbot
import stocks


class Account(object):
    def __init__(self, user_id, starting_cash):
        self.user_id = user_id
        self.cash = starting_cash
        self.bitcoin = 0


class CoinBot(commandbot.CommandBot):
    def __init__(self, api_key, channel):
        super(CoinBot, self).__init__(api_key, channel, "cb", description="Bitcoin buying game!")

        self.leader_emoji = ":crown:"
        self.trailer_emoji = ":poop:"

        # Game data
        self.stocks = stocks.Stocks("coinbot/accounts.json")
        self.stocks.load_from_file()

        # Commands
        self.command_system.add_command("register", self.add_user, "Create an account", requires_user=True)
        self.command_system.add_command("buy", self.buy, "Buy some coin <$ amount>", requires_user=True, has_args=True)
        self.command_system.add_command("sell", self.sell, "Sell some coin <btc amount>", requires_user=True, has_args=True)
        self.command_system.add_command("price", self.check_price, "Check price")
        self.command_system.add_command("account", self.check_account, "Check your account", requires_user=True)
        self.command_system.add_command("leaderboard", self.leaderboard, "See who is best", requires_user=False)

    def add_user(self, slack_user):
        if self.stocks.add_account(slack_user.id, slack_user.name):
            self.saypush("Welcome {user}, you have been given ${cash}, don't spend it all at once!\n".format(
                user=slack_user.name, cash=self.stocks.initial_cash))
        else:
            self.saypush("You are already playing stupid\n")

    def buy(self, slack_user, args):
        if len(args) == 0:
            self.saypush("You have to give an amount in $")
            return

        buy_dollars = 0
        try:
            buy_dollars = float(args[0])
        except ValueError:
            if args[0].lower() == "all":
                buy_dollars = self.stocks.accounts[slack_user.id].cash
            else:
                self.saypush("{} is not a valid $ value".format(args[0]))
                return

        if buy_dollars <= 0:
            self.saypush("{} is not a valid $ value".format(args[0]))
            return

        result = self.stocks.buy(slack_user.id, buy_dollars)
        self.stocks.save_to_file()

        if result.error == stocks.StockReturnCodes.Good:
            self.saypush("-${} | +{} btc ({} btc transaction fee)".format(abs(result.cash), result.coin, result.transaction_fee))
        elif result.error == stocks.StockReturnCodes.NoFundsError:
            self.saypush("You don't have ${}".format(buy_dollars))
        elif result.error == stocks.StockReturnCodes.NoAccountError:
            self.saypush("Please create an account using \"cb: register\"")
        else:
            self.saypush("UNKNOWN ERROR")

    def sell(self, slack_user, args):
        if len(args) == 0:
            self.saypush("You have to give an amount in btc")
            return

        sell_btc = 0
        try:
            sell_btc = float(args[0])
        except ValueError:
            if args[0].lower() == "all":
                sell_btc = self.stocks.accounts[slack_user.id].bitcoin
            else:
                self.saypush("{} is not a valid btc value".format(args[0]))
                return

        if sell_btc <= 0:
            self.saypush("{} is not a valid btc value".format(args[0]))
            return

        result = self.stocks.sell(slack_user.id, sell_btc)
        self.stocks.save_to_file()

        if result.error == stocks.StockReturnCodes.Good:
            self.saypush("+${} | {} btc ({} btc transaction fee)".format(result.cash, result.coin, result.transaction_fee))
        elif result.error == stocks.StockReturnCodes.NoFundsError:
            self.saypush("You don't have {} btc".format(sell_btc))
        elif result.error == stocks.StockReturnCodes.NoAccountError:
            self.saypush("Please create an account using \"cb: register\"")
        else:
            self.saypush("UNKNOWN ERROR")

    def check_price(self):
        price = self.stocks.get_price_bitcoin()
        self.saypush("1 btc = ${price}".format(price=price))

    def check_account(self, slack_user):
        if slack_user.id not in self.stocks.accounts:
            self.saypush("Please create an account using \"cb: register\"")
        else:
            self.saypush(self.stocks.account_summary_string(slack_user.id))

    def leaderboard(self):
        message = "Current scores:\n"

        sorted_ids = self.stocks.sorted_user_ids()

        for k in sorted_ids:
            emoji = ""
            if k is sorted_ids[0]:
                emoji = self.leader_emoji
            elif k is sorted_ids[-1]:
                emoji = self.trailer_emoji
            message += "\t" + emoji + " " + self.stocks.account_summary_string(k) + "\n"
        self.saypush(message)
