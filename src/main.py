# Coded with ingenuity,
# by Jawwad Abbasi (jawwad@omnitryx.ca)

# Initiates a Flask app to handle managed endpoints
# and relays to corresponding controller and module
# for processing.

import json
import sentry_sdk
import stripe
import settings

from flask import Flask,Response,request
from v1.controller import Ctrl_v1
from v2.controller import Ctrl_v2

sentry_sdk.init(
	dsn = settings.SENTRY_DSN,
	traces_sample_rate = settings.SENTRY_TRACES_SAMPLE_RATE,
	profiles_sample_rate = settings.SENTRY_PROFILES_SAMPLE_RATE,
	environment = settings.SENTRY_ENVIRONMENT
)

app = Flask(__name__)

stripe.api_key=settings.STRIPE_API_KEY

@app.errorhandler(404)
def RouteNotFound(e):

	return Response(None,status = 400,mimetype = 'application/json')

####################################
# Supported endpoints for API v1
####################################
@app.route('/api/v1/Stripe/Customer/Get',methods = ['GET'])
def GetCustomer():

	data = Ctrl_v1.GetCustomer(request.args)
	return Response(json.dumps(data),status = data['ApiHttpResponse'],mimetype = 'application/json')

@app.route('/api/v1/Stripe/Customer/Delete',methods = ['POST'])
def DeleteCustomer():

	data = Ctrl_v1.DeleteCustomer(request.json)
	return Response(json.dumps(data),status = data['ApiHttpResponse'],mimetype = 'application/json')

@app.route('/api/v1/Stripe/Invoices/Get',methods = ['GET'])
def GetInvoices():

	data = Ctrl_v1.GetInvoices(request.args)
	return Response(json.dumps(data),status = data['ApiHttpResponse'],mimetype = 'application/json')

@app.route('/api/v1/Stripe/Subscription/Cancel',methods = ['POST'])
def CancelSubscription():

	data = Ctrl_v1.CancelSubscription(request.json)
	return Response(json.dumps(data),status = data['ApiHttpResponse'],mimetype = 'application/json')

@app.route('/api/v1/Stripe/CheckoutSession/Create',methods = ['POST'])
def CreateCheckoutSession():

	data = Ctrl_v1.CreateCheckoutSession(request.json)
	return Response(json.dumps(data),status = data['ApiHttpResponse'],mimetype = 'application/json')

@app.route('/api/v1/Stripe/Webhook', methods=['POST'])
def ProcessEvents():

	data = Ctrl_v1.ProcessEvents(request.json)
	return Response(json.dumps(data),status = data['ApiHttpResponse'],mimetype = 'application/json')

####################################
# Initiate web server
####################################
app.run(host = '0.0.0.0',port = settings.FLASK_PORT,debug = settings.FLASK_DEBUG)