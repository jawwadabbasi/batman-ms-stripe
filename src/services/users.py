import requests

class Users:

	api_endpoint = 'http://batman-ms-users'

	def Get(user_id):

		data = {
			'UserId': user_id,
		}

		try:
			result = requests.get(f'{Users.api_endpoint}/api/v1/User/Get',params=data)
			
			return result.json()['ApiResult'] if result.ok else False

		except:

			return False
		
	def UpdateSubscription(user_id, subscription):

		data = {
			'UserId': user_id,
			'Subscription': subscription
		}

		try:
			result = requests.post(f'{Users.api_endpoint}/api/v1/User/UpdateSubscription',json = data,stream = True)
			
			return True if result.ok else False

		except:

			return False