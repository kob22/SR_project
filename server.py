from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
from os import listdir
from os.path import isfile, join
import base64
import os
import ntpath
import time
from threading import Thread


class Server:

	lock = '.lock'
	tmp = '.tmp'
	czas=15 #ile sekund czeka

	def __init__(self):
		self.id = 0
		self.transactions = []
		self.running_transactions = []
		self.mypath = 'onet'
		os.chdir(self.mypath)
		self.mypath = os.getcwd()

		self.koniec = 0
		self.automat = 1
		self.transaction_toaccept= []

	def start(self):

		dispatcher = SoapDispatcher(
			'my_dispatcher',
			location = "http://localhost:8008/",
			action = 'http://localhost:8008/', # SOAPAction
			namespace = "http://example.com/sample.wsdl", prefix="ns0",
			trace = True,
			ns = True)

		# register the user function
		dispatcher.register_function('ls', self.ls,
			returns={'lsreturn': str}, 
			args={})

		dispatcher.register_function('readBase64', self.read,
			returns={'readreturn': str}, 
			args={'filepath': str})

		dispatcher.register_function('writeBase64', self.write,
			returns={'writereturn': int}, 
			args={'filepath': str, 'content':str})

		dispatcher.register_function('acceptTransaction', self.accept,
			returns={'acceptreturn': int}, 
			args={'transactionId': int})

		dispatcher.register_function('refuseTransaction', self.refuse,
			returns={'refusereturn': int}, 
			args={'transactionId': int})

		print "Starting server..."
		httpd = HTTPServer(("", 8008), SOAPHandler)
		httpd.dispatcher = dispatcher
		httpd.dispatcher = dispatcher
		thread1 = Thread(target=httpd.serve_forever)
		thread2 = Thread(target=self.timeout)
		thread1.start()
		thread2.start()
		input = ''
		while input!='koniec':
			input = raw_input('podaj co chcesz robic ')
		self.koniec = 1
		httpd.shutdown()
		print 'abc'

	def add_to_accept(self,id_trans):
		self.transaction_toaccept.append([id_trans,time.time(),-1,-1])
		return 0
	
	def do_transaction(self):
		return 0
	



	#lista plikow
	def ls(self):
		onlyfiles = [ f for f in listdir(self.mypath) if isfile(join(self.mypath,f)) ]
		lista = ''
		for file in onlyfiles:
			lista+= file +"\n"
		return lista


	#tworzy transakcje z id+1 oraz nazwa pliku
	def new_transaction(self,fname,lock):
		self.id+=1
		transaction = [self.id,fname,lock,-1]
		self.transactions.append(transaction)
		self.running_transactions.append([self.id,time.time()])
		return self.id

	#robi update statusu transakcji
	def update_transaction(self,id_t,status,name_copy):
		for trans in self.transactions:
			if trans[0] == id_t:
				trans[3] = status
				if name_copy:
					trans[2]=name_copy
		return 0
		

	def remove_running(self,id_t):
		a=[]
		for tran in self.running_transactions:
			if tran[0]==id_t:
				a=tran
		if a:
			self.running_transactions.remove(a)
		return 0

	#zapisuje do pliku, tworzy lock jesli jest 
	def write(self,filepath,content):
		fname = ntpath.basename(filepath)
		if os.path.isfile(join(self.mypath,fname)):
			id_trans = self.new_transaction(fname,fname+self.lock)
			os.rename(fname,fname + self.lock)
			out_file = open(fname + self.tmp, "wb")
			file = base64.b64decode(content)
			out_file.write(file)
			out_file.close()
		else:
			id_trans = self.new_transaction(fname,'NO')
			out_file = open(fname + self.tmp, "wb")
			file = base64.b64decode(content)
			out_file.write(file)
			out_file.close()
		if os.path.isfile(join(self.mypath,fname + self.tmp )):
		
			return id_trans
		else:

			if os.path.isfile(join(self.mypath,fname + self.lock )):
				os.rename(fname+self.lock,fname)
			if os.path.isfile(join(self.mypath,fname + self.tmp )):
				os.remove(fname+self.tmp)
			self.update_transaction(id_trans,0,0)
			return -1

	def accept(self,transactionId):
		data = []

		for trans in self.transactions:
			if trans[0] == transactionId:
				data = trans
		fname=data[1]
		if data[3]== (-1):
			if os.path.isfile(join(self.mypath,fname + self.tmp )):
				os.rename(fname + self.tmp,fname)
			if os.path.isfile(join(self.mypath,fname + self.lock )):
				os.rename(fname + self.lock,fname + '_' + str(transactionId))

			self.update_transaction(transactionId,1,fname + '_' + str(transactionId))
			self.remove_running(transactionId)
		return 1

	def refuse(self,transactionId):
		data = []

		for trans in self.transactions:
			if trans[0] == transactionId:
				data = trans
		fname=data[1]
		if data[3]== (-1):
			if os.path.isfile(join(self.mypath,fname + self.tmp )):
				os.remove(fname + self.tmp)
			if os.path.isfile(join(self.mypath,fname + self.lock )):
				os.rename(fname + self.lock,fname)

			self.update_transaction(transactionId,0,0)
		return 1	

	def read(self,filepath):
		fname = ntpath.basename(filepath)

		if os.path.isfile(join(self.mypath,fname)):
			out_file = open(fname, "rb")
			data = out_file.read()
			out_file.close()
			file = base64.b64encode(data)
			return file
		elif os.path.isfile(join(self.mypath,fname+self.lock)):
			return 'zablokowany'
		else:
			return 'nie ma pliku'

	def timeout(self):

		while(not self.koniec):
			print 'abcasfsa'
			if self.running_transactions and (( int(time.time()) - self.running_transactions[0][1] ) > self.czas):
				id = self.running_transactions[0][0]
				self.refuse(id)
				self.running_transactions.pop(0)
				print 'Transaction killed id: ',id
			time.sleep(1)
		
abc = Server()
abc.start()





