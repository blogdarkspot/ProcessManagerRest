import signal
import subprocess


def handler_signal(signal, frame):
    print(signal)
    print(frame)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handler_signal)
    proc = subprocess.Popen(['/bin/sleep', '2'])    
    name = input()
