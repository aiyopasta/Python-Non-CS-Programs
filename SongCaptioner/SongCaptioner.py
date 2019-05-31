from tkinter import *
import numpy as np
import time

# Constants
frame_x, frame_y = 1440, 900

# Tkinter Setup
root = Tk()

w = Canvas(root, width=frame_x, height=frame_y)

root.title("Text Captioner")
# root.attributes("-topmost", True)
root.geometry(str(frame_x) + "x" + str(frame_y))  # window size hardcoded

# Main layout setup
w.create_rectangle(0, 0, frame_x, frame_y, fill='green')

black_buffer = 150
w.create_rectangle(0, 0, frame_x, black_buffer, fill='black')
w.create_rectangle(0, frame_y-black_buffer, frame_x, frame_y, fill='black')

# Read from textfile
captions = []
with open('captions.txt', 'r') as f:
    line = f.readline()
    header = []
    while line:
        if line.startswith('#'):
            header.append(line)
        else:
            captions.append(line.rsplit())

        line = f.readline()

# Label group structure
class LabelGroup():
    def __init__(self, word_list, font=30, spacing=20):
        self.word_list = word_list
        self.spacing = spacing
        self.labels = []
        self.total_width = spacing * (len(word_list) - 1)
        self.total_height = None

        for word in word_list:
            label = Label(root, text=word, font=('Avenir', font), fg='white', bg='black')
            self.labels.append(label)

            label.place(x=-100, y=-100) # dummy location
            root.update()
            self.total_width += label.winfo_width()
            self.total_height = label.winfo_height()

    def draw_caption(self):
        x_offset = -self.total_width / 2
        y_offset = -self.total_height /2
        x = (frame_x / 2) + x_offset
        y = frame_y - (black_buffer/2) + y_offset

        for label in self.labels:
            label.place(x=x, y=y)
            x += label.winfo_width() + self.spacing

        root.update()

    def remove_caption(self):
        for label in self.labels:
            label.destroy()

    def get_bouncer_locs(self, width=10, height=10, height_buffer=10):
        # The bouncer is the thing that ``bounces'' over the text as its being sung.
        locs = []
        for label in self.labels:
            x0 = label.winfo_x() + (label.winfo_width()/2) - (width/2)
            y0 = label.winfo_y() - height_buffer - height
            x1 = label.winfo_x() + (label.winfo_width()/2) + (width/2)
            y1 = label.winfo_y() - height_buffer
            locs.append([x0, y0, x1, y1])

        return locs


# A bouncer is the thing that ``bounces'' over the text as its being sung.
class Bouncer:
    def __init__(self, width, height, height_buffer=5, color='red'):
        self.width = width
        self.height = height
        self.height_buffer = height_buffer
        self.color = color

        self.coeffs = None

    def bounce_prep(self, p1, p2, bounce_height=15):
        p3 = [(p1[0] + p2[0]) / 2, p1[1] - bounce_height]
        self.coeffs = np.polyfit([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], deg=2)

    def bounce_step(self, x):
        return (self.coeffs[0]*(x**2)) + (self.coeffs[1]*x) + self.coeffs[2]

def wait(until_time):
    while time.time() < until_time:
        pass

