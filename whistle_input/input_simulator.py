import time
import sounddevice as sd
from pynput.keyboard import Controller, Key

from whistle_controller import WhistleController

# controller for pynput
keyboard = Controller()


# chirp callback -> tap corresponding key
def on_chirp(direction):
    if direction == "up":
        keyboard.tap(Key.up)
    elif direction == "down":
        keyboard.tap(Key.down)


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


# whistle controller with callback
controller = WhistleController(input_device=input_device, onchirp=on_chirp)
controller.start()
print("Running... Ctrl+C to stop")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    controller.stop()
