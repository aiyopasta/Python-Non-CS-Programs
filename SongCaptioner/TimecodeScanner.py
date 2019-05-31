from tkinter import *
import numpy as np
import time
import pyglet

# Import music
music = pyglet.resource.media('wiisports.mp3', streaming=False) # the other one is wiimusic.mp3
started = False

frame_x, frame_y = 500, 500
root = Tk()

time_codes = []
start_time = None

# Captions file
captions = []
with open('captions.txt', 'r') as f:
    line = f.readline()
    header = []
    while line:
        if line.startswith('#'):
            header.append(line)
        else:
            captions.extend(line.rsplit())

        line = f.readline()

captions.reverse()
def key_pressed(event):
    global started, start_time
    if not started:
        music.play()
        start_time = time.time()
        started = True

    tc = time.time() - start_time
    print('Timecode added:', tc, 'for caption:', captions.pop())
    time_codes.append(tc)

w = Canvas(root, width=frame_x, height=frame_y)
w.bind("<Key>", key_pressed)
w.bind("<1>", lambda event: w.focus_set())
w.pack()

root.title("Timecode Setter")
root.attributes("-topmost", True)
root.geometry(str(frame_x) + "x" + str(frame_y))  # window size hardcoded

def on_closing():
    print('Time codes:', time_codes)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

mainloop()