// Initialise stripe.js with publishable key and create an instance of the Stripe object
const stripe = Stripe(PUBLISHABLE_KEY);

// Set up Elements tied to this specific PaymentIntent to use in checkout form
const elements = stripe.elements({clientSecret: CLIENT_SECRET})

// Create and mount the payment element into DOM node in checkout.html
const paymentElementOptions = { layout: 'accordion'};
const paymentElement = elements.create('payment', paymentElementOptions);
paymentElement.mount('#payment-element');

const form = document.getElementById('payment-form');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  // Confirm the payment using details collected by Payment Element
  const {error} = await stripe.confirmPayment({
    elements,
    confirmParams: {
      return_url: 'http://localhost:5000/success',
    },
  });

  if (error) {
    const messageContainer = document.querySelector('#error-message');
    messageContainer.textContent = error.message;
  } else {
  }
});