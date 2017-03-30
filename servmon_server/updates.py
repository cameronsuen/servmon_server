from flask_socketio import SocketIO, send, emit
from servmon_server.init_socket import socketio
import time
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

thread = None
scheduler = BackgroundScheduler()
pid = 533

@socketio.on('connect')
def onConnect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=backgroundThread)

def sendUpdates():
    cpu = open('/proc/stat', 'r')
    ram = open('/proc/meminfo', 'r')
    process = open('/proc/' + str(pid) + '/stat')
    process_uid = open('/proc/' + str(pid) + '/status')
    p_out = process.readlines()

    for line in process_uid.readlines():
        if line.startswith('Uid') or line.startswith('Gid'):
            p_out.append(line)

    harddisk = subprocess.check_output(['df', '-h'])
    socketio.emit('updates', {'timestamp': time.time(), 'cpu': dict(l.strip().split(' ', maxsplit=1) for l in cpu.readlines()), 'ram': dict(l.strip().split(':') for l in ram.readlines()), 'process': p_out, 'harddisk': harddisk.decode('utf-8').split('\n')})

    cpu.close()
    ram.close()
    process.close()
    process_uid.close()

def backgroundThread():
    scheduler.add_job(sendUpdates, 'cron', second='*/30')
    scheduler.start()