def main(event):
    # Start music
    import pyglet
    music = pyglet.resource.media('wiisports.mp3', streaming=False) # the other one is wii sports
    music.play()

    # Time codes for wii mii music:
    # time_codes = np.array([6.9141387939453125e-06, 1.0558111667633057, 1.3467330932617188, 1.8863098621368408, 2.3837809562683105, 2.670012950897217, 2.9163589477539062, 3.1894190311431885, 5.060675144195557, 5.325214862823486, 5.581151008605957, 6.120630979537964, 6.902083158493042, 9.036263942718506, 9.545845031738281, 9.808182001113892, 10.324164867401123, 10.836302757263184, 11.361104965209961, 11.879215955734253, 12.152148962020874, 12.663172960281372, 12.920014142990112, 13.213198184967041, 13.477240085601807, 13.740917921066284, 14.745336055755615, 15.03515076637268, 15.287032127380371, 17.390365839004517, 17.918120861053467, 18.185786962509155, 18.71657395362854, 19.223264932632446, 19.513283014297485, 19.77398705482483, 20.050365924835205, 20.55309796333313, 20.794111013412476, 21.071122884750366, 21.89509391784668, 22.157872915267944, 22.400957822799683, 22.911581993103027, 23.41508984565735, 24.585880041122437, 24.844856023788452, 25.835243940353394, 26.341859817504883, 26.626954078674316, 27.158182859420776, 27.69097089767456, 27.96550989151001, 28.460943937301636, 28.748942136764526, 30.052278995513916, 30.29665493965149, 30.57878613471985, 31.54110288619995, 32.1120331287384, 32.623164892196655, 32.906936168670654, 33.21076679229736, 35.451825857162476, 35.85383892059326, 36.325817823410034, 38.910887002944946, 39.47808313369751, 39.7667441368103, 40.28000473976135, 40.55264592170715, 43.7137348651886, 44.22765398025513, 44.75776386260986, 45.52080297470093, 45.81482791900635, 47.43845081329346, 47.938698053359985, 48.46553587913513, 48.97448492050171, 52.08074998855591, 52.3915069103241, 52.65446186065674])
    # Time codes for wii sports music:
    time_codes = np.array([7.867813110351562e-06, 0.588676929473877, 0.9943070411682129, 1.3652749061584473, 1.6234638690948486, 6.514800071716309, 7.509671926498413, 8.287489891052246, 8.546714067459106, 8.901755094528198, 9.2744460105896, 9.554252862930298, 9.909250974655151, 10.546501874923706, 10.933196067810059, 11.668859720230103, 14.541089057922363, 15.517883062362671, 16.50391912460327, 17.218474864959717, 17.507601737976074, 18.237799882888794, 18.428513050079346, 18.64470386505127, 18.95769190788269, 19.36687994003296, 19.626702070236206, 20.062455892562866, 20.76489806175232, 21.087857961654663, 22.311403036117554, 22.43820595741272, 22.562134981155396, 22.91324210166931, 23.326291799545288, 23.58819890022278, 24.067970991134644, 26.36489486694336, 26.576310873031616, 26.94100284576416, 27.347012996673584, 27.6209979057312, 27.829124927520752, 28.088945865631104, 30.522809982299805, 30.900909900665283, 31.302875757217407, 32.58278298377991, 32.97794198989868, 33.33659887313843, 33.586827993392944, 34.00707197189331, 34.407861948013306, 34.7956280708313, 35.168740034103394, 35.55495095252991, 35.978606939315796, 36.59893083572388, 40.05614399909973, 40.3607919216156, 40.604130029678345, 41.24262499809265, 41.585675954818726])

    time_codes = time_codes - 0.
    tc = 0
    start_time = time.time()
    for i, line in enumerate(captions):
        label_group = LabelGroup(line, spacing=5)
        label_group.draw_caption()

        # For Regular oval bouncer:
        # bouncer = Bouncer(10, 10)
        # oval = w.create_oval(*label_group.get_bouncer_locs(height_buffer=bouncer.height_buffer)[0], fill=bouncer.color)

        # For arbitrary image:
        bouncer = Bouncer(40, 40, height_buffer=0)
        photo = PhotoImage(file=r"matt.gif")
        oval = w.create_image(*label_group.get_bouncer_locs(bouncer.width, bouncer.height, bouncer.height_buffer)[0][:2], image=photo, anchor='nw')

        root.update()

        wait(start_time + time_codes[tc+1])
        tc += 1

        bouncer_word = 0  # which word the bouncer is at. Increments after a bounce.
        while bouncer_word < len(line)-1:
            t = 0  # variable used to parametrize curve

            # Fit quadratic curve
            p1 = label_group.get_bouncer_locs(bouncer.width, bouncer.height, bouncer.height_buffer)[bouncer_word][:2]
            p2 = label_group.get_bouncer_locs(bouncer.width, bouncer.height, bouncer.height_buffer)[bouncer_word+1][:2]
            bouncer.bounce_prep(p1, p2)

            while t < 1:
                horiz_dist_between = p2[0] - p1[0]
                x = p1[0] + horiz_dist_between*t
                y = bouncer.bounce_step(x)

                # For regular oval bouncer:
                # w.coords(oval, x, y, x+bouncer.width, y+bouncer.height)

                # For arbitrary image:
                w.coords(oval, x, y)

                root.update()

                t += 0.08
                time.sleep(0.001)

            # Bounce finished
            bouncer_word += 1
            wait(start_time + time_codes[tc + 1])
            tc += 1

        # Line finished
        w.delete(oval)
        label_group.remove_caption()

if __name__ == '__main__':
    w.bind("<Key>", main)
    w.bind("<1>", lambda event: w.focus_set())
    w.pack()
    print("Press any key to start.")

mainloop()