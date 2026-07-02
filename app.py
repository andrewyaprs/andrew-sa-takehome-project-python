import os
import stripe

from dotenv import load_dotenv
from flask import Flask, request, render_template

load_dotenv()

STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = Flask(__name__,
  static_url_path='',
  template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "views"),
  static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))

# Home route
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

# Checkout route
@app.route('/checkout', methods=['GET'])
def checkout():
  # Just hardcoding amounts here to avoid using a database
  item = request.args.get('item')
  title = None
  amount = None
  error = None

  if item == '1':
    title = 'The Art of Doing Science and Engineering'
    amount = 2300
  elif item == '2':
    title = 'The Making of Prince of Persia: Journals 1985-1993'
    amount = 2500
  elif item == '3':
    title = 'Working in Public: The Making and Maintenance of Open Source'
    amount = 2800
  else:
    # Included in layout view, feel free to assign error
    error = 'No item selected'

# Create a PaymentIntent for the selected item using POST /v1/payment_intents
  payment_intent = stripe.PaymentIntent.create(
    amount=amount,
    currency="usd"
  )

  return render_template('checkout.html', 
                         title=title, 
                         amount=amount, 
                         error=error,
                         client_secret=payment_intent['client_secret'],
                         publishable_key=STRIPE_PUBLISHABLE_KEY
                         )

# Success route
@app.route('/success', methods=['GET'])
def success():
  #Stripe appends PaymentIntent id to the return url on redirect, retrieving id from query string
  payment_intent_id = request.args.get('payment_intent')
  #Retrieve full PaymentIntent details from Stripe using GET /v1/payment_intents/:id
  payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

  return render_template('success.html',
                         amount = payment_intent['amount'],
                         payment_intent_id = payment_intent['id']
                         )


if __name__ == '__main__':
  app.run(port=5000, host='0.0.0.0', debug=True)