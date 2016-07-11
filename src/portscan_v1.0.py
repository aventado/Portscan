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

reload(sys).setdefaultencoding('UTF-8')


TIMEOUT = 5
PORTLST = [80,8080,443]
ISOTIMEFORMAT = '%Y-%m-%d %X'


def save_to_file(content):
    '''保存结果'''
    try:
        f = codecs.open("result.html","a+","utf-8")
        #f = open("result.html","a+")
        f.write(content)
        f.close()
    except Exception,e:
        print e


def log_debug():
    '''日志处理'''
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='debug.log',
                filemode='a')



def port_scan(host,port = PORTLST,timeout = TIMEOUT):
    '''扫描端口'''     
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(float(timeout))
    # get ip of remote host
    remote_ip = socket.gethostbyname(host)
    # connect port
    for p in port:
        try:
            #if s.connect_ex((remote_ip,int(p))):
            s.connect((remote_ip,int(p)))
            print ("ip %s %d port open." % (remote_ip,p))
            time.sleep(2)
            # Get http title
            #print "get http title..."
            request_content(host,p)
        except Exception,e:
            logging.debug("%s:%s %s" %(remote_ip,p,e))
            #print e
        finally:
            #  make sure that socket are always closed
            s.close()
    


def request_content(ip,port):
    '''获取请求返回信息'''
    url = 'http://' + ip + ':' + str(port) + '/'
    
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language':'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
               'Accept-Charset':'UTF-8',
               'User-Agent':'Mozilla/5.0 (compatible; Googlebot/2.1; http://www.google.com/bot.html)'}
    
    try:
        r = requests.get(url,headers=headers,allow_redirects=True,verify=False)
        #print r.encoding
        #print chardet.detect("123dfegf")
        #print r.text
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text,"html.parser",from_encoding="utf-8")
        #print soup.original_encoding
        #print type(soup.title.string).__name__
        title = soup.title.string
        #print title
        
        if title is None:
            title = "no title"
    
        #print sp.find('title')
        info =  "<tr><td>"  + str(ip) 
        info += "</td><td>" + str(port)
        info += "</td><td>" + str(r.status_code)
        info += "</td><td>" + title
        info += "</td><td>" + str(r.headers)
        info += "</td></tr>"
        
        save_to_file(info)
        # delay time
        time.sleep(2)
    except requests.exceptions.RequestException,e:
        logging.debug(e)



def main(host,port):
    
    log_debug()
    
    # ip list
    iplst = []
    ip = IP(host)
    for i in ip:
        #print ipaddr
        iplst.append("%s" % (i) )
    # print iplst
    
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
                        <th>Title</th>
                        <th>Headers</th>
                      </tr>
                     '''
    save_to_file(tables_start)
    
    # close table
    tables_end = "</table>"

 

    #线程池
    pool = threadpool.ThreadPool(15)
    requests = threadpool.makeRequests(port_scan, iplst)
    [pool.putRequest(req) for req in requests]
    pool.wait() 
    
    save_to_file(tables_end)

     
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RPS')
    parser.add_argument('--host',action="store",dest="host",help="The ip address(could use CIDR).")
    parser.add_argument('--port',action="store",dest="port",default=PORTLST,type=str,help="Scan port use ',' split.")
    
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port
    
    
    main(host,port)
    