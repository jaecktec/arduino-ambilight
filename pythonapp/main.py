#!/usr/bin/python
import atexit
import cProfile
import io
import pstats
from time import sleep, time

import serial
from PIL import Image
from mss import mss


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

ser = serial.Serial()

config = {
    "loops_per_sec": 10.0,
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
borders = [[0, 0, 0]] * (2 * width + 2 * height)


def do_exit(*args):
    ser.write(b'set 0 \n')


@profile
def loop_step():
    sct_img = sct.grab(screen)
    image = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    image = image.resize((width, height), Image.ANTIALIAS)

    for w in range(width):
        borders[w] = image.getpixel((w, height - 1))
        borders[w + width] = image.getpixel((width - w - 1, 0))
    for h in range(height):
        borders[h + width + height] = image.getpixel((width - 1, height - h - 1))
        borders[h + 2 * width + height] = image.getpixel((0, h))

    # GRB
    colors = list(map(lambda x: '%02x%02x%02x' % (x[1], x[0], x[2]), borders))
    set_colors(colors)


if __name__ == '__main__':
    ser.baudrate = 115200
    ser.port = '/dev/cu.usbserial-011CC9B0'
    ser.open()
    ser.write(b'set 0 \n')
    atexit.register(do_exit)
    interval = 1 / config['loops_per_sec']
    with mss() as sct:
        screen = sct.monitors[config['screen']]
        while True:
            start_time = time()
            loop_step(sct, screen)
            delta_time = time() - start_time
            sleep_time = interval - delta_time
            if sleep_time > 0:
                sleep(sleep_time)
            # else:
            #     print(f'loop time exhausted by {-1 * sleep_time}')
