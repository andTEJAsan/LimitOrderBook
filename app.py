from orderbook import OrderBook
import tkinter as tk
from tkinter import ttk, Label, Entry, StringVar, messagebox
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
root.title('Market Making Order Book Simulation')

# Creating data input buttons and fields

# StringVar() is used to get the input from the entry widget
# price_value = StringVar()
# price_entry = Entry(root, textvariable=price_value)
# price_entry.pack()

# amount_label = Label(root, text="Amount:")
# amount_label.pack()

# amount_value = StringVar()
# amount_entry = Entry(root, textvariable=amount_value)
# amount_entry.pack()

# button_frame = ttk.Frame(root)
# button_frame.pack(side='top', anchor='ne', padx=10, pady=10)

# price_label = ttk.Label(button_frame, text="Price:")
# price_label.pack(side='top', anchor='nw', padx=10, pady=10)
# price_value = StringVar()
# price_entry = ttk.Entry(button_frame, textvariable=price_value)
# price_entry.pack(side='top', anchor='nw', padx=10, pady=5)


# start_sim_button = ttk.Button(
#     button_frame, text='Start Simulation', command=start_simulation)
# start_sim_button.pack(side='top', anchor='ne', padx=10, pady=10)
# # Simulation Label
# sim_label = ttk.Label(button_frame,
#                       text=f'Simulation will run for {time_left} seconds.')
# sim_label.pack(side='top', anchor='ne', padx=10, pady=10)
button_frame = ttk.Frame(root)
button_frame.pack(side='top', fill='x', expand=True, padx=10, pady=10)

# Configure the grid layout in the button_frame to use all available space
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)
button_frame.columnconfigure(2, weight=1)
button_frame.columnconfigure(3, weight=1)

# Place the price label and entry on the left side (first column)
price_label = ttk.Label(button_frame, text="Price:")
price_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

price_value = StringVar()
price_entry = ttk.Entry(button_frame, textvariable=price_value)
price_entry.grid(row=1, column=0, sticky='w', padx=10, pady=5)
# Place the amount label and entry on the left side (second column)
amount_label = ttk.Label(button_frame, text="Amount:")
amount_label.grid(row=0, column=1, sticky='w', padx=10, pady=10)
amount_value = StringVar()
amount_entry = ttk.Entry(button_frame, textvariable=amount_value)
amount_entry.grid(row=1, column=1, sticky='w', padx=10, pady=5)




def buy_handler():
    try:
        price = float(price_value.get())
        amount = int(float(amount_value.get()))
        order_book.add_buy_order(price, amount, price * amount)
        # empty the entry fields
    except ValueError:
        # print('Invalid input. Please enter a valid number.')
        messagebox.showerror('Invalid Input', 'Please enter a valid number.')
        price_value.set('')
        amount_value.set('')
    order_book.render_book(buy_tree, sell_tree)
    # update the buy tree
def sell_handler():
    try:
        price = float(price_value.get())
        amount = int(float(amount_value.get()))
        order_book.add_sell_order(price, amount, price * amount)
        # empty the entry fields
    except ValueError:
        messagebox.showerror('Invalid Input', 'Please enter a valid number.')
        price_value.set('')
        amount_value.set('')
    order_book.render_book(buy_tree, sell_tree)
buy_button = ttk.Button(button_frame, text='Buy', command=buy_handler)
sell_button = ttk.Button(button_frame, text='Sell', command=sell_handler)
buy_button.grid(row=1, column=2, sticky='w', padx=10, pady=10)
sell_button.grid(row=0, column=2, sticky='w', padx=10, pady=10)

# Adjust the placement of the start simulation button and simulation label
# Assuming you want them on the right, you can place them in the second column
start_sim_button = ttk.Button(button_frame, text='Start Simulation', command=start_simulation)
start_sim_button.grid(row=0, column=3, sticky='e', padx=10, pady=10)

sim_label = ttk.Label(button_frame, text=f'Simulation will run for {time_left} seconds.')
sim_label.grid(row=1, column=3, sticky='e', padx=10, pady=10)

# Create a frame for sell order table
sell_frame = ttk.Labelframe(root, text='Sell Orders')
sell_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create a TreeView widget for the sell orders table
sell_tree = ttk.Treeview(sell_frame, columns=(
    order_book.sell_col_names), style='Sell.Treeview')
sell_tree.heading('#1', text='Order Index')
sell_tree.heading('#2', text='Price (INR)')
sell_tree.heading('#3', text='Amount (BTC)')
sell_tree.heading('#4', text='Total (INR)')
sell_tree.pack(fill='both', expand=True)
# Create spread frame
spread_frame = ttk.Frame(root)
spread_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create Spread Label
spread_label = ttk.Label(sell_frame, text='Spread: ')
spread_label.pack()

spread_frame.pack(fill='both', expand='True')
update_spread_label()

# Create frame for buy order table
buy_frame = ttk.Labelframe(root, text='Buy Orders')
buy_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create a TreeView widget for the buy orders table
buy_tree = ttk.Treeview(buy_frame, columns=(
    order_book.buy_col_names), style='Buy.Treeview')
buy_tree.heading('#1', text='Order Index')
buy_tree.heading('#2', text='Price (INR)')
buy_tree.heading('#3', text='Amount (BTC)')
buy_tree.heading('#4', text='Total (INR)')
buy_tree.pack(fill='both', expand=True)


style = ttk.Style()

# configure sell treeview style
style.configure('Sell.Treeview', background='#FFFFFF',
                foreground='#000000', fieldbackground='#FFFFFF')
# customise colour for selected items in Sell tree
style.map('Sell.Treeview', background=[
          ('selected', '#cf0000')], foreground=[('selected', '#ffffff')])

# configure buy treeview style
style.configure("Buy.Treeview", background='#FFFFFF',
                foreground='#000000', fieldbackground='#FFFFFF')
# customise colour for selected items in Buy tree
style.map('Buy.Treeview', background=[
          ('selected', '#00cc0a')], foreground=[('selected', '#ffffff')])

root.mainloop()
