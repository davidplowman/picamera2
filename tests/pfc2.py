from numbers import Number
import sys
import time
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_preview_configuration(raw={'size': (1332, 990), 'format': 'SBGGR10_CSI2P'},
                                             buffer_count=3)
picam2.configure(config)
picam2.set_controls({'FrameRate': 120})
picam2.start(show_preview=False)

controls_list = [
    {'ExposureTime': 1000, 'AnalogueGain': 1, 'Saturation': 0.5},
    {'ExposureTime': 2000, 'AnalogueGain': 2, 'Saturation': 0.6},
    {'ExposureTime': 3000, 'AnalogueGain': 3, 'Saturation': 0.7},
    {'ExposureTime': 1000, 'AnalogueGain': 1.1, 'Saturation': 0.8},
    {'ExposureTime': 2000, 'AnalogueGain': 2.1, 'Saturation': 0.9},
    {'ExposureTime': 3000, 'AnalogueGain': 3.1, 'Saturation': 1.0},
    {'ExposureTime': 1000, 'AnalogueGain': 1.2, 'Saturation': 1.1},
    {'ExposureTime': 2000, 'AnalogueGain': 2.2, 'Saturation': 1.2},
    {'ExposureTime': 3000, 'AnalogueGain': 3.2, 'Saturation': 1.3}
    ]

images = []

def callback(ctrl_id, request):
    def do_round(val):
        return round(val, 2) if isinstance(val, Number) else val
    global controls_list
    md = request.get_metadata()
    expected = controls_list[ctrl_id]
    got = {key: do_round(md[key]) for key in expected.keys()}
    print(request.sync_id, ":", got, " expected ", expected)
    thresh = 0.01
    for key in expected.keys():
        if isinstance(got[key], Number) and \
        (got[key] > (1 + thresh) * expected[key] or got[key] < (1 - thresh) * expected[key]):
            print("ERROR - mismatch in setting", key)
            sys.exit(-1)
    images.append(request.make_array('main'))

print(picam2.capture_sequence(controls_list, callback))
