# Stripe: Take home project - Andrew Yap

This is a submission for the Stripe SA take home assignment, built on top of the original Python boilerplate provided [here](https://github.com/marko-stripe/sa-takehome-project-python). The base application is a simple bookstore e-commerce site that is missing the payment functionality. This submission adds the integration with Stripe to allow users to:
- Select a book to purchase
- Checkout and purchase the item using Stripe Elements
- Display a confirmation of purchase to the user with the total amount of the charge and Stripe Payment Intent ID (beginning with pi_)

## Setup instructions

This demo is written in Python with the [Flask framework](https://flask.palletsprojects.com/). You'll need to retrieve a set of testmode API keys from the Stripe dashboard (you can create a free test account [here](https://dashboard.stripe.com/register)) to run this locally.

We're using the [Bootstrap](https://getbootstrap.com/docs/4.6/getting-started/introduction/) CSS framework. It's the most popular CSS framework in the world and is pretty easy to get started with — feel free to modify styles/layout if you like. 

To simplify this project, we're also not using any database here, either. Instead `app.py` includes a simple case statement to read the GET params for `item`. 

To get started, clone the repository

```
git clone https://github.com/andrewyaprs/andrew-sa-takehome-project-python && cd andrew-sa-takehome-project-python
```

Set up a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Then install the dependencies:

```
pip3 install -r requirements.txt
```

Rename `sample.env` to `.env` and populate it with your Stripe account's test API keys. 

Then run the application locally:

```
flask run
```

## Testing instructions

Navigate to [http://localhost:5000](http://localhost:5000) on your browser to view the index page.

Click on the purchase button for one of the books to be brought to the checkout page.

At the checkout page, enter an email address and the Stripe [test card number](https://docs.stripe.com/testing) of 4242 4242 4242 4242 (any future expiry and any CVC). Click the pay button.

Once redirected to the success page, you will find both the amount charged and payment ID displayed to the end user as confirmation.

Feel free to also test with other card numbers that trigger errors (e.g. 4000 0000 0000 0002 for a generic card decline), you will notice inline error messages and validation appear right on the checkout form. This is a good demonstration of how Stripe absorbs the complexity of handling these edge cases so customer's do not have to build and maintain custom error-handling logic for every scenario. Freeing up more developer resources for strategic initiatives.

## How does the solution work

This app uses Stripe's [Payment Intents API](https://docs.stripe.com/api/payment_intents?architecture-style=resources) paired with the [Payment Element](https://docs.stripe.com/payments/payment-element) UI component to collect and confirm card payments. 

**How the solution works by payment flow:**

**Step 1 - User Selects a Book**

At the home page, users are presented with various options of books for purchase. They click "Buy" on a book, triggering a GET request to '`/checkout?item=<id>`' on our server.

**Step 2 - Create a PaymentIntent**

Our server receives the request, looks up the book price, and calls Stripe's [Create PaymentIntent POST API](https://docs.stripe.com/api/payment_intents/create) to register the intended charge with Stripe.

Stripe returns a JSON payload from which our server extracts the `client_secret`

**Step 3 - Server Renders Checkout Page**

Flask embeds the `client_secret` and our `publishable_key` directly in the checkout HTML template and sends it to the browser. The secret is passed server-side into the template.

**Step 4 - Payment Element Initialises and Mounts**

Stripe.js initialises using our `publishable_key` and a Stripe Elements instance is created, scoped to this specific payment using the `client_secret`

The Stripe Payment Element is mounted to a <div> in our checkout.html where Stripe renders the card input UI in an iframe it controls, so the server never touches raw card data and ensures PCI compliance.

**Step 5 - User Submits Payment**

The customer enters their card details and clicks "Pay". This is where Stripe.js calls [stripe.confirmPayment()](https://docs.stripe.com/js/payment_intents/confirm_payment), sending the card data directly to Stripe (never through our server).

Stripe processes the payment, authorises the charge and updates Payment Intent status to succeeded.

**Step 6 - Browser redirected to confirmation**

Stripe redirects the browser to our return_url with the query params of `payment_intent` and `redirect_status`

Our server reads the payment_intent ID from the query string and then makes a GET request to Stripe to [Retrieve a PaymentIntent](https://docs.stripe.com/api/payment_intents/retrieve), confirming the charge and retrieving the full PaymentIntent. Stripe is the source of truth to confirm status is actually 'succeeded' instead of trusting the redirect itself.

**Step 7 - Confirmation Page Shown**

Server renders the confirmation template with the payment_intent ID and total amount for the customer to see their confirmed order status.

--

For a visual representation of the payment flow, kindly refer to the Excalidraw link [here](https://excalidraw.com/#json=pZKINzzpbDVCSQaP0I4vR,rHAYSHvDueb_LUKmPOTFcA)

--

**Stripe APIs used:**

**Server-side:**
- [Create a PaymentIntent](https://docs.stripe.com/api/payment_intents/create) (POST /v1/payment_intents)
- [Retrieve a PaymentIntent](https://docs.stripe.com/api/payment_intents/retrieve) (GET /v1/payment_intents/:id)

**Client-side:**
- [Initializing Stripe.js](https://docs.stripe.com/js/initializing)
- [Create an Elements Instance](https://docs.stripe.com/js/elements_object/create)
- [Confirm a PaymentIntent](https://docs.stripe.com/js/payment_intents/confirm_payment) 

## Approach & Challenges

I started by reading through the existing boilerplate end to end before writing any code to separate what was already built from what needed Stripe logic. For example:
- custom.js already handled the converting of cent amounts to formatted dollar value
- the routes that required additional work were in the 'checkout' route and the 'success route'

I searched and referenced the following Stripe documentations to get a better understanding:
- [Payments API Feature Comparison](https://docs.stripe.com/payments/online-payments#compare-features-and-availability) - to decide between Checkout Sessions API vs Payment Intents API
- [Accept a payment (Payment Intents API)](https://docs.stripe.com/payments/accept-a-payment?payment-ui=elements&api-integration=paymentintents) - to understand the overall payment flow and reference sample code
- [Payment Intents API documentation](https://docs.stripe.com/payments/accept-a-payment?payment-ui=elements&api-integration=paymentintents) - for the exact request/response shape
- [Simulate payments to test integration](https://docs.stripe.com/payments/accept-a-payment?payment-ui=elements&api-integration=paymentintents)

I also referenced YouTube videos from Stripe Developers and others to reference the thought process which helps with conceptual understanding
- [Building a custom checkout form with Stripe Elements](https://www.youtube.com/watch?v=wfjLPf_MU_s)
- [Accept a payment with the Payment Element using Python](https://www.youtube.com/watch?v=tCSbCk5j3Tk)
- [Payment Object Overview](https://www.youtube.com/watch?v=CUAY6IQcVQM&t=216s)

Once familiar with the concepts, I built my incremental code on top of the original code. Stripe's publicly available documentations were very clear, following the payments flow chart listed [here](https://docs.stripe.com/payments/accept-a-payment?payment-ui=elements&api-integration=paymentintents#web-create-intent) in the Accept a payment documentation, I was able to understand the order of the APIs being utilised and flow of data. Before wiring anything directly in the code, I tested the APIs in Postman first to confirm the request worked in isolation so it will be easier to tell apart Stripe API issues from Flask integration issues once I added it into my code. 

Challenges:
- The terminologies around the various keys/secret (publishable keys, secret keys, client secret) were initially confusing and key-exposure boundary must be very consciously managed between what belongs in the browser vs the server. I took some time to take a step back and revisit the [Stripe API keys developer resources](https://docs.stripe.com/keys) to ensure only the right exposure.
- When designing the success page, I initially considered carrying the same amount value forward into the redirect and use the payment intent id via the query param to print directly on the page. But realised it could carry a risk of spoofing or fabricated confirmation for a payment that never happened. So I decided to directly retrieve the information from Stripe using the payment intent id as a lookup key.



## Extending The Solution

Functional ways to extend the solution to help our bookstore customer scale their business across various business models and keep up with changing consumer expectations with Stripe:
1. Integrate with other 3rd party business applications using the [Stripe partner directory](https://stripe.partners/) (e.g. Hubspot for segmentation based on customer's interest)
2. Provide an add to cart experience and checkout experience
3. Embed an agentic chat experience on the site capable of recommending books to customers and directly surfacing the stripe checkout javascript in chat interface
4. Provide more payment methods by enabling "automatic_payment_methods" so the Payment Element can offer wallets and localised payment types
5. Provide refunds via the [Refunds API](google.com/url?q=https://stripe.com/docs/refunds&sa=D&source=docs&ust=1782983116522823&usg=AOvVaw2YR6RfYEE2bWjWmPi9gGcv)
6. Multi-currency/localisation, currency is currently hardcoded to "usd", for a bookstore serving multiple regions this must be dynamic.
7. Should the bookstore evolve their business model to a marketplace, consider using [Stripe Connect ](https://stripe.com/en-sg/connect)to orchestrate money movement across multiple parties

Technical ways to extend the solution:
1. Add a webhook endpoint listening for payment intent succeeded so a confirmation email can be sent the moment Stripe confirms the charge. If the user closes the browser or the network drops in the middle of the redirect, the customer still gets their confirmation via the webhook triggered email confirmation.
2. Better error handlings, currently invalid items on checkout or a missing payment_intent on success will throw 500s instead of an error banner, both should validate input and fail with proper responses.
3. Idempotency keys on PaymentIntent creation to protect against duplicate charges. If the same checkout request accidentally gets sent twice, Stripe recognises it as a repeat and reuses the original PaymentIntent so the customer cannot be charged twice
4. Store the product catalogue in a database with a product table and order table so every purchase has a persistent record beyond what's in the Stripe dashboard
5. Deploy to a hosted environment serving the web app over HTTPS with a real domain since Stripe requires HTTPS for live payments
