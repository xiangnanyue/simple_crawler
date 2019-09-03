# Web Crawler via ip proxy
A simple and flexible web crawler API via python scripts and postgres database.  
It turns out that database is an essential part of web crawling since it provides an elegant way to store, manage and retrieve
data with column indexing, data recovery and so on. With the help of database, it is easy to launch multiple processes at one time without interfering each other. 
## Task list
To begin with, we can also store a task list in database. Each task can be marked with its corresponding working status, 
e.g. 0 for "to do", 1 for "done", 2 for "error", etc.
## Procedure 
The main procedure works as follows:  
We fetch a "to do" task with an ip proxy. While fetching, use "for update" phrase in postgres sql to lock the row 
in task table so that while one process is taking the job, other processes won't take and repeat the same work.  
When a task is finished, its status will be updated (it can either be "done" or "error"), and crawling result is written back to database.
## Implementation
You can implement your own concrete examples following an abstract class in core/task_abc.py.
## Caution
Be polite when you do web crawling.
## Advanced
If the task list is too long, you might consider distributed web crawling via cloud computing.
## Other
Sometimes, you might need ip proxy and webdriver to help.