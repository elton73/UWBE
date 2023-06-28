'''Launch Web App Here
'''
from flask import Flask, request
# from waitress import serve

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # serve(app, host="0.0.0.0", port=5000)





