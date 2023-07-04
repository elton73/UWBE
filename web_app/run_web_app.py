'''Launch Web App Here. Serves as a host for direct mp3 links.
'''
from flask import Flask
from waitress import serve

app = Flask(__name__)

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
    serve(app, host="0.0.0.0", port=5000)





