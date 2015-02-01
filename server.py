from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
from os import listdir
from os.path import isfile, join
import base64
import os
import ntpath
import time
from threading import Thread

id = 0
transactions = []
running_transactions = []
mypath = 'onet'
os.chdir(mypath)
mypath = os.getcwd()
lock = '.lock'
tmp = '.tmp'
czas=10 #ile sekund czeka
koniec = 0

#lista plikow
def ls():
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    return ''.join(onlyfiles)

#tworzy transakcje z id+1 oraz nazwa pliku
def new_transaction(fname,lock):
	global id
	id+=1
	transaction = [id,fname,lock,-1]
	transactions.append(transaction)
	running_transactions.append([id,time.time()])
	return id

#robi update statusu transakcji
def update_transaction(id_t,status,name_copy):
	for trans in transactions:
		if trans[0] == id_t:
			trans[3] = status
			if name_copy:
				trans[2]=name_copy
	return 0
		
	
#zapisuje do pliku, tworzy lock jesli jest 
def write(filepath,content):
	fname = ntpath.basename(filepath)
	if os.path.isfile(join(mypath,fname)):
		id_trans = new_transaction(fname,fname+lock)
		os.rename(fname,fname + lock)
		out_file = open(fname + tmp, "wb")
		file = base64.b64decode(content)
		out_file.write(file)
		out_file.close()
	else:
		id_trans = new_transaction(fname,'NO')
		out_file = open(fname + tmp, "wb")
		file = base64.b64decode(content)
		out_file.write(file)
		out_file.close()
	if os.path.isfile(join(mypath,fname + tmp )):
		
		return id_trans
	else:

		if os.path.isfile(join(mypath,fname + lock )):
			os.rename(fname+lock,fname)
		if os.path.isfile(join(mypath,fname + tmp )):
			os.remove(fname+tmp)
		update_transaction(id_trans,0,0)
		return -1

def accept(transactionId):
	data = []

	for trans in transactions:
		if trans[0] == transactionId:
			data = trans
	fname=data[1]
	if os.path.isfile(join(mypath,fname + tmp )):
		os.rename(fname + tmp,fname)
	if os.path.isfile(join(mypath,fname + lock )):
		os.rename(fname + lock,fname + '_' + str(transactionId))

	update_transaction(transactionId,1,fname + '_' + str(transactionId))
	return 1

def refuse(transactionId):
	data = []

	for trans in transactions:
		if trans[0] == transactionId:
			data = trans
	fname=data[1]
	if data[3]== (-1):
		if os.path.isfile(join(mypath,fname + tmp )):
			os.remove(fname + tmp)
		if os.path.isfile(join(mypath,fname + lock )):
			os.rename(fname + lock,fname)

		update_transaction(transactionId,0,0)
	return 1	

def read(filepath):
	fname = ntpath.basename(filepath)

	if os.path.isfile(join(mypath,fname)):
		out_file = open(fname, "rb")
		data = out_file.read()
		out_file.close()
		file = base64.b64encode(data)
		return file
	else:
		return -1

def timeout():

	while(not koniec):
		print 'abcasfsa'
		if running_transactions and (( int(time.time()) - running_transactions[0][1] ) > czas):
			print 'ubillllllllllllllleeeeeeeeeem'
			id = running_transactions[0][0]
			refuse(id)
			running_transactions.pop(0)
		time.sleep(1)
		


dispatcher = SoapDispatcher(
    'my_dispatcher',
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/', # SOAPAction
    namespace = "http://example.com/sample.wsdl", prefix="ns0",
    trace = True,
    ns = True)

# register the user function
dispatcher.register_function('ls', ls,
    returns={'lsreturn': str}, 
    args={})

dispatcher.register_function('readBase64', read,
    returns={'readreturn': str}, 
    args={'filepath': str})

dispatcher.register_function('writeBase64', write,
    returns={'writereturn': int}, 
    args={'filepath': str, 'content':str})

dispatcher.register_function('acceptTransaction', accept,
    returns={'acceptreturn': int}, 
    args={'transactionId': int})

dispatcher.register_function('refuseTransaction', refuse,
    returns={'refusereturn': int}, 
    args={'transactionId': int})


print "Starting server..."
httpd = HTTPServer(("", 8008), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.dispatcher = dispatcher
thread1 = Thread(target=httpd.serve_forever)
thread2 = Thread(target=timeout)
thread1.start()
thread2.start()
input = ''
while input!='koniec':
	input = raw_input('podaj co chcesz robic ')
koniec = 1
httpd.shutdown()
print 'abc'

