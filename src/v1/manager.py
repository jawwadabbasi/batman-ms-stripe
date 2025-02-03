import json
import inspect
import concurrent.futures

from v1.stripe import Stripe
from services.logger import Logger
from includes.db import Db
from includes.common import Common

class Manager:
	
	def Get(user_id):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			user_id = str(user_id)

		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		customer_id = Manager.GetCustomerId(user_id)

		if not customer_id:
			api_data['ApiHttpResponse'] = 200
			api_data['ApiMessages'] += ['INFO - No records found']

			return api_data
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			invoices = executor.submit(Manager.GetInvoice,user_id,False,10)
			subscription_details = executor.submit(Manager.GetSubscription,user_id)
			subscription_details = subscription_details.result()
			invoices = invoices.result()
		
		payload = {
			'Plan': {
				'SubscriptionId': subscription_details.get('SubscriptionId', ''),
				'SubscriptionName': invoices[0].get('Description', '').title() if invoices else 'Free',
				'Amount': subscription_details.get('Amount', 0),
				'AmountPaid': invoices[0].get('AmountPaid', 0) if invoices else 0,
				'Currency': subscription_details.get('Currency', 'USD'),
				'Taxes': invoices[0].get('Taxes', 0) if invoices else 0,
				'BillingInterval': subscription_details.get('BillingInterval', ''),
				'Status': subscription_details.get('Status', '').title(),
				'Disabled': subscription_details.get('Disabled', False),
        		'NextPaymentDate': subscription_details.get('PeriodEnd', '') if subscription_details.get('Status', '').lower() == 'active' else ''
			},
			'Invoices': invoices if invoices else []
		}

		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ['INFO - Request processed successfully']
		api_data['ApiResult'] = payload

		return api_data
	
	def Delete(user_id):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			user_id = str(user_id)

		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		query = """
			UPDATE customers
			SET disabled = %s
			WHERE user_id = %s
		"""

		inputs = (
			1,
			user_id,
		)

		if not Db.ExecuteQuery(query,inputs,True):
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not update records']

			return api_data
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(Manager.SuspendSubscription,user_id)
		
		api_data['ApiHttpResponse'] = 202
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data
	
	def CancelSubscription(user_id,subscription_id):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			user_id = str(user_id)
			subscription_id = str(subscription_id)

		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data

		subscription = Stripe.CancelSubscription(subscription_id)
		
		if not subscription:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to cancel subscription from stripe']

			return api_data
		
		query = """
			UPDATE subscriptions
			SET status = %s
			WHERE user_id = %s
		"""

		inputs = (
			'cancelled',
			user_id,
		)

		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(Db.ExecuteQuery,query,inputs,True)

		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data
		
	def Invoices(user_id, receipt_id=False, limit=10):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			user_id = str(user_id)

		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		invoices = Manager.GetInvoice(user_id,receipt_id,limit)

		if not invoices:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - No records found']

			return api_data
		
		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ['INFO - Request processed successfully']
		api_data['ApiResult'] = invoices

		return api_data
	
	def CreateCustomer(user_id, email, phone):
		
		customer = Stripe.CreateCustomer(user_id, email, phone)

		if not customer or 'id' not in customer:
			return False

		query = """
			INSERT INTO customers
			SET customer_id = %s,
				user_id = %s,
				email = %s,
				phone = %s,
				date = %s
		"""

		inputs = (
			customer['id'],
			user_id,
			email,
			phone,
			str(Common.Datetime())
		)

		result = Db.ExecuteQuery(query,inputs,True)

		if not result:
			return False
		
		return customer['id']
	
	def RetrieveCustomer(user_id):
		
		customer_id = Manager.GetCustomerId(user_id)

		if not customer_id:
			return False
		
		customer = Stripe.RetrieveCustomer(customer_id)
		
		if not customer:
			return False
		
		return customer
	
	def GetSubscriptionId(user_id):

		query = """
			SELECT subscription_id
			FROM subscriptions
			WHERE user_id = %s
			ORDER BY date DESC
			LIMIT 1
		"""

		inputs = (
			user_id,
		)

		result = Db.ExecuteQuery(query,inputs,True)

		return result[0]['subscription_id'] if result else False
	
	def GetCustomerId(user_id):

		query = """
			SELECT customer_id
			FROM customers
			WHERE user_id = %s
		"""

		inputs = (
			user_id,
		)

		result = Db.ExecuteQuery(query,inputs,True)

		return result[0]['customer_id'] if result else False
	
	def GetUserId(customer_id):

		query = """
			SELECT user_id
			FROM customers
			WHERE customer_id = %s
		"""

		inputs = (
			customer_id,
		)

		result = Db.ExecuteQuery(query,inputs,True)

		return result[0]['user_id'] if result else False
	
	def SuspendSubscription(user_id):

		subscription_id = Manager.GetSubscriptionId(user_id)

		if not subscription_id:
			return False
		
		result = Stripe.CancelSubscription(subscription_id)

		if not result:
			return False

		query = """
			UPDATE subscriptions
			SET status = %s
			WHERE user_id = %s
		"""

		inputs = (
			'cancelled',
			user_id,
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def GetInvoice(user_id,receipt_id=False,limit=1):
		
		query = """
			SELECT
				invoice_id AS InvoiceId,
				receipt_id AS ReceiptId,
				product_id AS ProductId,
				JSON_UNQUOTE(JSON_EXTRACT(invoice_data, '$.customer_email')) AS Email,
				description AS Description, 
				currency AS Currency, 
				amount AS Amount,
				amount_paid as AmountPaid,
				status AS Status,
				billing_interval AS BillingInterval,
				period_start AS PeriodStart, 
				period_end AS PeriodEnd
			FROM invoices
			WHERE user_id = %s
			AND event_type = %s
		"""
	
		inputs = (
			user_id,
			'invoice.paid',
		)
		
		if receipt_id:
			query += " AND receipt_id = %s ORDER BY DATE DESC LIMIT 1"
			inputs = (user_id, 'invoice.paid', receipt_id)
			
		else:
			query += f" ORDER BY DATE DESC LIMIT {limit}"

		result = Db.ExecuteQuery(query,inputs,True)

		if not result:
			return {}
		
		for row in result:
			row['Amount'] = float(row['Amount'])
			row['AmountPaid'] = float(row['AmountPaid'])
			row['Currency'] = str(row['Currency']).upper()
			row['ReceiptId'] = row['ReceiptId'].upper()
			row['Taxes'] = Common.CalculateTax(row['AmountPaid'], row['Amount'])
			row['Description'] = Common.CleanDescription(row['Description']).title()
			row['PeriodStart'] = Common.InvoiceFormat(row['PeriodStart'])
			row['PeriodEnd'] = Common.InvoiceFormat(row['PeriodEnd'])

		return result

	def GetSubscription(user_id):
		
		query = """
			SELECT
				subscription_id AS SubscriptionId,
				billing_interval AS BillingInterval,
				amount AS Amount,
				currency AS Currency, 
				status AS Status,
				disabled AS Disabled,
				period_start AS PeriodStart, 
				period_end AS PeriodEnd
			FROM subscriptions
			WHERE user_id = %s
			ORDER BY DATE DESC
			LIMIT 1
		"""
	
		inputs = (
			user_id,
		)

		result = Db.ExecuteQuery(query,inputs,True)

		if not result:
			return {}

		for row in result:
			row['Amount'] = float(row['Amount'])
			row['Currency'] = str(row['Currency']).upper()
			row['PeriodStart'] = Common.InvoiceFormat(row['PeriodStart'])
			row['PeriodEnd'] = Common.InvoiceFormat(row['PeriodEnd'])

		return result[0]
	
	def ExtractPaymentMethod(payload):

		if not payload:
			return False
		
		try:
			brand = payload['data'][0]['card']['brand']
			last4 = payload['data'][0]['card']['last4']

		except KeyError as e:

			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - KeyError exception caught', payload)
			return False
		
		except Exception as e:
			
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Failed to get data from payment method payload', payload)
			return False
		
		payment = {
			'Brand': brand,
			'Last4': last4,
			'Card':  brand.upper() + ' ' + last4
		}

		return payment