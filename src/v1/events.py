import json
import inspect
import concurrent.futures

from includes.common import Common
from includes.db import Db
from services.broadcast import Broadcast
from services.users import Users
from services.logger import Logger

class Events:
	
	def Process(event):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		if event.get('type') is None:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ["INFO - Invalid arguments"]

			return api_data

		if event['type'] == 'invoice.paid':
			return Events.PaymentSuccess(event, 'success', 'payment-success')

		if event['type'] == 'invoice.payment_failed':
			return Events.PaymentFailed(event, 'failed', 'payment-failed')

		if event['type'] == 'customer.subscription.created':
			return Events.CustomerSubscriptionCreated(event)

		if event['type'] == 'customer.subscription.updated':
			return Events.CustomerSubscriptionUpdated(event)

		if event['type'] == 'customer.subscription.deleted':
			return Events.CustomerSubscriptionDeleted(event)

		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ["INFO - Request processed successfully"]

		return api_data
	
	def PaymentSuccess(event, status, purpose):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		
		event_data = Events.ExtractInvoiceData(event)

		if not event_data:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ["ERROR - Failed to extract invoice data"]

			return api_data
		
		subscription_updated = Users.UpdateSubscription(event_data.get('user_id'), event_data.get('description'))

		if not subscription_updated:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to update subscription']

			return api_data
  
		receipt_id = Common.GenerateReceiptNumber()

		query = """
			REPLACE INTO invoices
			SET invoice_id = %s,
				receipt_id = %s,
				user_id = %s,
				customer_id = %s,
				subscription_id = %s,
				plan_id = %s,
				product_id = %s,
				currency = %s,
				billing_interval = %s,
				event_type = %s,
				description = %s,
				amount = %s,
				amount_paid = %s,
				status = %s,
				invoice_data = %s,
				period_start = %s,
				period_end = %s,
				date = %s
		"""

		inputs = (
			event_data.get('invoice_id'),
			receipt_id,
			event_data.get('user_id'),
			event_data.get('customer_id'),
			event_data.get('subscription_id'),
			event_data.get('plan_id'),
			event_data.get('product_id'),
			event_data.get('currency'),
			event_data.get('billing_interval'),
			event_data.get('event_type'),
			event_data.get('description'),
			event_data.get('amount'),
			event_data.get('amount_paid'),
			status,
			json.dumps(event_data.get('invoice_data')),
			str(event_data.get('period_start')),
			str(event_data.get('period_end')),
			str(Common.Datetime())
		)

		meta = {
			'Description': event_data.get('description').title(),
			'Amount': str(event_data.get('amount')),
			'AmountPaid': str(event_data.get('amount_paid')),
			'Currency': str(event_data.get('currency')).upper(),
			'Taxes': Common.CalculateTax(event_data.get('amount_paid', 0), event_data.get('amount', 0)),
			"PeriodStart": str(event_data.get('period_start')),
			"PeriodEnd": str(event_data.get('period_end')),
			"ReceiptNumber": receipt_id
		}
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(Db.ExecuteQuery,query,inputs,True)
			executor.submit(Broadcast.SendEmail,event_data.get('email'),purpose,meta)

		api_data['ApiHttpResponse'] = 201
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data

	def PaymentFailed(event, status, purpose):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		
		event_data = Events.ExtractInvoiceData(event)

		if not event_data:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ["ERROR - Failed to extract invoice data"]

			return api_data
		
		subscription_updated = Users.UpdateSubscription(event_data.get('user_id'), 'free')

		if not subscription_updated:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to update subscription']

			return api_data

		query = """
			REPLACE INTO invoices
			SET invoice_id = %s,
				user_id = %s,
				customer_id = %s,
				subscription_id = %s,
				plan_id = %s,
				product_id = %s,
				currency = %s,
				billing_interval = %s,
				event_type = %s,
				description = %s,
				amount = %s,
				amount_paid = %s,
				status = %s,
				invoice_data = %s,
				period_start = %s,
				period_end = %s,
				date = %s
		"""

		inputs = (
			event_data.get('invoice_id'),
			event_data.get('user_id'),
			event_data.get('customer_id'),
			event_data.get('subscription_id'),
			event_data.get('plan_id'),
			event_data.get('product_id'),
			event_data.get('currency'),
			event_data.get('billing_interval'),
			event_data.get('event_type'),
			event_data.get('description'),
			event_data.get('amount'),
			event_data.get('amount_paid'),
			status,
			json.dumps(event_data.get('invoice_data')),
			str(event_data.get('period_start')),
			str(event_data.get('period_end')),
			str(Common.Datetime())
		)
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(Db.ExecuteQuery,query,inputs,True)
			executor.submit(Broadcast.SendEmail,event_data.get('email'),purpose)

		api_data['ApiHttpResponse'] = 201
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data

	def CustomerSubscriptionCreated(event):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		
		event_data = Events.ExtractSubscriptionData(event)

		if not event_data:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ["ERROR - Failed to extract subscription data"]

			return api_data

		query = """
			REPLACE INTO subscriptions
			SET subscription_id = %s,
				user_id = %s,
				customer_id = %s,
				plan_id = %s,
				product_id = %s,
				event_type = %s,
				billing_interval = %s,
				amount = %s,
				currency = %s,
				status = %s,
				subscription_data = %s,
				period_start = %s, 
				period_end = %s,
				last_updated = %s,
				date = %s
		"""

		inputs = (
			event_data.get('subscription_id'),
			event_data.get('user_id'),
			event_data.get('customer_id'),
			event_data.get('plan_id'),
			event_data.get('product_id'),
			event_data.get('event_type'),
			event_data.get('billing_interval'),
			event_data.get('amount'),
			event_data.get('currency'),
			event_data.get('status'),
			json.dumps(event_data.get('subscription_data')),
			event_data.get('period_start'),
			event_data.get('period_end'),
			str(Common.Datetime()),
			str(Common.Datetime())
		)

		if Db.ExecuteQuery(query,inputs,True):
			api_data['ApiHttpResponse'] = 201
			api_data['ApiMessages'] += ['INFO - Request processed successfully']

			return api_data

		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] += ['ERROR - Could not create customer subscription record']

		return api_data

	def CustomerSubscriptionUpdated(event):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		
		event_data = Events.ExtractSubscriptionData(event)

		if not event_data:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ["ERROR - Failed to extract subscription data"]

			return api_data

		query = """
			UPDATE subscriptions
			SET customer_id = %s,
				user_id = %s,
				plan_id = %s,
				product_id = %s,
				event_type = %s,
				billing_interval = %s,
				amount = %s,
				currency = %s,
				status = %s,
				subscription_data = %s,
				period_start = %s, 
				period_end = %s,
				disabled = %s,
				last_updated = %s,
				date = %s
			WHERE subscription_id = %s
		"""

		inputs = (
			event_data.get('customer_id'),
			event_data.get('user_id'),
			event_data.get('plan_id'),
			event_data.get('product_id'),
			event_data.get('event_type'),
			event_data.get('billing_interval'),
			event_data.get('amount'),
			event_data.get('currency'),
			event_data.get('status'),
			json.dumps(event_data.get('subscription_data')),
			event_data.get('period_start'),
			event_data.get('period_end'),
			event_data.get('disabled'),
			str(Common.Datetime()),
			str(Common.Datetime()),
			event_data.get('subscription_id')
		)

		if Db.ExecuteQuery(query,inputs,True):
			api_data['ApiHttpResponse'] = 202
			api_data['ApiMessages'] += ['INFO - Request processed successfully']

			return api_data

		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] += ['ERROR - Could not update customer subscription record']

		return api_data

	def CustomerSubscriptionDeleted(event):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		
		event_data = Events.ExtractSubscriptionData(event)

		if not event_data:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ["ERROR - Failed to extract subscription data"]

			return api_data
		
		query = """
			UPDATE subscriptions
			SET event_type = %s,
				status = %s,
				subscription_data = %s,
				last_updated = %s
			WHERE subscription_id = %s
		"""

		inputs = (
			event_data.get('event_type'),
			'cancelled',
			json.dumps(event_data.get('subscription_data')),
			str(Common.Datetime()),
			event_data.get('subscription_id')
		)

		if Db.ExecuteQuery(query,inputs,True):
			api_data['ApiHttpResponse'] = 202
			api_data['ApiMessages'] += ['INFO - Request processed successfully']

			return api_data

		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] += ['ERROR - Failed to cancel subscription']

		return api_data
	
	def ExtractInvoiceData(event):

		try:
			invoice_data = event['data']['object']

			return {
				'invoice_data': event['data']['object'],
				'event_type': event['type'],
				'invoice_id': invoice_data['id'],
				'customer_id': invoice_data['customer'],
				'subscription_id': invoice_data['subscription'],
				'user_id': invoice_data['subscription_details']['metadata']['UserId'],
				'email': invoice_data['subscription_details']['metadata']['Email'],
				'plan_id': invoice_data['lines']['data'][0]['plan']['id'],
				'product_id': invoice_data['lines']['data'][0]['plan']['product'],
				'description': Common.CleanDescription(invoice_data['lines']['data'][0]['description']),
				'currency': invoice_data['currency'],
				'billing_interval': invoice_data['lines']['data'][0]['plan']['interval'],
				'amount': float(int(invoice_data['lines']['data'][0]['plan']['amount']) / 100),
				'amount_paid': float(int(invoice_data['amount_paid']) / 100),
				'period_start': Common.ConvertUnixDate(invoice_data['lines']['data'][0]['period']['start']) if invoice_data['lines']['data'][0]['period']['start'] else None,
				'period_end': Common.ConvertUnixDate(invoice_data['lines']['data'][0]['period']['end']) if invoice_data['lines']['data'][0]['period']['end'] else None
			}
		
		except KeyError as e:
			
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - KeyError exception caught', event)
			return False
		
		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to get data from invoice event', event)
			return False
		
	def ExtractSubscriptionData(event):

		try:
			subscription_data = event['data']['object']

			return {
				'subscription_data': event['data']['object'],
				'event_type': event['type'],
				'subscription_id': subscription_data['id'],
				'customer_id': subscription_data['customer'],
				'plan_id': subscription_data['plan']['id'],
				'product_id': subscription_data['plan']['product'],
				'currency': subscription_data['plan']['currency'],
				'billing_interval': subscription_data['plan']['interval'],
				'amount': float(int(subscription_data['plan']['amount']) / 100),
				'status': subscription_data['status'],
				'user_id': subscription_data['metadata']['UserId'],
				'period_start': str(Common.ConvertUnixDatetime(subscription_data['current_period_start'])),
				'period_end': str(Common.ConvertUnixDatetime(subscription_data['current_period_end'])) if subscription_data['current_period_end'] else None,
				'disabled': 1 if subscription_data['cancel_at'] else 0,
				'cancel_at': subscription_data['cancel_at']
			}
		
		except KeyError as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - KeyError exception caught', event)
			return False
		
		except Exception as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Failed to get data from subscription event', event)
			return False