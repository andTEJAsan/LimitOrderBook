from orderbook import OrderBook
import tkinter as tk
from tkinter import ttk
import threading
import time
from settings import time_left

order_book = OrderBook()


simulation_thread = None


def generate_row(buy_tree, sell_tree):
    order_book.generate_row(buy_tree, sell_tree)


def highlight_highest_buy_price():
    while not simulation_stopped:
        highest_price = 0
        highest_index = 0

        for item in buy_tree.get_children():
            # price is located in column index 1
            price = float(buy_tree.item(item, 'values')[1])
            if price > highest_price:
                highest_price = price
                highest_index = item
        if highest_index:
            buy_tree.selection_set(highest_index)

            # Scroll to the highlighted row
            buy_tree.see(highest_index)

            # Calculate the fraction for centering the selected item
            fraction = (buy_tree.index(highest_index) + 1) / \
                len(buy_tree.get_children())

            # Center the selected item in the TreeView
            buy_tree.yview_moveto(fraction)

            # Sleep for X seconds before checking again
            time.sleep(0.5)


def highlight_lowest_sell_price():
    while not simulation_stopped:
        lowest_sell_price = float('inf')
        lowest_sell_index = None

        # Iterate through sell_tree to find lowest price
        for item in sell_tree.get_children():
            price = float(sell_tree.item(item, 'values')[1])
            if price < lowest_sell_price:
                lowest_sell_price = price
                lowest_sell_index = item

        # Highlight lowest sell price
        if lowest_sell_index:
            sell_tree.selection_set(lowest_sell_index)

            # Scroll to the highlighted row
            sell_tree.see(lowest_sell_index)

            # calculate the fraction for centering selected item
            fraction = (sell_tree.index(lowest_sell_index) +
                        1 / len(sell_tree.get_children()))
            # Center the selected item
            sell_tree.yview_moveto(fraction)

            # Sleep for X seconds before checking again
            time.sleep(0.5)


def update_spread_label():
    spread = order_book.spread_data
    if spread is not None:
        spread_label.config(text=spread)
    root.after(2000, update_spread_label)


def start_simulation():
    global simulation_thread, simulation_stopped
    simulation_stopped = False
    print(f'Simulation Started, it will run for {time_left} seconds.')
    simulation_thread = threading.Thread(
        target=generate_row, args=(buy_tree, sell_tree))
    print('System check: threading.Thread is being invoked.')
    simulation_thread.daemon = True
    simulation_thread.start()

    # Start buy highlighting thread
    buy_highlight_thread = threading.Thread(target=highlight_highest_buy_price)
    buy_highlight_thread.daemon = True
    buy_highlight_thread.start()

    # Start sell highlighting thread
    sell_highlight_thread = threading.Thread(
        target=highlight_lowest_sell_price)
    sell_highlight_thread.daemon = True
    sell_highlight_thread.start()

    # disable button whilst running sim
    start_sim_button.config(state=tk.DISABLED)

    def enable_start_sim_button():
        global simulation_stopped
        simulation_stopped = True
        start_sim_button.config(state=tk.NORMAL)

    # re-enable start button
    root.after((time_left * 1000), enable_start_sim_button)


# Create the main window
root = tk.Tk()
root.title('Real-time Orderbook Simulation')

button_frame = ttk.Frame(root)
button_frame.pack(side='top', anchor='ne', padx=10, pady=10)

start_sim_button = ttk.Button(
    button_frame, text='Start Simulation', command=start_simulation)
start_sim_button.pack(side='top', anchor='ne', padx=10, pady=10)
# Simulation Label
sim_label = ttk.Label(button_frame,
                      text=f'Simulation will run for {time_left} seconds.')
sim_label.pack(side='top', anchor='ne', padx=10, pady=10)

# Create frame for buy order table
buy_frame = ttk.Labelframe(root, text='Buy Orders')
buy_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create a TreeView widget for the buy orders table
buy_tree = ttk.Treeview(buy_frame, columns=(
    order_book.buy_col_names), style='Buy.Treeview')
buy_tree.heading('#1', text='Order Index')
buy_tree.heading('#2', text='Price (GBP)')
buy_tree.heading('#3', text='Amount (BTC)')
buy_tree.heading('#4', text='Total (GBP)')
buy_tree.pack(fill='both', expand=True)

# Create spread frame
spread_frame = ttk.Frame(root)
spread_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create Spread Label
spread_label = ttk.Label(buy_frame, text='Spread: ')
spread_label.pack()

spread_frame.pack(fill='both', expand='True')
update_spread_label()


# Create a frame for sell order table
sell_frame = ttk.Labelframe(root, text='Sell Orders')
sell_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create a TreeView widget for the sell orders table
sell_tree = ttk.Treeview(sell_frame, columns=(
    order_book.sell_col_names), style='Sell.Treeview')
sell_tree.heading('#1', text='Order Index')
sell_tree.heading('#2', text='Price (GBP)')
sell_tree.heading('#3', text='Amount (BTC)')
sell_tree.heading('#4', text='Total (GBP)')
sell_tree.pack(fill='both', expand=True)

style = ttk.Style()

# configure buy treeview style
style.configure("Buy.Treeview", background='#FFFFFF',
                foreground='#000000', fieldbackground='#FFFFFF')
# customise colour for selected items in Buy tree
style.map('Buy.Treeview', background=[
          ('selected', '#00cc0a')], foreground=[('selected', '#ffffff')])

# configure sell treeview style
style.configure('Sell.Treeview', background='#FFFFFF',
                foreground='#000000', fieldbackground='#FFFFFF')
# customise colour for selected items in Sell tree
style.map('Sell.Treeview', background=[
          ('selected', '#cf0000')], foreground=[('selected', '#ffffff')])
root.mainloop()
