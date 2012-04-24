"""
Crawls reddit links and gets users link karma, comment karma and join date.

You can stop program anytime by pressing CTR + C.
Unsaved changes will be saved to file.



Options:
-sr	: Crawls only links from one subreddit. Default is All
-h	: This help
-o	: Output filename. Defalt is "Karma". You can also give path to file if you want.
-p	: Number of pages to get. 100 links per page. -1 for never stop, which is default
-m	: Minimium comments in a thread to open it. Default is 10
-u	: Get usernames only
-sl     : Time to sleep between requests in seconds. You can use float for subsecond precision. Don't set lower than 2 or reddit servers return error 503 after few tries. Default is 2.
-a      : Start from after specified link. Give in format "t3_xxxxx".
"""

from urllib2 import *
from threading import Thread
from time import time, sleep
from sys import argv, exit
from os import fsync

Starturl='http://www.reddit.com/r/All/'
after=''#Used to get next main page
Pagestoget=-1
limit='100'#Posts per page. Max 100
blacklist=set([])#If user returns 404, add name to this list and don't check it anymore.
sleeptime=3#Don't set lower than 2. Reddit servers don't like it.
min_comments=10#Min comments in thread to crawl it
output='Karma'
Names_only=False

class getkarma(Thread):
    def __init__ (self,name,returnname,format_date):
        Thread.__init__(self)
        self.name = name
        self.status = -1
        self.returnname = returnname
        self.format_date = format_date
    def run(self):
        if self.name not in blacklist:
            def format_time(time1):
                #Return time in days
                return ((int(time())-int(time1))//86400)
            def current_time():
                return str(int(time()))
            try:
                temp=urlopen('http://www.reddit.com/user/'+self.name+'/about.json').read()
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
                if self.format_date==True:
                    created=format_time(created)
                #Users[name]=[link,comment,created]
                if self.returnname==True:
                    self.status=(self.name,link,comment,created,current_time())
                else:
                    self.status=(link,comment,created,current_time())
            except URLError, e:
                    print
                    print 'Error: ' + str(e)
                    print
                    blacklist.add(self.name)

class getusers(Thread):
    def __init__ (self,url):
        Thread.__init__(self)
        self.url = url
    def run(self):
        try:
            temp=urlopen(self.url+'.json').read()
            p=i=10
            users=set([])
            while True:
                p=i+100
                i=temp.find('"author":',p)
                if i==-1:
                    break
                users.add(temp[i+11:temp.find('"',i+12)])
            self.status=users
        except URLError, e:
                print 'Error: ' + str(e)
                self.status=set([])

def main():
    global Starturl,output,Pagestoget,min_comments,Names_only,sleeptime,after
    for i in xrange(1,len(argv)):
            if argv[i] in ("-h", "--help"):
                print __doc__
                exit(0)
            elif argv[i]=='-sr':
                Starturl='http://www.reddit.com/r/'+argv[i+1].replace('r/','').replace('/','')+'/'
            elif argv[i]=='-o':
                output=argv[i+1]
            elif argv[i]=='-p':
                Pagestoget=int(argv[i+1])
            elif argv[i]=='-m':
                min_comments=int(argv[i+1])
            elif argv[i]=='-u':
                Names_only=True
            elif argv[i]=='-sl':
                sleeptime=argv[i+1]
            elif argv[i]=='-a':
                after=argv[i+1]
            elif argv[i][0]=='-':
                print 'Invalid arguments'
                print argv[i]
                quit()



def init():
    global f,user_list2,output
    user_list2=set([])
    try:
        f = open(output, 'r')
        for line in f:
            user_list2.add(line.split(',')[0])
    except IOError:
        print "File doesn't exist"
        f = open(output, 'w')
    except:
        raise
    else:
        print 'File exists'
        print 'Users in file: ' + str(len(user_list2))
        f.close()
        f = open(output, 'a')

def getstories(url):
    global after,user_list
    while True:
        try:
            if after=='':
                temp=urlopen(url+'/.json?limit='+limit).read()
            else:
                temp=urlopen(url+'/.json'+'?after='+after+'&limit='+limit).read()
            break
        except URLError, e:
            print 'Error: ' + str(e.code)
    p=i=20
    urls=[]
    while True:
        i=temp.find('"permalink":',p)
        if i==-1:
            break
        x=temp.find(', "num_comments": ',p)
        if int(temp[x+18:temp.find(',',x+18)])>=min_comments:
            urls.append('http://www.reddit.com'+temp[i+14:temp.find('"',i+15)])
        p=i+10
    after=temp[temp.rfind('"after":')+10:temp.rfind('", "')]
    try:
            p=i=10
            users=set([])
            while True:
                p=i+100
                i=temp.find('"author":',p)
                if i==-1:
                    break
                users.add(temp[i+11:temp.find('"',i+12)])
            user_list=user_list.union(users)
    except URLError, e:
            print 'Error: ' + str(e.code)
    return urls

def writetofile(s):
    global f,Names_only
    if Names_only==False:
        for i in xrange(0,len(s)-1):
            f.write(s[i]+',')
        f.write(s[len(s)-1])
        f.write('\n')
    else:
        f.write(s+'\n')

def crawler():
    global user_list,user_list2
    done=False
    user_list=set([])
    pages=0
    init()
    if after!='':
        print 'Starting from page after ' + after
    while True:
        if pages==Pagestoget:
            break
        pages+=1
        url_list=getstories(Starturl)
        if Pagestoget!=-1:
            print 'Page '+ str(pages)+'/'+str(Pagestoget)
        else:
            print 'Page ' + str(pages)
        try:
            output=[]
            i=0
            for url in url_list:
                i+=1
                print 'Link '+ str(i)+'/'+str(len(url_list))
                current = getusers(url)
                output.append(current)
                sleep(sleeptime)
                current.start()
        except KeyboardInterrupt:
            done=True
            try:
                current.start()
            except:
                pass

        if Names_only==False:
            for i in output:
                i.join()
                try:
                   user_list=user_list.union(i.status)
                except:
                    print 'Thread didn\'t return status'

            if '[deleted]' in user_list:
                user_list.remove('[deleted]')

            #Remove user names already in file
            user_list=user_list-user_list2
            user_list2=user_list2.union(user_list)

            output=[]
            i=0
            l=str(len(user_list))
            for name in user_list:
                try:
                    i+=1
                    current = getkarma(name,True,False)
                    output.append(current)
                    print name,str(i)+'/'+l
                    sleep(sleeptime)
                    current.start()
                except KeyboardInterrupt:
                    done=True
                    break
                except:
                    pass

            for i in output:
                try:
                   i.join()
                   writetofile(i.status)
                except KeyboardInterrupt:
                    done=True
                except:
                    pass
        else:
            for i in output:
                i.join()
                try:
                   user_list=user_list.union(i.status)
                except:
                    print 'Thread didn\'t return status'

            if '[deleted]' in user_list:
                user_list.remove('[deleted]')
            user_list=user_list-user_list2
            user_list2=user_list2.union(user_list)
            for name in user_list:
                    writetofile(name)
        f.flush()
        fsync(f.fileno())
        if done==True:
            print 'Last link was:' + after
            f.close()
            break

if __name__ == "__main__":
    main()
crawler()
