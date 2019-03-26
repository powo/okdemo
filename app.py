
import time
from flask import Flask


app = Flask(__name__)
starttime = time.time()


@app.route('/')
def home():
    # simulate some initial delay until the app is ready to respond
    uptime = time.time() - starttime
    delay = 10 - uptime
    if delay > 0:
        return "Sorry, the App needs %d more seconds to boot up" % delay, 503

    # check if we have Database Credentials
    db_params = {
        ''
    }


    return 'Hello World! %d/%d' % (delay, uptime)


if __name__ == '__main__':
    app.run()
