Reddit-Karma-Crawler
====================

Get link and karma counts of reddit users

reddit_karma.py - Crawl reddit for new user accounts.
update.py - Updates karma counts of already existing accounts.

Reddit karma crawler works by opening /r/all or optionally any subreddit, opening top link comment pages
and extracting all reddit user names. Then it loads about.json from every users page. This info includes
link and comment karma and join date, current time is also written so update.py script can update only
accounts older than some specified time.


reddit_karma.py acceps few command line switches:

    -sr : Crawls only links from one subreddit. Default is All
    -h	 : Help
    -o	 : Output filename. Defalt is "Karma". You can also give path to file.
    -p	 : Number of pages to get. 100 links per page. -1 for never stop, which is default
    -m	 : Minimium comments in a thread to open it. Default is 10
    -u	 : Get usernames only
    -sl : Time to sleep between requests in seconds. You can use float for subsecond precision.
          Don't set lower than 2 or reddit servers might ban you.    
    -a  : Start from after specified link. Give in format "t3_xxxxx". Last link is written to stdout, when program exits.
 
 You can stop it any time by pressing C-c. Pressing C-c when loading links will stop the link loading and 
 program begins to get user pages. Pressing C-c again quits the program. All data will be saved.