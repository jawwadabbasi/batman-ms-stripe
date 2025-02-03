import time
import random
import string

from datetime import datetime, timezone

class Common:

	def Date():

		return datetime.now(timezone.utc).strftime('%Y-%m-%d')

	def Datetime():

		return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

	def DateObject():

		return datetime.strptime(Common.Date(), '%Y-%m-%d')

	def DatetimeObject():

		return datetime.strptime(Common.Datetime(), '%Y-%m-%d %H:%M:%S')
	
	def ConvertUnixDatetime(timestamp):

		return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
	
	def ConvertUnixDate(timestamp):

		return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
	
	def InvoiceFormat(date):

		return date.strftime('%B %d, %Y')
	
	def UnixTime():

		return int(time.time())

	def GenerateReceiptNumber():

		hex_string = ''.join(random.choices(string.hexdigits.upper(), k=16))

		return '-'.join([hex_string[i:i+4] for i in range(0, len(hex_string), 4)])
	
	def CleanDescription(string):

		try:
			return string.split(" × ")[1].split(" (")[0].lower()
		
		except:
			return string.lower()
		
	def CalculateTax(amount_paid, amount):

		if not amount_paid:
			return "0.00"
		
		return "{:.2f}".format(abs(float(amount_paid) - float(amount)))