from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup
import retrieve_data

app = Flask(__name__)

#Test if web app is working
@app.route('/')
def hello_world():
    return 'Hello from Flask!'

#Get current stock price for the given ticker symbol by scraping yahoo finance
def get_current_price(ticker):
    path = "https://finance.yahoo.com/quote/{0}/"
    path = path.format(ticker)
    result = requests.get(path)
    bs = BeautifulSoup(result.text, 'html.parser')
    try:
        title = bs.find('title').contents[0]
        price = bs.find('span', 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)').contents[0]
    except:
        return 'Sorry, I can\'t find that stock. Check if your ticker symbol is correct and format your text like this: ticker GOOG'
    return str(title.split(" (", 1)[0] + ': ' + price)

@app.route('/sms', methods=['GET', 'POST'])
def sms_reply():
    #Parse text message
    resp = MessagingResponse()
    body = request.values.get('Body', None)
    command = str(body).lower()
    
    if command == 'hello':
        resp.message('Hi there. My name is Spot. I\'m an sms bot that can get real-time and historical financial data for you. To get a list of commands, text \'commands\'.')
    elif command == 'commands':
        resp.message('''Commands:
            For current stock prices, text: 
            ticker {SYMBOL}
            Example: ticker GOOG
            
            More features coming soon.
            ''')
    elif 'ticker' in command:
        ticker = command[7:]
        price = get_current_price(ticker)
        resp.message(price)
    else:
        resp.message('I\'m sorry, I don\'t understand your request. Text \'hello\' for an introduction or \'commands\' for a list of commands.')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)