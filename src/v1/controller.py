import inspect

from v1.manager import Manager
from v1.checkout import Checkout
from v1.events import Events
from services.logger import Logger

class Ctrl_v1:

	def Response(endpoint,request_data = None,api_data = None,log = True):
		
		if log is True:
			Logger.CreateServiceLog(endpoint,request_data,api_data)

		return api_data

	def BadRequest(endpoint,request_data = None):

		api_data = {}
		api_data['ApiHttpResponse'] = 400
		api_data['ApiMessages'] = ['ERROR - Missing required parameters']
		api_data['ApiResult'] = []

		Logger.CreateServiceLog(endpoint,request_data,api_data)

		return api_data
	
	def GetCustomer(request_data):

		if (not request_data.get('UserId')):
			return Ctrl_v1.BadRequest(inspect.stack()[0][3],request_data)

		api_data = Manager.Get(
			request_data.get('UserId')
		)

		return Ctrl_v1.Response(inspect.stack()[0][3],request_data,api_data)
	
	def DeleteCustomer(request_data):

		if (not request_data.get('UserId')):
			return Ctrl_v1.BadRequest(inspect.stack()[0][3],request_data)

		api_data = Manager.Delete(request_data.get('UserId'))

		return Ctrl_v1.Response(inspect.stack()[0][3],request_data,api_data)
	
	def GetInvoices(request_data):

		if (not request_data.get('UserId')):
			return Ctrl_v1.BadRequest(inspect.stack()[0][3],request_data)

		api_data = Manager.Invoices(
			request_data.get('UserId'),
			request_data.get('ReceiptId',False),
			request_data.get('Limit', 10)
		)

		return Ctrl_v1.Response(inspect.stack()[0][3],request_data,api_data)
	
	def CancelSubscription(request_data):

		if (not request_data.get('UserId')
			or not request_data.get('SubscriptionId')
		):
			return Ctrl_v1.BadRequest(inspect.stack()[0][3],request_data)

		api_data = Manager.CancelSubscription(
			request_data.get('UserId'),
			request_data.get('SubscriptionId')
		)

		return Ctrl_v1.Response(inspect.stack()[0][3],request_data,api_data)
	
	def CreateCheckoutSession(request_data):

		if (not request_data.get('UserId')
			or not request_data.get('PriceId')
			or not request_data.get('Email')
			or not request_data.get('Phone')
			or not request_data.get('ProfileStatus')
		):
			return Ctrl_v1.BadRequest(inspect.stack()[0][3],request_data)

		api_data = Checkout.CreateSession(
			request_data.get('UserId'),
			request_data.get('PriceId'),
			request_data.get('Email'),
			request_data.get('Phone'),
			request_data.get('ProfileStatus')
		)

		return Ctrl_v1.Response(inspect.stack()[0][3],request_data,api_data)
	
	def ProcessEvents(request_data):

		if (not request_data.get('RequestBody')):
			return Ctrl_v1.BadRequest(inspect.stack()[0][3],request_data)
		
		api_data = Events.Process(request_data.get('RequestBody'))

		return Ctrl_v1.Response(inspect.stack()[0][3],request_data,api_data)