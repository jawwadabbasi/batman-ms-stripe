import settings

from v1.manager import Manager
from v1.stripe import Stripe

class Checkout:

	def CreateSession(user_id, price_id, email, phone, profile_status):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			user_id = str(user_id)
			price_id = str(price_id)

		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		customer = Manager.RetrieveCustomer(user_id) or Manager.CreateCustomer(user_id, email, phone)

		if not customer:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to create customer on stripe']

			return api_data
		
		if profile_status.lower() == 'draft':
			return_url = f'{settings.DOMAIN}/profile/update'
		
		else:
			return_url = f'{settings.DOMAIN}/profile/manage'
		
		checkout_session = Stripe.CreateCheckoutSession(user_id, customer, email, price_id, return_url)

		if not checkout_session:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to create checkout session']

			return api_data
		
		if checkout_session:
			api_data['ApiHttpResponse'] = 200
			api_data['ApiMessages'] += ['INFO - Request processed successfully']
			api_data['ApiResult'] = checkout_session.client_secret

			return api_data

		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] += ['ERROR - Could not create checkout session']

		return api_data