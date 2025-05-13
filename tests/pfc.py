import time

from picamera2 import Picamera2


def print_info(sync_id, md):
    exp = md['ExposureTime']
    ag = md['AnalogueGain']
    dg = md['DigitalGain']
    print(sync_id, "exp", exp, "ag", round(ag, 2), "dg", round(dg, 2))


def pfc_callback(request):
    md = request.get_metadata()
    sync_id = request.sync_id
    print_info(sync_id, md)


picam2 = Picamera2()
picam2.pre_callback = pfc_callback

controls = {'FrameRate': 30}
config = picam2.create_preview_configuration(controls=controls)
picam2.configure(config)
picam2.start(show_preview=True)

time.sleep(1)

picam2.set_controls({'ExposureTime': 1000, 'AnalogueGain': 3.0})
time.sleep(1)

picam2.set_controls({'ExposureTime': 20000, 'AnalogueGain': 1.3})
time.sleep(1)

sync_id = picam2.set_controls({'ExposureTime': 0, 'AnalogueGain': 0})
time.sleep(0.5)
picam2.capture_request(sync_id=sync_id)
