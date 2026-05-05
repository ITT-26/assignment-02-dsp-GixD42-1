# AUDIO SETTINGS

# reduce chunk size and sampling rate for lower latency
# Chunk size lower, so we get more frequent updates -> better for chirps (in testing)
CHUNK_SIZE = 512  # Number of audio frames per buffer
RATE = 44100  # Audio sampling rate (HZ)
CHANNELS = 1  # Mono audio

# DETECTION SETTINGS

# Minimum RMS volume
MIN_VOLUME = 0.01
# Bounds for whistle frequencies
# (1000 Hz – 4000 Hz -> google said 1300 - 4000 but it didn't work well for my whistles)
FREQ_MIN = 1000
FREQ_MAX = 4000
# Spectral flatness threshold (0-1) -> lower -> more filtered -> filters out speech and noise
FLATNESS_THRESHOLD = 0.2
# How much stronger the peak must be compared to the mean to be considered a valid detection
PROMINENCE_FACTOR = 5

# CHIRP CLASSIFICATION SETTINGS

# How many frames are used in a Whistle
MAX_HISTORY = 20
# How few frames are allowed in a whistle
MIN_HISTORY = 5
# How many consecutive silent frames are allowed before the whistle is considered complete
SILENT_COUNTER_THRESHOLD = 3
# Kernel size for convolution --> needs to be odd and lower than MAX_HISTORY-1
SMOOTHING_KERNEL = 3

# THRESHOLDS FOR CLASSIFYING CHIRPS

# Rise/fall in median frequency
# Minimum Hz rise (end - start median) for "up" chirp
DELTA_UP = 40
# Minimum Hz fall (end - start median) for "down" chirp
DELTA_DOWN = -30
# Thresholds for mean fraction of upward or downward steps in history
# Minimum fraction of upward steps for "up" chirp
UP_STEPS_MIN = 0.5
# Minimum fraction of downward steps for "down" chirp
DOWN_STEPS_MIN = 0.5

# DEBUG: set True to see detection details -> useful for tuning constants to fit the personal whistles
DEBUG = False