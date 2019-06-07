from tkinter import *
import math
import numpy as np
import copy
import random
import traceback

# Constants
frame_x, frame_y = 1500, 900

# Tkinter Setup
root = Tk()
root.title("Flipnote")
root.resizable(False, False)
root.attributes("-topmost", True)
root.geometry(str(frame_x) + "x" + str(frame_y))  # window size hardcoded
root.configure(background='black')

w = Canvas(root, width=frame_x, height=frame_y)

help_text = 'a: prev page, d: next / new page, c: duplicate page, r: remove page, space: toggle animate, x: toggle eraser'
w.create_text(frame_x/2, frame_y - 40, font=('Avenir', 13), fill='red', text=help_text, tags='instructions')
mouse_loc = [0, 0]


class Point:
    def __init__(self, x, y, num_oval):
        self.x = x
        self.y = y
        self.num_oval = num_oval

    def __str__(self):
        return '('+str(self.x)+', '+str(self.y)+'), num: '+str(self.num_oval)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, item):
        pts = [self.x, self.y]
        return pts[item]

# Data and relevant constants
pages = [[]]
current_page = 0
anim_page = 0
prev_point = None
r = 5

animate = False
erase = False
eraser = None
after = None

# Data file storage setup
file_id = None  # STRING! input a valid file_id to load a file
f = None
loaded_file = True

if not (isinstance(file_id, str) or file_id is None):
    raise TypeError('file_id should be a string!')

if file_id is None:
    loaded_file = False
    file_id = int(random.random()*100000)
    f = open('saved_data%d.txt' % file_id, 'wb')
    np.savetxt(f, [], header="page, x, y\n")
else:
    with open('saved_data%s.txt' % file_id, 'r+') as f:
        line = f.readline()
        while line:
            if not line.startswith('#'):
                data = line.split(' ')
                page_number = float(data[0])
                x = float(data[1])
                y = float(data[2])
                while page_number > len(pages)-1:
                    pages.append([])

                num = w.create_oval(x, y, x + r, y + r, fill='black', outline='')
                if current_page != page_number:
                    w.delete(num)

                pages[int(page_number)].append(Point(x, y, num))

            line = f.readline()

# Create counter
w.create_text(100, 50, font=('Avenir', 40), fill='red', text='Page: %d/%d' % (1, len(pages)), tags='counter')

def reload_counter():
    global current_page, pages
    w.delete('counter')
    w.delete('instructions')
    w.create_text(100, 50, font=('Avenir', 40), fill='red', text='Page: %d/%d' % (current_page+1, len(pages)), tags='counter')
    w.create_text(frame_x / 2, frame_y - 40, font=('Avenir', 13), fill='red', text=help_text, tags='instructions')

def key(event):
    global pages, current_page, animate, erase, eraser, after

    if not animate: # lock controls while animating
        if not erase:
            if event.char == 'a' and current_page > 0:
                current_page -= 1
                reload_drawings()
                reload_counter()
            elif event.char == 'a' and current_page == 0:
                current_page = len(pages) - 1
                reload_drawings()
                reload_counter()

            if event.char == 'd' and current_page < len(pages)-1:
                current_page += 1
                reload_drawings()
                reload_counter()
            elif event.char == 'd' and current_page == len(pages)-1:
                current_page += 1
                pages.append([])
                reload_drawings()
                reload_counter()

            if event.char == '0':
                current_page = 0
                reload_drawings()
                reload_counter()

            if event.char == 'c':
                pages.insert(current_page, copy.deepcopy(pages[current_page]))
                reload_counter()

            if event.char == 'x' and len(pages) > 1:
                pages.remove(pages[current_page])
                current_page = current_page % len(pages)
                reload_drawings()
                reload_counter()

            if event.char == 's':
                save_data()


        if event.char == 'w':
            erase = not erase
            if erase:
                eraser = w.create_oval(mouse_loc[0] - 20, mouse_loc[1] - 20, mouse_loc[0] + 20, mouse_loc[1] + 20, fill='', tag='eraser')
                root.update()
            if not erase:
                w.delete('eraser')
                eraser = None

    if event.char == ' ':
        animate = not animate
        if animate:
            w.delete('eraser')
            eraser = None
            erase = False
            play(20)

        if not animate:
            stop()


