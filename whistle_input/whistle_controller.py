import numpy as np
import sounddevice as sd

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
# Chunk size lower, so we get more frequent updates -> better for chirps (in testing)
CHUNK_SIZE = 512  # Number of audio frames per buffer
RATE = 44100  # Audio sampling rate (HZ)
CHANNELS = 1  # Mono audio

MIN_VOLUME = 0.01

DEBUG = True


class WhistleController:
    def __init__(self, input_device, onchirp=None):
        self.input_device = input_device

        self.onchirp = onchirp

        # history of the last frequencies
        self.history = []
        self.max_history = 20

        # silence for a single frame shouldnt count as a break in the whistle -> counter for silent frames
        self.silent_counter = 0
        # if counter is above -> break in whistle
        self.silent_counter_threshold = 3

        # audio stream
        self.stream = sd.InputStream(
            device=self.input_device,
            channels=CHANNELS,
            samplerate=RATE,
            blocksize=CHUNK_SIZE,
            callback=self.audio_callback,
            latency='low'
        )

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)

        data = indata[:, 0]  # mono
        freq = self.detect(data)

        if freq is not None:
            self.history.append(freq)
            self.silent_counter = 0
        # No sound
        else:
            # silent frame
            self.silent_counter += 1
            # Detected break in whistle -> interpret history
            if self.silent_counter >= self.silent_counter_threshold:
                # check if the whistle was long enough
                if len(self.history) >= 5:
                    direction = self.interpret_history()
                    # if a chirp is interpreted -> callback function (used for controls)
                    if direction:
                        if self.onchirp:
                            self.onchirp(direction)
                self.history = []
            else:
                if DEBUG:
                    print(f"SILENCE_FRAME {self.silent_counter}")

    # extract frequency from audio data
    def detect(self, audio_data):

        # only detect sounds with minimum volume
        rms = np.sqrt(np.mean(audio_data ** 2))
        if rms < MIN_VOLUME:
            return None

        # hamming windowing
        hamming = audio_data * np.hamming(len(audio_data))
        # fourier similar to notebook from exercise
        # but with rfft instead of fft -> somehow works better for whistling I don't know why exactly but testing showed that
        spectrum = np.abs(np.fft.rfft(hamming))
        freqs = np.fft.rfftfreq(len(audio_data), 1 / RATE)

        # mask: only consider frequencies in whistle range (1000 Hz – 4000 Hz -> google said 1300 - 4000 but it didn't work well for my whistles)
        freq_mask = (freqs >= 1000) & (freqs <= 4000)
        masked_spectrum = spectrum * freq_mask

        # flatness: to differentiate between chirp and speech
        # chirp is more "clean/pure" than speech

        masked_vals = masked_spectrum[freq_mask]
        # geometric mean / arithmetic mean -> flatness measure -> close to 0 for speech, close to 1 for pure tones
        # formula from https://en.wikipedia.org/wiki/Spectral_flatness
        g_mean = np.exp(np.mean(np.log(masked_vals + 1e-10)))
        a_mean = np.mean(masked_vals)
        flatness = g_mean / a_mean

        if flatness > 0.2:
            if DEBUG:
                print(f"[REJECT] flatness={flatness:.4f} (too high), rms={rms:.4f}")
            return None

        # peak frequency is the detected frequency
        peak_idx = np.argmax(masked_spectrum)

        # if the peak is not strong enough -> probably background noise -> ignore
        peak_val = masked_spectrum[peak_idx]
        mean_val = np.mean(masked_spectrum[freq_mask])
        prominence = peak_val / mean_val
        if peak_val < 5 * mean_val:
            if DEBUG:
                print(f"[REJECT] prominence={prominence:.1f}x (too low), flatness={flatness:.4f}")
            return None

        freq = freqs[peak_idx]
        if DEBUG:
            print(f"[DETECT] freq={freq:.1f} Hz, flatness={flatness:.4f}, prominence={prominence:.1f}x, rms={rms:.4f}")
        return freq

    # classifies chirps
    def interpret_history(self):

        # short whistle -> ignore
        if len(self.history) < 5:
            return None

        # history to np array
        history_arr = np.array(self.history)

        # convolution
        history_smoothed = np.convolve(
            history_arr, np.ones(3) / 3, mode='valid')

        # median of first and last third of history -> check if up or down trend
        divider = max(2, len(history_smoothed) // 3)
        start_median = np.median(history_smoothed[:divider])
        end_median = np.median(history_smoothed[-divider:])
        delta_median = end_median - start_median

        # see how much it went up or down -> mean for percentage
        diffs = np.diff(history_smoothed)
        up_steps = np.mean(diffs > 0)
        down_steps = np.mean(diffs < 0)

        if DEBUG:
            print("CHECKING HISTORY:", len(self.history))
            print(f"delta_median={delta_median:.1f}, up_steps={up_steps:.2f}, down_steps={down_steps:.2f}")

        # upward trend and mostly up steps -> up chirp
        if delta_median > 40 and up_steps >= 0.5:
            self.history = []
            return "up"

        # downward trend and mostly down steps -> down chirp
        if delta_median < -30 and down_steps >= 0.5:
            self.history = []
            return "down"

        return None

    # start the stream
    def start(self):
        self.stream.start()

    # properly stop the stream
    def stop(self):
        self.stream.stop()
        self.stream.close()


# test
if __name__ == "__main__":
    import time

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

    # print direction for chirp
    def on_chirp(direction):
        print(f"Chirp: {direction}")

    controller = WhistleController(input_device=input_device, onchirp=on_chirp)
    controller.start()
    print("Listening... Ctrl+C to stop")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        controller.stop()
