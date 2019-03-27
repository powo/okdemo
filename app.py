import os
import socket
import time

import psycopg2 as psycopg2
from flask import Flask


app = Flask(__name__)
starttime = time.time()

@app.route('/')
def home():
    ##########################################################################
    # simulate some initial delay until the app is ready to respond
    ##########################################################################
    uptime = time.time() - starttime
    delay = 0 - uptime
    if delay > 0:
        return "503 Sorry, the App needs %d more seconds to boot up" % delay, 503

    s = ''  # collect lines we want to output


    ##########################################################################
    # check if we have Database Credentials
    ##########################################################################
    dbconn = None
    dbhost = os.environ.get('DB_HOST')
    if dbhost:
        try:
            dbconn = psycopg2.connect(
                    host = dbhost,
                    dbname = os.environ.get('DB_NAME', dbhost),
                    user = os.environ.get('DB_USER', dbhost),
                    password = os.environ.get('DB_PASS', ''),
            )
            s+= 'Connected to DB\n'
            # create schema if it does not yet exist
            dbcursor = dbconn.cursor()
            dbcursor.execute('CREATE TABLE IF NOT EXISTS demodb(counter INTEGER)')
            dbconn.commit()
        except Exception as e:
            s += 'Failed to connect to DB: %s\n' % str(e).strip()
    else:
        s += "No DB available\n"


    ##########################################################################
    # Update a counter in DB
    ##########################################################################
    if dbconn:
        dbcursor = dbconn.cursor()
        dbcursor.execute('UPDATE demodb SET counter=counter+1')
        if dbcursor.rowcount < 1:
            dbcursor.execute('INSERT INTO demodb(counter) VALUES(1)')
        dbcursor.execute('SELECT counter FROM demodb LIMIT 1')
        counterval = dbcursor.fetchone()[0]
        dbconn.commit()
        s += "Counter in DB increased to %d\n" % counterval
        dbconn.close()


    ##########################################################################
    # make responses slow and CPU-intensive (200ms loop)
    ##########################################################################
    t1 = time.time()
    while True:
        for _ in range(10000):
            pass
        if (time.time()-t1) > 0.2:
            break
    s += '%dms of hard work done\n' % ((time.time()-t1)*1000)


    ##########################################################################
    # send response
    ##########################################################################
    myhostname = socket.gethostname()
    myip = socket.gethostbyname(myhostname)
    s += "\nServer Hostname: %s\nServer IP: %s\n" % (myhostname, myip)
    return '<pre>%s</pre>Hello World! (uptime:%d)' % (s, uptime)


if __name__ == '__main__':
    app.run()
