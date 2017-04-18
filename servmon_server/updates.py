from flask_socketio import SocketIO, send, emit
from servmon_server.init_socket import socketio
import time
import subprocess
import re
import sysconfig
from apscheduler.schedulers.background import BackgroundScheduler

thread = None
scheduler = BackgroundScheduler()
pid = -2 
processName = ''

""" Get group name based on gid """
def getGroup(gid):
    ps = subprocess.Popen(['getent', 'group', gid], stdout=subprocess.PIPE)
    group = subprocess.check_output(['cut', '-d:', '-f', '1'], stdin=ps.stdout)
    return group.decode('utf-8').replace('\n', '')

""" Get user name based on uid """
def getUser(uid):
    ps = subprocess.Popen(['getent', 'passwd', uid], stdout=subprocess.PIPE)
    user = subprocess.check_output(['cut', '-d:', '-f', '1'], stdin=ps.stdout)
    return user.decode('utf-8').replace('\n', '')
    #user = subprocess.check_output(['getent', 'passwd', uid, '|', 'cut', '-d:', '-f', '1'])
    #return user.decode('utf-8')

@socketio.on('connect')
def onConnect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=backgroundThread)

@socketio.on('process_change')
def onProcessChange(json):
    print('here')
    global pid
    global processName
    processName = json['processName']
    result = subprocess.check_output('ps -A | awk \'$4=="' + processName + '" {print $1; exit}\'', shell=True)
    if result == b'':
        pid = -1
        print('PID: ' + str(pid))
    else:
        pid = int(result.decode('utf-8').replace('\n', ''))


def sendUpdates():
    global pid
    result = subprocess.check_output('ps -A | awk \'$1==' + str(pid) + ' {print $1; exit}\'', shell=True)
    if result == b'':
        print('Is empty')
        pid = -1

    # -2 means does not receive instruction from client about which process to fetch yet 
    if pid != -2:
        cpu = open('/proc/stat', 'r')
        cpuinfo = open('/proc/cpuinfo', 'r')
        cpuinfo_stripped = []
        ram = open('/proc/meminfo', 'r')

        # -1 means the process is not executing
        if pid != -1:
            process = open('/proc/' + str(pid) + '/stat')
            process_uid = open('/proc/' + str(pid) + '/status')
            p_out = process.readlines()

            for line in process_uid.readlines():
                if line.startswith('Uid'):
                    info = line.split('\t')
                    real_user = getUser(info[1])
                    effective_user = getUser(info[2])

                    p_out.append(info[1] + '(' +  effective_user + ')/' + info[2] + '(' + real_user + ')')

                elif line.startswith('Gid'):
                    info = line.split('\t')
                    real_group = getGroup(info[1])
                    effective_group = getGroup(info[2])

                    p_out.append(info[1] + '(' +  effective_group + ')/' + info[2] + '(' + real_group + ')')

            # Get memory usage of the process
            p_ram = re.sub(' +', ' ', subprocess.check_output(['pmap', '-x', str(pid)]).decode('utf-8').split('\n')[-2]).split(' ')[3]
            p_out.append(p_ram)
            process.close()
            process_uid.close()
        else:
            p_out = False

        for line in cpuinfo.readlines():
            if 'MHz' in line:
                cpuinfo_stripped.append(line.replace(' ', '').replace('\n', '').split(':')[-1])


        harddisk = subprocess.check_output(['df', '-h', '--total'])


        socketio.emit('updates', {'timestamp': time.time(), 'cpu': dict(l.strip().split(' ', maxsplit=1) for l in cpu.readlines()), 'cpuinfo': cpuinfo_stripped, 'ram': dict(l.strip().split(':') for l in ram.readlines()), 'process': p_out, 'harddisk': harddisk.decode('utf-8').split('\n')})

        print(p_out)

        cpu.close()
        ram.close()

def backgroundThread():
    #scheduler.add_job(sendUpdates, 'cron', second='*/30')
    scheduler.add_job(sendUpdates, 'cron', second='*/5')
    scheduler.start()
