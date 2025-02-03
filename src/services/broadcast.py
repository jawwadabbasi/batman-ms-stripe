import requests

class Broadcast:

	api_endpoint = 'http://batman-ms-broadcast'

	def SendEmail(email,purpose,meta=False):

		data = {
			'Email': email,
			'Purpose': purpose,
			'Meta': meta
		}

		try:
			result = requests.post(f'{Broadcast.api_endpoint}/api/v1/Email/Send',json = data,stream = True)

			return True if result.ok else False

		except:
			return False