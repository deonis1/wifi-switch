import usocket as socket
import utime as time
from machine import Pin
from machine import reset
from machine import Timer
from machine import RTC
import ujson as json
import uos
import gc
from ntptime import settime

class wifi_switch(object):
    def __init__(self):
        self.ip_address = "192.168.0.16"  # set your ip here
        self.port = 80  # set your port here
        pin_id = 4
        self.setlocaltime()
        self.eveton = False
        self.p0 = Pin(pin_id, Pin.OUT)  # 5 in esp-12
        self.p0.value(0)
        self.tim = Timer(-1)
        self.config_json =False
        self.config_file = "config.json"
        if self.exists(self.config_file):
           config_json =  self.loadjson()
           dur = config_json["dur"]
           timer = config_json["timer"]
           self.tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda t: self.running(dur, timer))
        self.conn = None
        self.s = None
        self.run_socket()

    def setlocaltime(self):
        try:
            settime()
            t0 = time.time() - 21600 # Set your time zone here; UTC - 6 hours in this case 
            dt = time.localtime(t0)
            tm = dt[0:3] + (0,) + dt[3:6] + (0,)
            RTC().datetime(tm)
        except OSError:
            time.sleep(3)
            settime()
            t0 = time.time() - 21600
            dt = time.localtime(t0)
            tm = dt[0:3] + (0,) + dt[3:6] + (0,)
            RTC().datetime(tm)
            pass

    def connection(self, html):
        try:
            self.conn.sendall(html)
            time.sleep(0.2)
        except Exception as exc:
            print("Send Error", exc.args[0])
            pass
        finally:
            self.conn.close()

    def running(self, dur, timer):
        if time.localtime()[3] == int((timer.split(":")[0])) and time.localtime()[4] == int((timer.split(":")[1])):
            if not self.eveton:
                self.p0.value(1)
                self.eveton = True
                self.setlocaltime()
                gc.collect()

        else:
            if time.localtime()[3] >= int((timer.split(":")[0])) + int(int(dur) / 3600) and time.localtime()[4] > int(
                    (timer.split(":")[1])):
                if self.eveton:
                    self.p0.value(0)
                    self.eveton = False
                    gc.collect()


    def parse_request(self):
        posted = self.request.find("POSTED")
        if posted > -1:
            l = self.request.split(r'\r\n')
            jl = json.loads((l[-1]).replace("'", ""))
            timer = jl[2]
            dur = int(jl[4])
            config_json = {"timer":timer, "dur":dur}
            self.savejson(config_json)
            print(dur, timer)
            if jl:
                if dur == 0:
                    self.tim.deinit()
                    self.p0.value(0)
                    self.eveton = False
                else:
                    self.tim.init(period=5000, mode=Timer.PERIODIC,
                                  callback=lambda t: self.running(dur, timer))
        self.request = None

    def exists(self, file):
        try:
            uos.stat(file)
            return True
        except:
            return False

    def loadjson(self):
            config = open(self.config_file)
            config_json = json.load(config)
            config.close()
            return config_json

    def savejson(self, config_json):
        config = open(self.config_file, "w")
        json.dump(config_json, config)
        config.close()


    def run_socket(self):
        self.request = None
        self.start = True
        html = None
        try:
            with open("index.html", "r") as fhtml:
                html = fhtml.read()
        except OSError:
            pass
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind((self.ip_address, self.port))
            self.s.listen(5)
        except Exception as exc:
            print("Address in use, restarting", exc.args[0])
            time.sleep(2)
            reset()
            pass
        while True:
            try:
                self.conn, addr = self.s.accept()
                for i in str(self.conn).split():
                    print(i)
            except Exception as exc:
                print("Socket Accept Error ", exc.args[0])
                reset()
                pass
            print('Connected by', addr)
            try:
                self.request = str(self.conn.recv(1024))
            except Exception as exc:
                print("recv -------------", exc.args[0])
                reset()
                pass
            self.parse_request()
            self.connection(html)
