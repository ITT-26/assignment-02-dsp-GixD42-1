from midi_song import MidiSong

# tolerance for notematching in semitones
TOLERANCE = 1


class KaraokeGame:
    def __init__(self, song: MidiSong):
        # song to match
        self.song = song
        # score
        self.score = 0
        # max score (for current time, so percentage can always be calculated)
        self.max_score = 0
        # percentage of points achieved
        self.percentage = 0.0
        # current time in seconds
        self.time = 0.0
        # game state
        self.running = False

    def start(self):
        self.running = True
        self.time = 0.0
        self.score = 0
        self.max_score = 0
        self.percentage = 0.0

    # calculate percentage of current performance
    def calculate_percentage(self):
        self.percentage = round(
            self.score / self.max_score * 100, 2) if self.max_score > 0 else 0.0

    # every frame
    def update(self, dt, input_midi):

        # if the game isn't running, don't do anything
        if not self.running:
            return 0

        self.time += dt

        if self.time > self.song.duration:
            self.running = False
            return 0

        current_note = self.song.get_current_note(self.time)

        if current_note is not None:
            self.max_score += 2  # max score for this note

        if input_midi is None or current_note is None:
            return 0

        # calculating distance in semitones and scoring
        dist_semitones = abs(input_midi - current_note)
        # Max points for perfect match (with Tolerance)
        if dist_semitones <= TOLERANCE:
            self.score += 2
            self.calculate_percentage()
            return 2
        # Half points for being somewhat close
        elif dist_semitones <= TOLERANCE * 2:
            self.score += 1
            self.calculate_percentage()
            return 1

        self.calculate_percentage()
        return 0