def save_data():
    global f, file_id, loaded_file, pages
    try:
        if loaded_file:
            if '(' in file_id:
                p1 = file_id.index('(')
                p2 = file_id.index(')')
                second_id = int(file_id[p1+1:p2]) + 1
                f = open('saved_data%s(%d).txt' % (file_id[:p1], second_id), 'wb')
            else:
                f = open('saved_data%s(%d).txt' % (file_id, 1), 'wb')

            np.savetxt(f, [], header="page, x, y\n")

        for i, page in enumerate(pages):
            for point in page:
                np.savetxt(f, np.column_stack((i, point.x, point.y)), fmt='%f')

    except ValueError:
        print('Encountered error while saving:')
        traceback.print_exc()
    else:
        print('Saved successfully.')


def play(dt):
    global after, anim_page, pages, r, animate

    if animate:
        w.delete('all')
        for point in pages[anim_page]:
            w.create_oval(point[0], point[1], point[0]+r, point[1]+r, fill='black', outline='')

        anim_page = (anim_page + 1) % len(pages)
        root.update()
        after = root.after(dt, lambda: play(dt))

def stop():
    global after, anim_page
    root.after_cancel(after)
    anim_page = 0
    w.delete('all')
    reload_drawings()
    reload_counter()


def reload_drawings():
    global r

    def convert_color(rgb):
        """translates an rgb tuple of int to a tkinter friendly color code.
            From: https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
        """
        return "#%02x%02x%02x" % rgb

    def squash(x):
        return (2. / (1. + math.exp(-max(x, 0)))) - 1

    w.delete('all')
    root.update()
    for i in range(0, current_page):
        # calculate color
        rgb = int(squash(current_page - i) * 255)
        color = convert_color((rgb, rgb, rgb))

        points = pages[i]
        for point in points:
            num = w.create_oval(point[0], point[1], point[0]+r, point[1]+r, fill=color, outline='')
            point.num_oval = num

    for point in pages[current_page]:
        num = w.create_oval(point[0], point[1], point[0]+r, point[1]+r, fill='black', outline='')
        point.num_oval = num

    root.update()


def mouse_click(event):
    global prev_point, r, animate, pages, current_page

    if not animate and not erase:
        prev_point = [event.x, event.y]
        num = w.create_oval(event.x, event.y, event.x + r, event.y + r, fill='black', outline='')
        pages[current_page].append(Point(event.x, event.y, num))


def left_drag(event):
    global prev_point, r, erase, animate, pages, current_page

    if not animate:
        if not erase:
            num = w.create_oval(event.x, event.y, event.x + r, event.y + r, fill='black', outline='')
            pages[current_page].append(Point(event.x, event.y, num))

            min_dist = r/2
            dist = math.sqrt(math.pow(event.x - prev_point[0], 2) + math.pow(event.y - prev_point[1], 2))
            if dist > min_dist:
                if event.x - prev_point[0] == 0:
                    for y in np.arange(prev_point[1], event.y, np.sign(event.y - prev_point[1])):
                        x = event.x
                        num = w.create_oval(x, y, x + r, y + r, fill='black', outline='')
                        pages[current_page].append(Point(x, y, num))
                else:
                    m = (event.y - prev_point[1]) / (event.x - prev_point[0])
                    b = event.y - (m * event.x)

                    delta_x = (r / 2) / math.sqrt(1 + math.pow(m, 2)) # quantity calculated from whiteboard
                    for x in np.arange(prev_point[0], event.x, np.sign(event.x - prev_point[0]) * delta_x):
                        y = (m * x) + b
                        num = w.create_oval(x, y, x+r, y+r, fill='black', outline='')
                        pages[current_page].append(Point(x, y, num))

            prev_point = [event.x, event.y]
        else:
            overlapping = list(w.find_overlapping(*w.bbox(eraser)))
            for i, dot in enumerate(overlapping):
                if i != len(overlapping)-1:
                    for point in pages[current_page]:
                        if point.num_oval == dot:
                            pages[current_page].remove(point)
                            w.delete(dot)

def shift(event):
    pass


def mouse_moved(event):
    global erase, eraser, mouse_loc
    radius = 40

    mouse_loc[0] = event.x
    mouse_loc[1] = event.y

    if animate and eraser:
        eraser = False
        w.delete(eraser)
        eraser = None

    if erase and not animate:
        w.coords(eraser, event.x-(radius/2), event.y-(radius/2), event.x+(radius/2), event.y+(radius/2))

w.bind("<Key>", key)
w.bind("<Button-1>", mouse_click)
w.bind('<B1-Motion>', left_drag)
w.bind('<Shift-1>', shift)
root.bind('<Motion>', mouse_moved)
w.focus_set()
w.pack()


def on_closing():
    global f
    print('closing')
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
mainloop()