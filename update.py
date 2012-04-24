from urllib2 import *
from threading import Thread
from time import time, sleep
from sys import argv, exit
from os import fsync,remove
import shutil

def writetofile(s):
    global g
    for i in xrange(0,len(s)-1):
        g.write(s[i]+',')
    g.write(s[len(s)-1])
    
def getuser(name):
            def current_time():
                return str(int(time()))
            try:
                temp=urlopen('http://www.reddit.com/user/'+name+'/about.json').read()
                #Link karma
                l=temp.find('"link_karma":')
                if l==-1: 
                    raise URLError('Reddit server didn\'t return page')
                link=temp[l+14:temp.find(',',l+15)]
                #Comment karma
                l=temp.find('"comment_karma":')
                comment=temp[l+17:temp.find(',',l+18)]
                #Created
                l=temp.find('"created":')
                created=temp[l+11:temp.find('.',l+18)]
                #Users[name]=[link,comment,created]
                writetofile([name,link,comment,created,current_time()+'\n'])
            except URLError, e:
                        print 
                        print 'Error: ' + str(e)
                        print

shutil.move( 'Karma', 'Karma'+"~" )
f = open('Karma~', 'r')
g = open('Karma', 'w')
stop=False
for line in f:
    try:
         line=line.split(',')
         if stop==False:
             #name,link,comment,join date,crawl date
             line[4].replace('\n','')
             #Time in seconds
             if ((int(time())-int(line[4]))>(10**6)) and (int(line[1])+int(line[2])>5000):
                print line[0:4]
                getuser(line[0])
                sleep(2)
             else:
                writetofile(line)
         else:
               writetofile(line) 
    except KeyboardInterrupt:
        stop=True
    

f.close()
g.close()
remove('Karma~')
