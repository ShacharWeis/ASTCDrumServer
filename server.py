import logging 
from logging.handlers import RotatingFileHandler
import rtmidi
import socket
from rtmidi.midiutil import open_midiinput
import configparser
from select import select
import time
import os
from datetime import datetime

def run_loop():
    drum_count=3
    while True:
        c = count_drums()
        if (c==0):
            break
        if (c!=drum_count):
            log("Number of drums has changed from %d to %d." % (drum_count,c))
            if (c>drum_count):
                setup_drums()
            drum_count=c
        time.sleep(1)

def log(s):
    t=datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]
    print(t+' | '+s)
    logging.info(s)

def broadcast(msg):
    log(msg)   
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((IP_address,0))
    sock.sendto(str.encode(msg), ("255.255.255.255", Port))
    sock.close()

def get_device_id(name):
	return name.split(" ")[3]#.replace(":","_")

class MidiInputHandler:
    def __init__(self, name):
        self.name = name
    def __call__(self, event, data=None):
        message, dt = event
        device_id = get_device_id(self.name)
        #drum_number = config["main"][device_id]
        if message[0]==144:
            # msg = Table_Id+"."+drum_number+"."+device_id
            msg = "DRUM."+Table_Id+"."+device_id
            broadcast(msg)

def setup_drums():
    port_names = Midi_In.get_ports()
    for port_name in port_names:
        port, name = open_midiinput(port_name)
        port.set_callback(MidiInputHandler(name))
        if (name.startswith	("BopPad")):
            device_id = get_device_id(name)
            log("Drum %s detected" % (device_id))


def count_drums():
    port_names = Midi_In.get_ports()
    drum_count=0
    for port_name in port_names:
        if (port_name.startswith("BopPad")):
            drum_count += 1
    return drum_count

def log_setup():
    log_handler = logging.handlers.TimedRotatingFileHandler('/home/user/ASTCMidiServer/midiserver.log', when='midnight')
    formatter = logging.Formatter(
        '%(asctime)s program_name [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')
    formatter.converter = time.gmtime  # if you want UTC time
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

# read config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),  'config.ini'))
IP_address = socket.gethostbyname(socket.gethostname() + '.local')
Port = int(config['main']['port']) 
Table_Id = config['main']['table_id'] 
log_setup()
log("Server V1.04 for Table '%s' running on IP Address %s, Port %s" % (Table_Id,IP_address, Port))

# Setup MIDI devices
Midi_In = rtmidi.MidiIn()

setup_drums()

run_loop()

