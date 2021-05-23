from alpha_vantage.timeseries import TimeSeries
import sqlite3
from os import path
import os
import math

from datetime import date
from datetime import datetime
import re
# DO CAN BUY
canbuy = 1


api_key = 'RNZPXZ6Q9FEFMEHM'

#making the database




#defining stock prices at that time

def price(stock_name):

    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=stock_name, interval='1min', outputsize='compact')
    d = data.iat[0, 3]

    #logging the time and date

    global buy_time
    now = datetime.now()
    buy_time = str(now.strftime("%H:%M:%S"))

    global buy_date
    buy_date = date.today()

    return d

def balance():
    connect = sqlite3.connect('balance.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM balance")
    value = (cursor.fetchone())
    global balance
    balance = ''.join(map(str, value))
    connect.commit()
    connect.close()
    return balance


def starting_balance():
    connect = sqlite3.connect('settings.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM settings")
    value = cursor.fetchone()
    starting_balance = ''.join(map(str, value))
    connect.commit()
    connect.close()
    return starting_balance

#interactive board
def interact():
    option = int(input('What would you like to do\n'
                       '1. Buy a stock\n'
                       '2. Sell a stock\n'
                       '3. Check balance\n'
                       '4. Check Stocks\n'
                       '5. Quit\n'
                       '6. Reset Account\n'
                       '7. Settings\n'
                       ))


    if option == 1:

        # calculating balance
        connect = sqlite3.connect('balance.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM balance")

        value = (cursor.fetchone())
        balance = ''.join(map(str, value))
        buy_stock = input('Please type the NASDAQ code of the stock you would like to buy\n')
        bstock_data = price(buy_stock)

        maximum = math.floor(float(balance) / float(bstock_data))
        connect.commit()
        connect.close()



        print('Here are some statistics of the stock {0}'.format(buy_stock))
        print('Price of stock: {}'.format(bstock_data))
        print('Maximum amount you can buy: {}'.format(maximum))

        how_many = int(input('Please type the number of stocks you would like to buy\n'))

        if how_many > maximum:
            print('You are not able to afford that many stocks')

        else:
            print('\nPurchasing {} {} stocks'.format(how_many, buy_stock))

            connect = sqlite3.connect('stock_info.db')
            cursor = connect.cursor()

            cursor.execute("SELECT * FROM stock_prices WHERE company = ?", (buy_stock,))
            if not cursor.fetchall():
                sql = "INSERT INTO stock_prices (company, date, time, current_price, how_many) VALUES ('{0}', '{1}', '{2}', {3}, {4})".format(
                    buy_stock, buy_date, buy_time, bstock_data, how_many)

                cursor.execute(sql)
                connect.commit()
                connect.close()
            else:
                cursor.execute("UPDATE stock_prices SET how_many = how_many + ?", (how_many,))
                connect.commit()
                connect.close()

            print(
                'Purcahse complete you bought a total of {0} {1} stocks for {2} each'.format(how_many, buy_stock,
                                                                                             bstock_data))

            new_balance = float(balance) - float(how_many * bstock_data)
            connect = sqlite3.connect('balance.db')
            cursor = connect.cursor()
            cursor.execute("DELETE FROM balance")
            sql = "INSERT INTO balance (money) VALUES ({})".format(new_balance)
            cursor.execute(sql)
            connect.commit()
            connect.close()
            print('Your new balance is {}\n'.format(new_balance))

            interact()

    elif option == 2:
        connect = sqlite3.connect('stock_info.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM stock_prices")
        stock_list = (cursor.fetchall())
        connect.commit()
        connect.close()

        if len(stock_list) == 0:
            print('You own 0 Stocks')
            interact()

        else:
            connect = sqlite3.connect('stock_info.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM stock_prices")

            stock_list = cursor.fetchone()
            while stock_list != None:
                if stock_list[5] == 0:
                    cursor.execute("DELETE FROM stock_prices WHERE id={}".format(stock_list[0]))
                stock_list = cursor.fetchone()
            connect.commit()
            connect.close()

            connect = sqlite3.connect('stock_info.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM stock_prices")
            stock_list = (cursor.fetchall())
            connect.commit()
            connect.close()
            for x in range(0, len(stock_list)):
                dstock_list = str(stock_list[x])
                estock_list = re.sub('[\'(),]', '', dstock_list)
                stock = list(estock_list.split(" "))
                print('{0}, Current price: {1} with {2} shares'.format(stock[1], stock[4], stock[5]))


            sell_stock = input('Please type the NASDAQ code of the stock you would like to sell\n')

            if sell_stock in stock :
                sell_how_many = int(input('How many of the stock would you like to sell\n'))
                if sell_how_many > int(stock[5]):
                    print('You dont own that many stocks')
                else:
                    connect = sqlite3.connect('stock_info.db')
                    cursor = connect.cursor()

                    sell_price = price(sell_stock)
                    gained_money = int(sell_price) * sell_how_many
                    now_how_many = int(stock[5]) - sell_how_many

                    cursor.execute("UPDATE stock_prices SET how_many={0} WHERE id={1}".format(now_how_many, len(stock_list)))

                    connect.commit()
                    connect.close()

                    connect = sqlite3.connect('balance.db')
                    cursor = connect.cursor()
                    cursor.execute("SELECT * FROM balance")
                    value = (cursor.fetchone())
                    balance = ''.join(map(str, value))

                    sell_balance = float(balance) + float(gained_money)
                    cursor.execute("DELETE FROM balance")
                    sqls = "INSERT INTO balance (money) VALUES ({})".format(sell_balance)
                    cursor.execute(sqls)
                    connect.commit()
                    connect.close()
                    print('Your new balance is {}\n'.format(sell_balance))

                    interact()




            else:
                print('You do not own that stock')

    elif option == 3:
        connect = sqlite3.connect('balance.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM balance")
        value = (cursor.fetchone())
        balance = ''.join(map(str, value))
        connect.commit()
        connect.close()
        print(balance)

        interact()


    elif option == 4:
        connect = sqlite3.connect('stock_info.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM stock_prices")
        stock_list = (cursor.fetchall())
        connect.commit()
        connect.close()
        if len(stock_list) == 0:
                print('You own 0 Stocks')
                interact()

        else:
            connect = sqlite3.connect('stock_info.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM stock_prices")
            print(cursor.fetchall())

            connect.commit()
            connect.close()



    elif option == 5:
        print('Your data has been saved')
        exit()

    elif option == 6:
        reset = input('Are you sure you would like to reset your account?\n')
        if reset == 'yes':
            os.remove("stock_info.db")
            os.remove("balance.db")
            print('Your account was reset')
            print('Note; Your settings have not been reset')
            exit()


        elif reset == 'no':
            print('reset canceled')
            interact()

    elif option == 7:
        setting = int(input('Please select an option\n'
                            '1. Change Starting Balance\n'
                            '2. Add money to your account\n'
                            '3. Remove money from an account\n'
                            '4. Reset Settings\n'
                            ))

        if setting == 1:
            connect = sqlite3.connect('settings.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM settings")
            value = cursor.fetchone()
            starting_balance = ''.join(map(str, value))
            connect.commit()
            connect.close()

            print('The current starting balance is {}'.format(starting_balance))
            new_starting_bal = input('What would you like to change the starting balance to?\n')
            if new_starting_bal.isnumeric():
                connect = sqlite3.connect('settings.db')
                cursor = connect.cursor()
                cursor.execute("DELETE FROM settings")
                sqls = "INSERT INTO settings (start_balance) VALUES ({})".format(float(new_starting_bal))
                cursor.execute(sqls)
                connect.commit()
                connect.close()
                print('The starting value has been changed to {}'.format(new_starting_bal))
                interact()
            else:
                print('Inputted value is not a number')

                interact()

        if setting == 2:
            connect = sqlite3.connect('balance.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM balance")
            value = (cursor.fetchone())
            balance = ''.join(map(str, value))
            connect.commit()
            connect.close()
            print('Your current balance is {}'.format(balance))
            increase = input('How much would you like to increase your balance by\n')
            if increase.isnumeric():
                increase_total = float(balance) + float(increase)
                connect = sqlite3.connect('balance.db')
                cursor = connect.cursor()
                cursor.execute("DELETE FROM balance")
                sqls = "INSERT INTO balance (money) VALUES ({})".format(increase_total)
                cursor.execute(sqls)
                connect.commit()
                connect.close()
                print('Your new balance is {}\n'.format(increase_total))

                interact()
            else:
                print('Inputted value is not a number')

                interact()

        if setting == 3:
            connect = sqlite3.connect('balance.db')
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM balance")
            value = (cursor.fetchone())
            balance = ''.join(map(str, value))
            connect.commit()
            connect.close()
            print('Your current balance is {}'.format(balance))
            decrease = input('How much would you like to decrease from your balance\n')
            if decrease.isnumeric():

                decrease_total = float(balance) - float(decrease)
                connect = sqlite3.connect('balance.db')
                cursor = connect.cursor()
                cursor.execute("DELETE FROM balance")
                sqls = "INSERT INTO balance (money) VALUES ({})".format(decrease_total)
                cursor.execute(sqls)
                connect.commit()
                connect.close()
                print('Your new balance is {}\n'.format(decrease_total))
                interact()
            else:
                print('Inputted value is not a number')

                interact()


        if setting == 4:
            reset_settings = str(input('Are you sure you would like to reset your settings\n'))

            if reset_settings == 'yes':
                os.remove('settings.db')
                print('Settings reset')

            if reset_settings == 'no':
                print('Reset canceled')
                interact()

            else:
                print('Invalid Option')
                print('Reset canceled')
                interact()




        else:
            print('Please select a valid option')




if __name__ == "__main__":


    if path.exists("settings.db"):
        print('')

    else:
        connect = sqlite3.connect('settings.db')
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE settings (
                start_balance real
            )""")
        cursor.execute("INSERT INTO settings VALUES ({0})".format(50000))
        connect.commit()
        connect.close()
        print(balance)


    if path.exists("balance.db"):
        print('')

    else:

        connect = sqlite3.connect('settings.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM settings")
        value = cursor.fetchone()
        starting_balance = ''.join(map(str, value))

        connect.commit()
        connect.close()

        connect = sqlite3.connect('balance.db')
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE balance (
                money real
            )""")
        cursor.execute("INSERT INTO balance (money) VALUES ({0})".format(starting_balance))

        connect.commit()
        connect.close()

        connect = sqlite3.connect('stock_info.db')
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company text,
            date text,
            time text,
            current_price real,
            how_many INTEGER
        )""")

        connect.commit()
        connect.close()


interact()



