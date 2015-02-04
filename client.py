import base64
import sys
import ConfigParser

from pysimplesoap.client import SoapClient


class Client:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('config_client.ini')
        self.nrserwera = 1
        self.change_server()
        self.tryb = 0  # 0 - brak transakcji, 1 - transakcja
        self.kill = 0
        self.writes = []

    def reset(self):
        self.tryb = 0
        self.writes = []

    def change_server(self):
        for i in range(1, len(sys.argv)):
            print "Serwer %", i
        self.nrserwera = raw_input('Ktory wybierasz ? ')
        self.do_change_server(int(self.nrserwera))


    def do_change_server(self, id_server):
        self.serwer = self.config.get('serwer' + str(id_server), 'serwer')
        self.client = SoapClient(
            location=self.serwer,
            action=self.serwer,  # SOAPAction
            namespace="http://server",
            soap_ns='soap',
            trace=False,
            ns=False)

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
            return -1
        elif content == 'nie ma pliku':
            print 'Nie ma takiego pliku'
            return -1
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
        response = self.client.writeBase64(filepath=input, content=data_base)
        result = response.writereturn
        id_trans = int(result)
        if id_trans >= 0:
            self.writes.append([self.nrserwera, id_trans, -1])  # czy byl commit
        return id_trans

    def transaction(self):
        if len(self.writes) > 0:
            input = raw_input('Akceptujemy transakcje? (T/N,domyslnie=N) ')
            guard = 0
            if input.lower() == 't':
                for write in self.writes:
                    if self.can_commit(write[0], write[1]) != 0:
                        guard = 1
                if guard == 0:
                    return self.commit()
                else:
                    print 'Jeden z serwerow anulowal'
                    return self.abort()
            else:
                return self.abort()
        return -1

    def can_commit(self, serwer, id_trans):
        self.do_change_server(serwer)
        response = self.client.canCommit(transactionId=id_trans)
        result = response.canommmitreturn
        return int(result)

    def commit(self):
        guard = 0
        for write in self.writes:
            self.do_change_server(write[0])
            print write[2]
            if self.acceptTransaction(write[1]) == 0:
                write[2] = 0
            else:
                guard = 1

        if guard == 0:
            return 0
        else:
            return self.abort_withrollback()


    def abort(self):
        for write in self.writes:
            self.do_change_server(write[0])
            self.refuseTransaction(write[1])
        return 1

    def abort_withrollback(self):
        print 'jeden z serwerow anulowal'
        for write in self.writes:
            self.do_change_server(write[0])
            if write[2] == -1:  # jesli nie bylo jeszcze commita robi abort
                self.refuseTransaction(write[1])
            else:  # jesli byl robimy rollbacka
                print 'wykonujemy rollback'
                print write[1]
                response = self.client.forceRollback(transactionId=write[1])
                result = response.forcerollbackreturn
                # brakuje info co jesli inna aplikacja zablokuje juz plik
        return 2

    def acceptTransaction(self, transaction_id):
        response = self.client.acceptTransaction(transactionId=transaction_id)
        result = response.acceptreturn
        return int(result)

    def refuseTransaction(self, transaction_id):
        response = self.client.refuseTransaction(transactionId=transaction_id)
        result = response.refusereturn
        return int(result)

    def program(self):
        print '-----------------------------------------'
        print 'Co chcesz wykonac?:\nserwer - zmiana serwera\nls - odczyt plikow w katalogu\nread - odczyt pliku\nstart -rozpoczecie transakcji\nkoniec - koniec programu'
        print '-----------------------------------------'
        todo = raw_input()
        if todo == 'serwer':
            self.change_server()
        elif todo == 'ls':
            result = self.ls()
            print result
        elif todo == 'read':
            result = self.read()

            if (result == 0):
                print 'Plik odczytano i zapisano'
        elif todo == 'start':
            self.tryb = 1
        elif todo == 'koniec':
            self.kill = 1

    def program_transakcji(self):
        print '-----------------------------------------'
        print 'Co chcesz wykonac?:\nserwer - zmiana serwera\nls - odczyt plikow w katalogu\nread - odczyt pliku\nwrite -zapis do pliku\nstop - koniec transakcji\nkoniec - koniec programu'
        print '-----------------------------------------'
        todo = raw_input()
        if todo == 'serwer':
            self.change_server()
        elif todo == 'ls':
            result = self.ls()
            print result
        elif todo == 'read':
            result = self.read()
            if (result == 0):
                print 'Plik odczytano i zapisano na dysku'
        elif todo == 'write':
            result = self.write()
            if (result >= 0):
                print 'Plik przeslano na serwer'
            elif (result == -2):
                print 'Odmowa dostepu, blokada na pliku'
            elif (result == -1):
                print 'Blad zapisu'
        elif todo == 'stop':
            result = self.transaction()
            if result == 0:
                print "transakcja powiodla sie"
            elif result == 2:
                print "transakcja niepowiodla sie"
            elif result == 1:
                print "transakcje anulowano"
            elif result == -1:
                print "brak operacji do zatwierdzenia"

            self.reset()

        elif todo == 'koniec':
            self.kill = 1

abc = Client()

while (not abc.kill):
    if not abc.tryb:
        abc.program()
    elif abc.tryb == 1:
        abc.program_transakcji()
    else:
        abc.kill = 1