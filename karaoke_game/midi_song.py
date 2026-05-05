import mido
from mido import MidiFile


class MidiSong:
    def __init__(self, file_path):
        # List in format: (start_sec, midi_note, duration_sec)
        self.notes = []
        self.load(file_path)

    def load(self, file_path):
        midi = MidiFile(file_path)
        # default tempo 120 bpm -> 500000 microseconds per beat
        tempo = 500000
        current_time = 0.0
        active_notes = {}

        # iterate over midi track
        for msg in midi.merged_track:
            # current time in seconds
            current_time += mido.tick2second(msg.time,
                                             midi.ticks_per_beat, tempo)

            # adjust tempo to midi -> if not specified it is 120 bpm and the standard value is used
            if msg.type == "set_tempo":
                tempo = msg.tempo

            # note on -> add to active notes with start time
            elif msg.type == "note_on" and msg.velocity > 0:
                active_notes[msg.note] = current_time

            # note off -> calculate duration and add to notes list
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active_notes:
                    start = active_notes.pop(msg.note)
                    duration = current_time - start
                    self.notes.append((start, msg.note, duration))

        # sort notes by start time
        self.notes.sort(key=lambda n: n[0])
        self.duration = current_time

    # get the current note
    def get_current_note(self, elapsed_time):
        for start, note, duration in self.notes:
            # return note if elapsed time is within the notes duration
            if start <= elapsed_time <= start + duration:
                return note
        # note not found
        return None
