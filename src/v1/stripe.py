import stripe
import inspect
import settings

from services.logger import Logger

class Stripe:

	def CreatePaymentMethod(user_id, payment_method_token):

		try:
			payment_method = stripe.PaymentMethod.create(
				type='card',
				card={
					'token': payment_method_token
				},
				metadata={
					'UserId': user_id
				}
			)
		
			return payment_method.id
		
		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to create payment method')
			return False


	def AttachPaymentMethod(customer_id, payment_method_id):

		try:
			payment = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

			stripe.Customer.modify(customer_id, invoice_settings={'default_payment_method': payment_method_id})

			return payment
		
		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to attach payment method')
			return False
		
	def CreateCustomer(user_id, email, phone):

		try:
			return stripe.Customer.create(
				email = email, 
				phone = phone,
				metadata = {
					"UserId": user_id
				},
			)

		except Exception as e: 

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to create customer on stripe')
			return False
	
	def RetrieveCustomer(customer_id):

		try:
			return stripe.Customer.retrieve(customer_id)

		except Exception as e: 

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to retrieve customer from stripe')
			return False
		
	def DeleteCustomer(customer_id):

		try:
			stripe.Customer.delete(customer_id)

			return True

		except Exception as e: 

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to delete customer from stripe')
			return False
		
	def CreateCheckoutSession(user_id, customer_id, email, price_id, return_url):

		try:
			return stripe.checkout.Session.create(
				automatic_tax={
					'enabled': True
				},
				client_reference_id=user_id,
				customer=customer_id,
				customer_update={
					'address': 'auto'
				},
				line_items=[
					{
						'price': price_id,
						'quantity': 1,
					},
				],
				metadata={
					'Email': email,
					'UserId': user_id
				},
				mode='subscription',
				redirect_on_completion='always',
				subscription_data={
					'metadata': {
						'Email': email,
						'UserId': user_id
					}
				},
				return_url=return_url,
				ui_mode='embedded',
			)
		
		except Exception as e: 

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to create checkout session')
			return False
	
	def CreateSubscription(user_id, customer_id, email, price_id):
		try:
			
			return stripe.Subscription.create(
				customer = customer_id,
				items = [{
					'price': price_id,
				}],
				currency = 'usd',
				metadata={
					'UserId': user_id,
					'Email': email,
				}
			)
		
		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to create subscription')
			return False
		
	def RetrieveSubscription(subscription_id):

		try:
			return stripe.Subscription.retrieve(
				subscription_id
			)

		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to get subscription: ' + subscription_id)
			
			return False
		
	def CancelSubscription(subscription_id):

		try:
			return stripe.Subscription.delete(
				subscription_id
			)
		
		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to cancel subscription: ' + subscription_id)
			return False
		
	def ListPaymentMethods(customer_id, limit=1):

		try:
			return stripe.Customer.list_payment_methods(
				customer_id,
				limit=limit
			)

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to list payment methods: ' + customer_id)
			return False
		
	def GetUpcomingInvoice(customer_id):

		try:
			return stripe.Invoice.upcoming(
				customer=customer_id
			)

		except Exception as e:
			
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to get upcoming invoice: ' + customer_id)
			return False