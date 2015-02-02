from pysimplesoap.client import SoapClient, SoapFault
import base64

class Client:

	def __init__(self):
		self.client = SoapClient(
			location = "http://localhost:8008/",
			action = 'http://localhost:8008/', # SOAPAction
			namespace = "http://example.com/sample.wsdl", 
			soap_ns='soap',
			trace = False,
			ns = False)

	def ls(self):
		response = self.client.ls()
		result = response.lsreturn
		return result

	def read(self):
		input = raw_input('Podaj nazwe pliku do odczytu ')
		response = self.client.readBase64(filepath=input)
		content = str(response.readreturn)
		if content == 'zablokowany':
			print 'Plik jest zablokowany'
			return 0
		elif content == 'nie ma pliku':
			print 'Nie ma takiego pliku'
			return 0
		else:
			out_file = open(input, "wb")
			file = base64.b64decode(content)
			out_file.write(file)
			out_file.close()
			return 0

	def write(self):
		input = raw_input('Podaj sciezke do pliku ')
		in_file = open(input, "rb")
		data = in_file.read()
		in_file.close()
		data_base = base64.b64encode(data)
		response = self.client.writeBase64(filepath = input, content = data_base)
		result = response.writereturn
		id_trans = int(result)
		return self.transaction(id_trans)

	def transaction(self,transaction_id):
		input = raw_input('Akceptujemy transakcje? (T/N,domyslnie=N) ')
		if input.lower() == 't':
			self.acceptTransaction(transaction_id)
		else:
			self.refuseTransaction(transaction_id)

	def acceptTransaction(self,transaction_id):
		response = self.client.acceptTransaction(transactionId=transaction_id)
		result = response.acceptreturn
		print result
		return 0


	def refuseTransaction(self,transaction_id):
		response = self.client.refuseTransaction(transactionId=transaction_id)
		result = response.refusereturn
		print result
		return 0

abc = Client()
result = abc.ls()
print result

print '--------------------------------------'
#abc.read()

abc.write()


