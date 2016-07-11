#!/usr/bin/python
# encoding=utf-8

import threadpool
import argparse
import socket
import sys
import time
import codecs
import requests
import logging
from IPy import IP
from bs4  import BeautifulSoup


TIMEOUT = 5
TSN = 6
PORTLST = [21,22,23,1433,3306,4000,1521,80,8080,443,8089]
RPORT = None
ISOTIMEFORMAT = '%Y-%m-%d %X'


def save_result(content):
    '''save results'''
    
    try:
        f = codecs.open("result.html","a+","utf-8")
        #f = open("result.html","a+")
        f.write(content)
        f.close()
    except Exception,e:
        print e


def debug_log():
    '''logging'''
    
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='debug.log',
                filemode='a')



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
    host = socket.gethostbyname(host)
    # connect port
    try:
        if s.connect_ex((host,int(port))) is 0:
            port_state['state'] = 1
            try:
                data = s.recv(1024)
            except socket.timeout,e:
                pass
            if data is not None:
                # banner
                port_state['banner'] = data
            else:
                # send http request
                s.send("HEAD / HTTP/1.1\r\nHost: %s\r\n\r\n" % (host))
                try:
                    data = s.recv(1024)
                except socket.timeout,e:
                    pass
                if (data is not None) and ("HTTP/" in data):
                    port_state['isHTTP'] = 1
                    
    except Exception,e:
        print("[-] Debug: %s" % e)
    finally:
        s.close()
    return port_state
    

def get_http_title(ip,port):
    '''get title'''
    
    url = 'http://' + ip + ':' + str(port) + '/'
    
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language':'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
               'Accept-Charset':'UTF-8',
               'User-Agent':'Mozilla/5.0 (compatible; Googlebot/2.1; http://www.google.com/bot.html)'}
    
    try:
        r = requests.get(url,headers=headers,allow_redirects=True,verify=False)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text,"html.parser",from_encoding="utf-8")
        #print soup.original_encoding
        #print type(soup.title.string).__name__
        
        if soup.title is None or soup.title.string is None:
            title = "can't get title"
        else:
            title = soup.title.string
            
        info =  "<tr><td>"  + str(ip) 
        info += "</td><td>" + str(port)
        info += "</td><td>" + str(r.status_code)
        info += "</td><td>" + title
        info += "</td><td>" + str(r.headers)
        info += "</td></tr>"
        
    except requests.exceptions.RequestException,e:
        logging.debug(e)
    
    return info



def main_control(host):
    global RPORT
    for p in RPORT:
        cp = get_port_state(host,p)
        if cp['state'] == 1:
            print("[-] Debug: host %s port:%s open." %(host,p))
            if cp['isHTTP'] == 1:
                # get the http title
                #print("host %s:%s is http " %(host,p))
                save_result(get_http_title(host,p))
            elif cp['banner'] is not None:
                print("[*] ip:%s port:%d banner: %s" %(host,p,cp['banner']))



def main():
    
    global RPORT

    parser = argparse.ArgumentParser(description='Portscan & Get banner v1.0  write by ruo.')
    parser.add_argument('--host',dest='host',required='true',type=str,help="The ip address(could use CIDR)")
    parser.add_argument('-p','--port',dest='port',type=str,help="Scan port use ',' split,don't be naughty")
    parser.add_argument('-t','--threads',dest='thread_num',type = int,help="The numbers of threads less than 13 (default 3)")
    parser.add_argument('-v',help="Show the soft version.",action='version')                   
    args = parser.parse_args()
        
    host = args.host
    RPORT = args.port
    t_num = args.thread_num
    
    if t_num is None or t_num > 8:
        t_num = TSN
    
    if RPORT is None:
        RPORT = PORTLST
    else:
        RPORT = list(eval(RPORT.strip()))
    
    # debug log
    debug_log()
    
    iplst = []
    ip = IP(host)
    for i in ip:
        #print i
        iplst.append("%s" % (i) )
    
    '''
    for i in range(100,200):
        iplst.append("%s" % ("61.139.105."+str(i)))
        
    '''   
        
    
    tables_start =  '''
                    <div style="height:50px"> Scan 
                    '''
    tables_start += host + "</br>"
    tables_start += time.strftime(ISOTIMEFORMAT,time.gmtime(time.time()))
    tables_start += '''
                    </div>
                    <table border="1px" cellspacing="0px" style="border-collapse:collapse">
                      <tr>
                        <th>IP</th>
                        <th>Port</th>
                        <th>Code</th>
                        <th>Title(Banner)</th>
                        <th>Headers</th>
                      </tr>
                     '''
    save_result(tables_start)
    
    # close table
    tables_end = "</table>"
    
    # threadpool
    pool = threadpool.ThreadPool(t_num)
    requests = threadpool.makeRequests(main_control, iplst)
    [pool.putRequest(req) for req in requests]
    pool.wait() 
    
    save_result(tables_end)

     
if __name__ == '__main__':
    main()
    