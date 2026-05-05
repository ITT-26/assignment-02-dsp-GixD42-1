import pyglet
import sounddevice as sd

from whistle_controller import WhistleController


# print info about audio devices
print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

# let user select audio device
input_device = int(input("\nSelect input device: "))


# constants for pyglet
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
NUM_RECTANGLES = 5
RECT_HEIGHT = 50
RECT_WIDTH = 100
RECT_GAP = 10


# window
window = pyglet.window.Window(
    WINDOW_WIDTH, WINDOW_HEIGHT, caption="Whistle Controller Demo")

# starting rectangle (highest)
selected_index = NUM_RECTANGLES - 1


# rectangle list
rectangles = []

# for calculating y positions of rectangles
total_height = NUM_RECTANGLES * RECT_HEIGHT + (NUM_RECTANGLES - 1) * RECT_GAP
# y position to start, so that everything is centered
start_y = (WINDOW_HEIGHT - total_height) // 2
# x position chosen to center the rectangles
x = (WINDOW_WIDTH - RECT_WIDTH) // 2

# set rectangle positions
for i in range(NUM_RECTANGLES):
    y = start_y + i * (RECT_HEIGHT + RECT_GAP)
    rect = pyglet.shapes.Rectangle(
        x, y, RECT_WIDTH, RECT_HEIGHT, color=(80, 80, 80))
    rectangles.append(rect)


# change colors based on selected index
def update_colors():
    for i, rect in enumerate(rectangles):
        rect.color = (255, 0, 0) if i == selected_index else (80, 80, 80)


# draws rectangles
@window.event
def on_draw():
    window.clear()
    for rect in rectangles:
        rect.draw()


# callback -> up and down for controlling selected rectangle
def on_chirp(direction):
    global selected_index
    if direction == "up":
        selected_index = min(NUM_RECTANGLES - 1, selected_index + 1)
    elif direction == "down":
        selected_index = max(0, selected_index - 1)
    update_colors()


# initial color update
update_colors()


controller = WhistleController(input_device=input_device, onchirp=on_chirp)
controller.start()
pyglet.app.run()
