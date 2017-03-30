from flask import Flask
from servmon_server import updates
from servmon_server.init_socket import socketio
from servmon_server.init_socket import app as application
from flask_socketio import SocketIO, send, emit

import eventlet

if __name__ == '__main__':
    socketio.run(application)

    while True:
        print('here')
        file_obj = open('/proc/stat', 'r')
        data = file_obj.read()
        socketio.emit('updates', {'data': data})
        sleep(60)
