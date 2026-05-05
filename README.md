[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/B3oR_XLF)

# 0 Requirements and installation

- Python (3.13 used to code this)
- Install requirements using pip install -r requirements.txt

# 1 Karaoke Game

This game works with midis in the format of the ones provided.
To start the game you have to use the following command:

python karaoke_game/karaoke.py "path to midi"
example: python karaoke_game/karaoke.py read_midi/berge.mid

Then you will have a prompt on your command line to choose your desired input device (Code used from audio_sample.py).

After you did that a new window will open and a countdown appears.
When the Countdown is over the game begins. You have to sing the midi you chose.

You will be rewarded for hitting the right notes (with a tolerance). A smaller reward will be given to you if you stay within 2 times the tolerance.
The tolerance is measured in semitones.

Your score will be updated in real time. The percentage displayed will always be your current performance and may drop if you miss notes.

Once the game is finished you can view your score and try it again by pressing the spacebar.

# 2 Whistle Input

To configure the whistle inputs for your own liking you have to follow these steps:
- open whistle_input/chirp_constants.py in an editor and set DEBUG = True
- test your own whistling by running whistle_controller.py (python whistle_input/whistle_controller.py)
- in your command line data of your whistles and their classification will be shown
- play around with the parameters until your up and down chirps get recognized well (the current settings worked well for me)
- after you found the settings that work best for you, set DEBUG = False and you are good to go

Here is an overview over the parameters (that are meant to be changed):
- MIN_VOLUME: minimum volume for detecting sounds
- FREQ_MIN: minimum frequency for detecting sounds
- FREQ_MAX: maximum frequency for detecting sounds
- FLATNESS_THRESHOLD: Maximum spectral threshold. Used to separate speech and background noises (lower -> less background noise, but also more likely to not detect whistling)
- PROMINENCE_FACTOR: Factor of how much higher the peak should be than the average of the spectrum -> reduces chance of other sounds being detected (higher -> less clear whistles might not be detected)
- MAX_HISTORY: Maximum number of frequencies stored (higher -> longer whistles possible)
- MIN_HISTORY: Minimum number of frequencies needed to be considered a whistle
- SILENT_COUNTER_THRESHOLD: Number of consecutive silent frames allowed in a whistle. If these are exceeded the whistle is considered complete.
- SMOOTHING_KERNEL: Used for convolution. Needs to be at least 2 lower than MIN_HISTORY and odd
- DELTA_UP: Minimum positive median frequency change (end-start) in a whistle. Try adjusting this when chirp upwards isn't detected properly
- DELTA_DOWN: Maximum negative median frequency change (end-start) in a whistle. Try adjusting this when chirp downwards isn't detected properly
- UP_STEPS_MIN: Minimum fraction of steps upwards to be considered an upward chirp. Try adjusting this when chirp upwards isn't detected properly
- DOWN_STEPS_MIN: Minimum fraction of steps downwards to be considered a downward chirp. Try adjusting this when chirp downwards isn't detected properly
- DEBUG: determines if prints are enabled

## 2 a

A short demo for a use case was implemented using pyglet.
It uses the configured whistling recognition.

To start the program use the following prompt: python whistle_input/pyglet_demo.py
The Demo window will open after once again choosing the input device in your console.

Controls:
- Chirp down: Rectangle below gets selected
- Chirp up: Rectangle above gets selected

## 2 b

To use the chirps as inputs for the keyboard use the following prompt: python whistle_input/input_simulator.py
you will be once again asked to choose your input device in the command line.

After that your chirps will simulate the up and down keys.
To stop this use Ctrl + C in your command line.