import numpy as np
import sounddevice as sd

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
CHUNK_SIZE = 1024  # Number of audio frames per buffer
RATE = 44100  # Audio sampling rate (HZ)
CHANNELS = 1  # Mono audio

MIN_VOLUME = 0.01


class WhistleController:
    def __init__(self, input_device, onchirp=None):
        self.input_device = input_device

        self.onchirp = onchirp

        # history of the last frequencies
        self.history = []
        self.max_history = 20

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
        # No sound
        else:
            # Sound was there before -> interpret history
            if len(self.history) >= 5:
                direction = self.interpret_history()
                # if a chirp is interpreted -> callback function (used for controls)
                if direction:
                    if self.onchirp:
                        self.onchirp(direction)
            self.history = []

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

        # peak frequency is the detected frequency
        peak_idx = np.argmax(masked_spectrum)

        # if the peak is not strong enough -> probably background noise -> ignore
        peak_val = masked_spectrum[peak_idx]
        mean_val = np.mean(masked_spectrum[freq_mask])
        if peak_val < 5 * mean_val:
            return None

        return freqs[peak_idx]

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

        # upward trend and mostly up steps -> up chirp
        if delta_median > 80 and up_steps > 0.5:
            self.history = []
            return "up"

        # downward trend and mostly down steps -> down chirp
        if delta_median < -80 and down_steps > 0.5:
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
