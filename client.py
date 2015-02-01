from pysimplesoap.client import SoapClient, SoapFault
import base64

# create a simple consumer
client = SoapClient(
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/', # SOAPAction
    namespace = "http://example.com/sample.wsdl", 
    soap_ns='soap',
    trace = False,
    ns = False)

# call the remote method
response = client.ls()

# extract and convert the returned value
result = response.lsreturn
print result
print '--------------------------------------'
# call the remote method
#in_file = open("/home/kob22/Pobrane/PySimpleSOAP-1.10/pysimplesoap/a.jpg", "rb") # opening for [r]eading as [b]inary
#data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
#in_file.close()

#a = base64.b64encode(data)
#response = client.writeBase64(filepath = '/home/kob22/Pobrane/PySimpleSOAP-1.10/pysimplesoap/a.jpg', content = a)

# extract and convert the returned value
#result = response.writereturn
#id_trans = int(result)


#-------------

# call the remote method
#response = client.acceptTransaction(transactionId=id_trans)

# extract and convert the returned value
#result = response.acceptreturn
#print result

#response = client.refuseTransaction(transactionId=id_trans)

# extract and convert the returned value
#result = response.refusereturn
#print result

# call the remote method
fpname='abc.jpg'
response = client.readBase64(filepath=fpname)

# extract and convert the returned value
content = response.readreturn
out_file = open(fpname, "wb")
file = base64.b64decode(str(content))
out_file.write(file)
out_file.close()
