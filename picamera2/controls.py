#!/usr/bin/python3
from libcamera import ControlType, Rectangle, Size


class Controls():
    def _framerates_to_durations_(framerates):
        if not isinstance(framerates, (tuple, list)):
            framerates = (framerates, framerates)
        return (int(1000000 / framerates[1]), int(1000000 / framerates[0]))

    def _durations_to_framerates_(durations):
        if durations[0] == durations[1]:
            return 1000000 / durations[0]
        return (1000000 / durations[1], 1000000 / durations[0])

    _VIRTUAL_FIELDS_MAP_ = {"FrameRate": ("FrameDurationLimits", _framerates_to_durations_, _durations_to_framerates_)}

    def __init__(self, picam2, controls={}):
        self._camera_ctrl_info = picam2.camera_ctrl_info
        self._controls = []
        # We're using the Picamera2's global controls lock.
        self._controls_lock = picam2._controls_lock
        self._set_controls(controls)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            if name in Controls._VIRTUAL_FIELDS_MAP_:
                real_field = Controls._VIRTUAL_FIELDS_MAP_[name]
                name = real_field[0]
                value = real_field[1](value)
            if name not in self._camera_ctrl_info.keys():
                raise RuntimeError(f"Control {name} is not advertised by libcamera")
            self._controls.append(name)
        self.__dict__[name] = value

    def __getattribute__(self, name):
        if name in Controls._VIRTUAL_FIELDS_MAP_:
            real_field = Controls._VIRTUAL_FIELDS_MAP_[name]
            real_value = self.__getattribute__(real_field[0])
            return real_field[2](real_value)
        return super().__getattribute__(name)

    def __repr__(self):
        return f"<Controls: {self.make_dict()}>"

    def __enter__(self):
        self._controls_lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._controls_lock.release()

    def set_controls(self, controls):
        with self._controls_lock:
            self._set_controls(controls)

    def _set_controls(self, controls):
        if isinstance(controls, dict):
            for k, v in controls.items():
                self.__setattr__(k, v)
        elif isinstance(controls, Controls):
            for k in controls._controls:
                v = controls.__dict__[k]
                self.__setattr__(k, v)
        else:
            raise RuntimeError(f"Cannot update controls with {type(controls)} type")

    def get_libcamera_controls(self):
        # The caller must hold the controls lock
        def list_or_tuple(thing):
            return type(thing) in {list, tuple}

        libcamera_controls = {}
        for k in self._controls:
            v = self.__dict__[k]
            id = self._camera_ctrl_info[k][0]
            if id.type == ControlType.Rectangle:
                # We can get a list of Rectangles or a single one.
                if list_or_tuple(v) and v and list_or_tuple(v[0]):
                    v = [Rectangle(*i) for i in v]
                else:
                    v = Rectangle(*v)
            elif id.type == ControlType.Size:
                v = Size(*v)
            libcamera_controls[id] = v
        return libcamera_controls

    def make_dict(self):
        dict_ = {}
        for k in self._controls:
            v = self.__dict__[k]
            dict_[k] = v
        return dict_
