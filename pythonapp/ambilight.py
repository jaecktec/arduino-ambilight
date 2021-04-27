#!/usr/bin/python
import atexit
import cProfile
import io
import pstats
from proto.z_message_pb2 import SetColorMessage, MessageColor
from time import sleep, time
import math
import d3dshot

from PIL import Image
from mss import mss
from socket import socket, AF_INET, SOCK_DGRAM
import threading

IPADDR = '192.168.188.50'
PORTNUM = 1234
d = d3dshot.create()


def profile(fnc):
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


config = {
    "loops_per_sec": 15,
    "numLedsWidth": 31,
    "numLedsHeight": 21,
    "screen": 1
}


def crop_dimensions(screen, factor):
    return {
        'left': int(screen['width'] / 2 - screen['width'] / (2 * factor) + screen['left']),
        'top': int(screen['height'] / 2 - screen['height'] / (2 * factor) + screen['top']),
        'width': int(screen['width'] / factor), 'height': int(screen['height'] / factor)
    }


def set_colors(colors):
    commands = ''.join(f'set {str(i)} {c} \n' for i, c in enumerate(colors, start=1))
    ser.write(commands.encode())


width = config['numLedsWidth']
height = config['numLedsHeight']
num_leds = (2 * width + 2 * height)
borders = [[0, 0, 0]] * num_leds

BOTTOM = [[0, 0, 0]] * config['numLedsWidth']
RIGHT = [[0, 0, 0]] * config['numLedsHeight']
TOP = [[0, 0, 0]] * config['numLedsWidth']
LEFT = [[0, 0, 0]] * config['numLedsHeight']


def create_color_message_entry(x):
    color = MessageColor()
    color.R = x[1]
    color.G = x[0]
    color.B = x[2]
    return color


def set_color(color):
    sock = socket(AF_INET, SOCK_DGRAM, 0)
    sock.connect((IPADDR, PORTNUM))
    lightstrip = [color] * num_leds
    colors = [create_color_message_entry(x) for x in lightstrip]
    message = SetColorMessage()
    message.colors.extend(colors)
    message.brightness = 255
    sock.send(message.SerializeToString())
    sock.close()
    pass


class CaptureBordersThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.sock = socket(AF_INET, SOCK_DGRAM, 0)

    def stop(self):
        self.running = False
        pass

    # @profile
    def run(self):
        self.sock.connect((IPADDR, PORTNUM))

        interval = 1 / config['loops_per_sec']
        while self.running:
            start_time = time()
            image = d.screenshot()
            image = image.resize((width, height), Image.NEAREST)

            for w in range(config['numLedsWidth']):
                BOTTOM[w] = image.getpixel((w, config['numLedsHeight'] - 1))
                TOP[w] = image.getpixel((config['numLedsWidth'] - w - 1, 0))

            for h in range(config['numLedsHeight']):
                RIGHT[h] = image.getpixel((config['numLedsWidth'] - 1, config['numLedsHeight'] - h - 1))
                LEFT[h] = image.getpixel((0, h))

            lightstrip = []
            lightstrip += BOTTOM
            lightstrip += RIGHT
            lightstrip += TOP
            lightstrip += LEFT

            colors = [create_color_message_entry(x) for x in lightstrip]
            message = SetColorMessage()
            message.colors.extend(colors)
            message.brightness = 255
            self.sock.send(message.SerializeToString())

            delta_time = time() - start_time
            sleep_time = interval - delta_time
            if sleep_time > 0:
                sleep(sleep_time)
            else:
                print(f'loop time exhausted by {-1 * sleep_time}')


if __name__ == '__main__':
    capture_process = CaptureBordersThread()
    write_process = UpdateColorsThread()
    capture_process.start()
    write_process.start()
    capture_process.join()
    write_process.join()

    pass
