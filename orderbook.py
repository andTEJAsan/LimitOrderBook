import copy
import random
import time
import heapq
from settings import interval_from, interval_to, time_left, min_price, min_btc, max_price, max_btc


class OrderBook:
    def __init__(self):
        self.buy_data = []
        # we will use a max heap to store the buy order as we want the highest price at which a buyer is willing to buy
        self.sell_data = []
        self.spread_data = ''
        self.buy_col_names = [
            'Index', 'Price (INR)', 'Amount (BTC)', 'Total (INR)']
        self.sell_col_names = [
            'Index', 'Price (INR)', 'Amount (BTC)', 'Total (INR)']
        self.buy_title = 'Buy Orders'
        self.sell_title = 'Sell Orders'
        self.filled_orders = 0

    def fill_buy_order(self, price, amount):
        # This implements FIFO filling algorithm
        num_orders_filled = 0
        num_partially_filled = 0
        while(len(self.sell_data)):
            if(amount > 0):
                sell_order = heapq.heappop(self.sell_data)
                sell_amount = sell_order[2]
                sell_price = sell_order[0]
                if(sell_price > price):
                    # we cant fill this order 
                    # lets stop
                    break
                if(amount >= sell_amount):
                    amount -= sell_amount
                    sell_amount = 0
                    num_orders_filled += 1
                else:
                    sell_amount -= amount
                    amount = 0
                    num_partially_filled += 1
                    new_sell_order = (sell_price, sell_order[1], sell_amount, sell_order[3], sell_order[4])
                    heapq.heappush(self.sell_data, new_sell_order)
            else:
                break
        if(amount > 0):
            # we still have some order left. So we will add it to the buy order
            buy_order = (-price, len(self.buy_data) + 1, amount, price * amount, f'Buy {len(self.buy_data) + 1}')
            heapq.heappush(self.buy_data, buy_order)
    def fill_sell_order(self, price, amount):
        num_orders_filled = 0
        num_partially_filled = 0
        while(len(self.buy_data)):
            if(amount > 0):
                buy_order = heapq.heappop(self.buy_data)
                buy_amount = buy_order[2]
                buy_price = -buy_order[0]
                if(buy_price < price):
                    # we cant fill this order 
                    # lets stop
                    break
                if(amount >= buy_amount):
                    amount -= buy_amount
                    buy_amount = 0
                    num_orders_filled += 1
                else:
                    buy_amount -= amount
                    amount = 0
                    num_partially_filled += 1
                    new_buy_order = (-buy_price, buy_order[1], buy_amount, buy_order[3], buy_order[4])
                    heapq.heappush(self.buy_data, new_buy_order)
            else:
                break
        if(amount > 0):
            # we still have some order left. So we will add it to the sell order
            sell_order = (price, len(self.sell_data) + 1, amount, price * amount, f'Sell {len(self.sell_data) + 1}')
            heapq.heappush(self.sell_data, sell_order)
    def add_buy_order(self, price, amount, total):
        total = price * amount
        # buy_order = [f'Buy {len(self.buy_data) + 1}',
                    #  price, amount, total]
        time = len(self.buy_data) + 1
        buy_order = (-price, time , amount, total, f'Buy {time}')
        # self.buy_data.append(buy_order)
        print("Buy order recorded ", price, time, amount, total, f'Buy {time}')
        # lowest_sell_price = self.sell_data[0][0]
        self.fill_buy_order(price, amount)

    def add_sell_order(self, price, amount, total):
        total = price * amount
        # sell_order = [f'Sell {len(self.sell_data) + 1}', price, amount, total]
        time = len(self.sell_data) + 1
        sell_order = (price,time ,  amount, total, f'Sell {time}')
        print("Sell order recorded ", price, time, amount, total, f'Sell {time}')
        # self.sell_data.append(sell_order)
        self.fill_sell_order(price, amount)
        # heapq.heappush(self.sell_data, sell_order)

    def calculate_spread(self):
        if not self.buy_data or not self.sell_data:
            return None
        highest_buy_price = - self.buy_data[0][0]
        lowest_sell_price = self.sell_data[0][0]
        spread = round(lowest_sell_price - highest_buy_price, 2)
        return spread

    def update_spread(self):
        spread = self.calculate_spread()
        if spread is not None:
            self.spread_data = f'Spread: {spread}'

    def render_buy_tree(self, buy_tree):
        heapcopy = copy.deepcopy(self.buy_data)
        for item in buy_tree.get_children():
            buy_tree.delete(item)
        while heapcopy:
            item = heapq.heappop(heapcopy)
            buy_tree.insert("", "end", values=[item[4], -item[0], item[2], item[3]])      

    def render_sell_tree(self, sell_tree):
        heapcopy = copy.deepcopy(self.sell_data)
        for item in sell_tree.get_children():
            sell_tree.delete(item)
        temp_list = []
        while heapcopy:
            item = heapq.heappop(heapcopy)
            temp_list.append(item)
        for item in reversed(temp_list):
            sell_tree.insert("", "end", values=[item[4], item[0], item[2], item[3]])      
    def render_book(self, buy_tree, sell_tree):
        self.render_buy_tree(buy_tree= buy_tree)
        self.render_sell_tree(sell_tree=sell_tree)
    def generate_row(self, buy_tree, sell_tree):
        start_time = time.time()
        buy_index = 1
        sell_index = 1

        while time.time() - start_time < time_left:  # Run for X amount of seconds
            print('New Generation started')
            price = round(random.uniform(min_price, max_price), 2)
            # amount = round(random.uniform(min_btc, max_btc), 2)
            amount = random.randint(min_btc, max_btc)
            total = round(price * amount, 2)

            if random.choice([True, False]):
                self.add_buy_order(price, amount, total)
                self.render_buy_tree(buy_tree)
                buy_index += 1
            else:
                self.add_sell_order(price, amount, total)
                self.render_sell_tree(sell_tree)
                sell_index += 1
                

            self.calculate_spread()
            self.update_spread()
            print(self.spread_data)
            time.sleep(random.uniform(
                interval_from, interval_to))
