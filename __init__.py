from flask import Flask

app = Flask(__name__)
app.debug = True

import Twidder.views

if __name__ == '__main__':
    app.run()
