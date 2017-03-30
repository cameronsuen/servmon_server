from flask import Flask
from flask_cors import CORS
#from flask_socketio import SocketIO
#import servmon_server.updates
from servmon_server import updates
from servmon_server import init_socket

from flask_socketio import SocketIO, send, emit

app = Flask(__name__) 
CORS(app)
app.config['SECRET_KEY']='12345'
socketio = SocketIO(app)
