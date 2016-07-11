


__author__ = 'bwarner' 
import socket 
import time


class Scan(object): 
    
    PORTLST = [21,22,23,8080,1433,3306,1522,4000,443,80]
    host = ""

    def __init__(self): 
        pass

    def get_banner(self,host,port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((host,int(port)))
            print("Port: " + repr(port) + " Open")
            '''
            while 1:
                data = s.recv(1024)
                if not data: break
            print repr(data)
            '''
            print(s.recv(1024))
            time.sleep(2)  
        except socket.error as msg:
            print msg
        s.close()


sc = Scan()
for p in sc.PORTLST:
    sc.get_banner("127.0.0.1",p)
          
