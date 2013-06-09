#!/usr/bin/env python

from pprint import pprint
import curses

class Curses(object):

    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        self.screen.keypad(1)

    def add(self, s, x=None, y=None):
        if x is not None and y is not None:
            self.screen.addstr(x, y, s)
        else:
            self.screen.addstr(s)

    def getch(self):
        return self.screen.getch()

    def __del__(self):
        curses.endwin()



c = Curses()

c.add('Hello World!')

count = 0
run = True
while run:
    c.add(str(count), 10, 10)
    run = c.getch() != ord('q')
    count += 1
