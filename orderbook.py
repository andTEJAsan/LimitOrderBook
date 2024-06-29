import random
import time
from settings import interval_from, interval_to, time_left, min_price, min_btc, max_price, max_btc


class OrderBook:
    def __init__(self):
        self.buy_data = []
        self.sell_data = []
        self.spread_data = ''
        self.buy_col_names = [
            'Index', 'Price (INR)', 'Amount (BTC)', 'Total (INR)']
        self.sell_col_names = [
            'Index', 'Price (INR)', 'Amount (BTC)', 'Total (INR)']
        self.buy_title = 'Buy Orders'
        self.sell_title = 'Sell Orders'

    def add_buy_order(self, price, amount, total):
        total = price * amount
        buy_order = [f'Buy {len(self.buy_data) + 1}',
                     price, amount, total]
        self.buy_data.append(buy_order)

    def add_sell_order(self, price, amount, total):
        total = price * amount
        sell_order = [f'Sell {len(self.sell_data) + 1}', price, amount, total]
        self.sell_data.append(sell_order)

    def calculate_spread(self):
        if not self.buy_data or not self.sell_data:
            return None
        highest_buy_price = max(float(row[1]) for row in self.buy_data)
        lowest_sell_price = min(float(row[1]) for row in self.sell_data)

        spread = round(highest_buy_price - lowest_sell_price, 2)
        return spread

    def update_spread(self):
        spread = self.calculate_spread()
        if spread is not None:
            self.spread_data = f'Spread: {spread}'

    def generate_row(self, buy_tree, sell_tree):
        start_time = time.time()
        buy_index = 1
        sell_index = 1

        while time.time() - start_time < time_left:  # Run for X amount of seconds
            print('New Generation started')
            price = round(random.uniform(min_price, max_price), 2)
            amount = round(random.uniform(min_btc, max_btc), 2)
            total = round(price * amount, 2)

            if random.choice([True, False]):
                self.add_buy_order(price, amount, total)
                buy_tree.insert("", "end", values=[
                    f'Buy {len(self.buy_data)}', price, amount, total])
                print(f'Buy order recorded: \n {self.buy_data[-1]}')
                buy_index += 1
            else:
                self.add_sell_order(price, amount, total)

                sell_tree.insert("", "end", values=[
                    f'Sell {len(self.sell_data)}', price, amount, total])
                print(f'Sell order recorded: \n {self.sell_data[-1]}')
                sell_index += 1

            self.calculate_spread()
            self.update_spread()
            print(self.spread_data)
            time.sleep(random.uniform(
                interval_from, interval_to))
