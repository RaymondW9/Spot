from flask import Flask, request, redirect, render_template
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup
import retrieve_data

app = Flask(__name__)

#Home page with ticker lookup
@app.route('/')
def hello_world():
    return render_template('search_ticker.html')

@app.route('/search')
def search():

    name = request.args.get('name')
    stock = get_current_price(name)[1]
    price = get_current_price(name)[2]

    return render_template('stock_price.html', stock=stock, price=price)

#Get current stock price for the given ticker symbol
def get_current_price(ticker):
    path = "https://finance.yahoo.com/quote/{0}/"
    path = path.format(ticker)
    result = requests.get(path)
    bs = BeautifulSoup(result.text, 'html.parser')
    try:
        title = bs.find('title').contents[0]
        stock = title.split(" (", 1)[0]
        price = bs.find('span', 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)').contents[0]
    except:
        return 'Sorry, I can\'t find that stock. Check if your ticker symbol is correct and format your text like this: \nticker GOOG'
    return [str(stock + ': ' + price), stock, price]

@app.route('/sms', methods=['GET', 'POST'])
def sms_reply():
    resp = MessagingResponse()
    body = request.values.get('Body', None)
    command = str(body).lower()

    if command == 'hello' or command == 'hi':
        resp.message('Hi there. My name is Spot. I\'m an sms bot that can get real-time and historical financial data for you. To get a list of commands, text \'commands\'.')
    elif command == 'commands':
        resp.message('''Commands: \n
        --------------------\nFor current stock prices, text: \nticker {SYMBOL} \nExample: ticker GOOG
        --------------------
        More features coming soon.''')
    elif 'ticker' in command:
        ticker = command[7:]
        price = get_current_price(ticker)[0]
        resp.message(price)
    else:
        resp.message('I\'m sorry, I don\'t understand your request. Text \'hello\' for an introduction or \'commands\' for a list of commands.')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)