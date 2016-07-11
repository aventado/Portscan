#!/usr/bin/env puthon
# encoding=utf-8


import socket
import time



PORT = [22,23,80]
TIMEOUT = 5


'''
def connect_port(host,port):
    port_state = {"state":0, # port state，default 0 is close
                  #"port":None, # port num
                  "isHTTP":0,  # is HTTP port,default 0 is not
                  "banner":"" # banner
                  }
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(float(TIMEOUT))
    #get ip of remote host
    host = socket.gethostbyname(host)
    #connect port
    try:
        if s.connect_ex((host,int(port))) is 0:
            port_state['state'] = 1
            #print ("ip %s %d port open." % (host,port))
            #s.send('GET / HTTP/1.0\r\n\r\n')
            s.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % (host))
            # change port state
            data = s.recv(1024)
            if data and ("HTTP/" in data):
                # http port
                #print "http port"
                #port_state['port'] = port
                port_state['isHTTP'] = 1
            else:
                # banner
                #print("datatype %s" % type(data))
                # if server return "" string
                #print data
                port_state['banner'] = data
    except Exception,e:
        print("debug: %s" % e)
    finally:
        #print "close socket"
        s.close()
    return port_state
'''

def get_port_state(host,port):
    '''connect the port'''
    data = None
    port_state = {"state":0, # port state，default 0 is close
                  #"port":None, # port num
                  "isHTTP":0,  # is HTTP port,default 0 is not
                  "banner":"" # banner
                  }
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(float(TIMEOUT))
    #s.setblocking(0)
    # get ip of remote host
    host = socket.gethostbyname(host)
    # connect port
    try:
        if s.connect_ex((host,int(port))) is 0:
            port_state['state'] = 1
            #print ("ip %s %d port open." % (host,port))
            
            try:
                data = s.recv(1024)
            except socket.timeout,e:
                pass
            
            if data is not None:
                # banner
                port_state['banner'] = data
            else:
                # send http request
                s.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % (host))
                try:
                    data = s.recv(1024)
                except socket.timeout,e:
                    pass
                if (data is not None) and ("HTTP/" in data):
                    port_state['isHTTP'] = 1
                    
    except Exception,e:
        print("Debug(line 83): %s" % e)
    finally:
        #print "close socket"
        s.close()
    return port_state


for p in PORT:
    host = '61.139.105.107'
    cp = get_port_state(host,p)
    if cp['state'] == 1:
        if cp['isHTTP'] == 1:
            print("host %s:%s is http " %(host,p))
        elif cp['banner'] is not None:
            #pass
            print cp['banner']
            
    
    
    
    