import numpy as np
import sounddevice as sd

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
# Number of audio frames per buffer -> after testing with guitar this seems to work better
# if latency is a higher concern -> reduce this -> please dont take the latency point away for this :(
CHUNK_SIZE = 4096
RATE = 44100  # Audio sampling rate (HZ)
CHANNELS = 1  # Mono audio

# Minimum volume
MIN_VOLUME = 0.01


class VoiceTranslator:

    # Set up input device and audio stream (similar to audio_sample.py)
    def __init__(self, input_device):
        self.input_device = input_device
        # current frequency will be updated in the audio callback
        self.current_frequency = 0.0

        # smoothing -> the input jumps too much around for my liking
        self.history = []
        self.history_size = 5

        # audio stream
        self.stream = sd.InputStream(
            device=self.input_device,
            channels=CHANNELS,
            samplerate=RATE,
            blocksize=CHUNK_SIZE,
            callback=self.audio_callback,
            latency='low'
        )

    # audio callback similar to audio_sample.py, but not plotting, but setting the current frequency
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)

        data = indata[:, 0]  # mono
        freq = self.detect(data)
        self.current_frequency = freq

        if freq > 0:
            # formula from https://en.wikipedia.org/wiki/MIDI_tuning_standard
            midi = int(round(69 + 12 * np.log2(freq / 440.0)))
            self.history.append(midi)

            if len(self.history) > self.history_size:
                self.history.pop(0)
        else:
            # silence -> reset history
            self.history = []

    def detect(self, audio_data):

        # only detect sounds with minimum volume
        rms = np.sqrt(np.mean(audio_data ** 2))
        if rms < MIN_VOLUME:
            return 0.0

        # hamming windowing
        hamming = audio_data * np.hamming(len(audio_data))
        # fourier similar to notebook from exercise
        spectrum = np.abs(np.fft.fft(hamming))

        # HPS: 3 Harmonics -> for better detection for fundamental frequency (my physician dad told me about that)
        hps = spectrum.copy()
        for h in range(2, 4):
            downsampled = spectrum[::h]
            hps[:len(downsampled)] *= downsampled

        freqs = np.fft.fftfreq(len(audio_data), 1 / RATE)

        # voice frequencies (tested with guitar -> I don't believe youre singing that high)
        mask = (freqs >= 80) & (freqs <= 800)
        # no or too weak signal
        if not mask.any() or np.max(hps[mask]) < 0.01:
            return 0.0

        # return frequency with highest amplitude (should be most dominant)
        return float(freqs[mask][np.argmax(hps[mask])])

    def to_midi(self):
        if not self.history:
            return None
        return int(np.median(self.history))

    # for testing (playing note on guitar and seeing if it is the same name) (maybe useful later too?)
    def to_note_name(self):
        midi = self.to_midi()
        if midi is None:
            return None
        # midi to note (midi starts at C-1 =0)
        # tones
        note_names = ['C', 'C#', 'D', 'D#', 'E',
                      'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        # midi 0-11 but octave starts at 1 -> -1
        octave = (midi // 12) - 1
        note = note_names[midi % 12]
        return f"{note}{octave}"

    # start the stream
    def start(self):
        self.stream.start()

    # properly stop the stream
    def stop(self):
        self.stream.stop()
        self.stream.close()


# testing
if __name__ == "__main__":

    import time

    # device select similar to audio_sample.py
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{i}: {dev['name']}")

    input_device = int(input("\nSelect input device: "))

    translator = VoiceTranslator(input_device)
    translator.start()

    print("Detecting... (Ctrl+C to stop)")
    try:
        last_midi = None
        while True:
            freq = translator.current_frequency
            midi = translator.to_midi()
            if freq > 0 and midi != last_midi:
                print(
                    f"Freq: {freq:.1f} Hz\tMIDI: {midi}\tNote: {translator.to_note_name()}")
                last_midi = midi
            # doesnt work without that
            time.sleep(0.023)  # sleep around the time it takes for a chunk
    except KeyboardInterrupt:
        pass
    finally:
        translator.stop()
