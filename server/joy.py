#!/usr/bin/env python

from sense_emu import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from time import sleep

import json

x = 0
y = 0
c = 0

def main():
    sense = SenseHat()

    def pushed_up(event):
        global y
        if event.action != ACTION_RELEASED:
            y = y + 1

    def pushed_down(event):
        global y
        if event.action != ACTION_RELEASED:
            y = y - 1

    def pushed_left(event):
        global x
        if event.action != ACTION_RELEASED:
            x = x - 1

    def pushed_right(event):
        global x
        if event.action != ACTION_RELEASED:
            x = x + 1
            
    def pushed_middle(event):
        global c
        if event.action != ACTION_RELEASED:
            c = c + 1

    def write_to_file():
        data = {'x': x, 'y': y, 'c': c}
        json_data = json.dumps(data)
        print(json_data)
        #f.write('\n'.join(json_data))
        with open('joystick.dat', 'a') as f:
            f.write(json_data + '\n')

    sense.stick.direction_up = pushed_up
    sense.stick.direction_down = pushed_down
    sense.stick.direction_left = pushed_left
    sense.stick.direction_right = pushed_right
    sense.stick.direction_middle = pushed_middle
    sense.stick.direction_any = write_to_file

    while True:
        write_to_file()
        sleep(0.05)
    f.close()

if __name__ == '__main__':
    main()

