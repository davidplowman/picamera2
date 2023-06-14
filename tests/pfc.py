import time
from picamera2 import Picamera2

last_sync_id = 0
last_md = {}

def print_info(sync_id, md):
    exp = md['ExposureTime']
    ag = md['AnalogueGain']
    dg = md['DigitalGain']
    print(sync_id, "exp", exp, "ag", round(ag, 2), "dg", round(dg, 2), end="")

def pfc_callback(request):
    global last_sync_id, last_md
    md = request.get_metadata()
    sync_id = request.sync_id
    if sync_id != last_sync_id:
        print_info(sync_id, md)
        print(" \tpreviously: ", end="")
        print_info(last_sync_id, last_md)
        print("")
    last_md = md
    last_sync_id = sync_id
    
picam2 = Picamera2()
picam2.pre_callback = pfc_callback

picam2.configure()
picam2.start(show_preview=True)

time.sleep(2)

picam2.set_controls({'ExposureTime': 10000})
time.sleep(2)

picam2.set_controls({'ExposureTime': 0, 'AnalogueGain': 1})
time.sleep(2)

sync_id = picam2.set_controls({'ExposureTime': 0, 'AnalogueGain': 0})
picam2.capture_request(sync_id=sync_id)
