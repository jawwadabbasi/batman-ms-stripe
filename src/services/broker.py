import requests

class Broker:

	api_endpoint = 'http://batman-ms-broker'

	def QueueMessage(queue,message):

		data = {
			'Queue': queue,
			'Message': message
		}

		try:
			result = requests.post(f'{Broker.api_endpoint}/api/v1/Message/Queue',json = data,stream = True)

			return True if result.ok else False

		except:
			return False