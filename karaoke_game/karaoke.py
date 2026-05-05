import sys
import pyglet
import sounddevice as sd
from midi_song import MidiSong
from voice_translator import VoiceTranslator
from karaoke_game import KaraokeGame
from karaoke_window import KaraokeWindow


if __name__ == "__main__":
    # in command line path to midi
    if len(sys.argv) < 2:
        print("Usage: python karaoke.py <path_to_midi_file>")
        sys.exit(1)

    midi_path = sys.argv[1]

    # load MIDI file
    song = MidiSong(midi_path)

    # select input device
    devices = sd.query_devices()
    print("\nAvailable input devices:")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{i}: {dev['name']}")

    device_id = int(input("\nSelect input device: "))

    # create needed objects
    translator = VoiceTranslator(device_id)
    game = KaraokeGame(song)
    window = KaraokeWindow(game, translator)

    # start game
    pyglet.app.run()
