from flask_script import Manager
from servmon_server.init_socket import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
