import subprocess
import tempfile
import time
import psutil
import atexit
import threading
import os
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

process_threads = []
pids = []


def shutdown():
     parent = psutil.Process()
     children = parent.children()
     for child in children:
        child.terminate()
     gone, alive = psutil.wait_procs(children)
     print(gone)
     print(alive)
     print('shutdown...')


def wait_process(process, stdout, stderr):
    cwdir = os.getcwd()
    procdir = os.path.join(cwdir, str(process.pid))
    if not os.path.isdir(procdir):
        os.mkdir(procdir, 0o755)
    
    stderrFile = os.path.join(procdir, 'stderr.txt')
    stdoutFile = os.path.join(procdir, 'stdout.txt')
    fileStderr = open(stderrFile, 'wb') 
    fileStdout = open(stdoutFile, 'wb')

    while process.poll() is None:
        where = stdout.tell()
        tmp = stdout.read()
        if not tmp:
            time.sleep(0.1)
            stdout.seek(where)
        else:
            print('stdout')
            fileStdout.write(tmp)
            fileStdout.flush()
        
        where = stderr.tell()
        tmp = stderr.read()
        if not tmp:
            time.sleep(0.1)
            stderr.seek(where)
        else:
            print('stderr')
            fileStderr.write(tmp)
            fileStderr.flush()
    log = stdout.read()
    if log:
        fileStdout.write(log)
        fileStdout.flush()
    log = stderr.read()
    if log:
        fileStderr.write(log)
        fileStderr.flush()             

    pids.remove(process.pid)


class start(Resource):
    def get(self):
        cmd = ["python3", "./test.py"]
        stdoutTmp = tempfile.NamedTemporaryFile()
        stderrTmp = tempfile.NamedTemporaryFile()
        ret = -1
        try:
            p = subprocess.Popen(cmd, stdout=stdoutTmp, stderr=stderrTmp)
            t = threading.Thread(target=wait_process, args=(p, stdoutTmp, stderrTmp))
            process_threads.append(t)
            t.start() 
            pids.append(p.pid)
            ret = p.pid
        except OSError as e:
            print(e)
        except ValueError as e:
            print(e)
        except Exception as e:
            print(e)
        finally:
            return {'task' : ret} 


class status(Resource):
    def get(self):
        return {'tasks': pids}
        

class stop(Resource):
    def get(self, id):
        parent = psutil.Process()
        children = parent.children()
        for child in children:
            if child.pid == id:
                child.terminate()
                child.wait()
                return {'task' : 0 }
        return {'task' : -1}
                 

api.add_resource(start, '/start')
api.add_resource(status, '/status')
api.add_resource(stop, '/stop/<int:id>')
    
if __name__ == '__main__':
    atexit.register(shutdown)
    app.run(debug=True, threaded=True)
