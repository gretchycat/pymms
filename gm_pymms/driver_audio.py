from .Timer import Timer
import math
from pydub import AudioSegment

STOP=0
PLAY=1
RECORD=2

class driver_audio():
    def __init__(self):
        self.endHandler=None
        self.status=STOP
        self.timer=Timer()
        self.cursor=0
        self.fps=44100
        self.channels=1
        self.sample_width=16//8
        self.record_buffer=None
        self.audio=None
        self.audio_start=0
        self.record_audio=None
        return None

    def load(self, filename):
        self.timer.clear()
        self.audio=AudioSegment.from_file(filename)
        self.setAudioProperties(fps=self.audio.frame_rate,
            channels=self.audio.channels, sample_width=self.audio.sample_width)
        self.audio_start=0
        return self.audio

    def play(self, start=0, end=0):
        self.status=PLAY
        #buffer=self.audio.get_array_of_samples()
        self.audio_start=self.get_cursor()
        self.timer.start(factor=self.audio.frame_rate, offset=-int(self.get_cursor()/self.audio.frame_rate))
        if end==0:
            pass
            #return sd.play(buffer[int(start):], self.audio.frame_rate)
        #return sd.play(buffer[int(start):int(end)], self.audio.frame_rate)

    def stop(self):
        #sd.stop()
        self.status=STOP
        if self.record_buffer is not None:
            frames=int(self.timer.get())
            self.record_audio=self.setAudio(self.record_buffer[:frames],
                self.fps,
                self.sample_width, self.channels)
            record_buffer=None
        self.timer.clear()
        self.audio_start=0

    def rec(self):
        self.status=RECORD
        self.audio_start=self.get_cursor()
        self.timer.start(factor=self.fps)
        len=self.fps*self.channels*60*10
        self.record_audio=None
        #self.record_buffer=sd.rec(len, self.fps, channels=self.channels)

    def wait(self):
        pass
        #return sd.wait()

    def save(self, filename):
        # Validate audio data
        if self.audio:
            self.audio.export(filename)

    def length_time(self):
        if self.audio:
            return self.length()/self.audio.frame_rate
        return 0

    def length(self):
        if self.audio:
            if self.status==RECORD:
                if self.timer.get():
                    return int(self.timer.get()+self.audio.frame_count())
            else:
                return int(self.audio.frame_count())
        else:
            if self.status==RECORD:
                return int(self.timer.get())
        return 0

    def get_cursor(self): #TODO FIXME find authoritative value
        if self.cursor>=self.length() and self.status==PLAY:
            if self.endHandler:
                self.endHandler()
        t=int(self.timer.get())
        if t>0:
            self.cursor=t
            if self.status==RECORD:
                self.cursor = t+self.audio_start
            if self.cursor>self.length():
                self.cursor=self.length()
        return self.cursor

    def get_cursor_time(self):
        fps=self.fps
        if self.audio:
            fps=self.audio.frame_rate
        if fps:
            return self.get_cursor()/fps #au.audio.frame_rate
        return 0

    def setAudio(self, buffer, fps, sample_width, channels):
        #return AudioSegment from buffer
        raise NotImplementedError(f"you must implement setAudio in {type(self)}")

    def setAudioProperties(self, fps=24000, channels=1, sample_width=16//8):
        self.fps=fps
        self.sample_width=sample_width
        self.channels=channels

    def concatenate(self, audiolist):
        full=None
        for a in audiolist:
            if full==None:
                full=a
            else:full=full+a
        return full

    def crop(self, start=None, end=None):
        fps=self.fps
        channels=self.channels
        sample_width=16//8
        if self.audio:
            fps=self.audio.frame_rate
            channels=self.audio.channels
            sample_width=self.audio.sample_width
        else:
            return None
        sf,ef=None, None
        if start is not None:
            sf=int(start)
        if end is not None:
            ef=int(end)
        if sf is not None and ef is not None:
            clip_frames=self.audio.get_array_of_samples()[sf:ef]
        elif sf is not None:
            clip_frames=self.audio.get_array_of_samples()[sf:]
        elif ef is not None:
            clip_frames=self.audio.get_array_of_samples()[:ef]
        else:
            clip_frames=self.audio.get_array_of_samples()
        #convert to AudioSegment
        audio_segment = AudioSegment(clip_frames.tobytes(), frame_rate=fps,
            sample_width=sample_width, channels=channels)
        if audio_segment.frame_count()>0:
            return audio_segment
        return None

import math
from pydub import AudioSegment, silence

def noise_reduction(audio_segment, smooth_factor=0.1):
    """
    Reduces noise in an audio segment using FFT-based filtering.

    Args:
            audio_segment: The Pydub AudioSegment to process.
            sample_rate: The sample rate (frames per second) of the audio.
            smooth_factor: A value between 0 and 1 to control smoothing during noise reduction (optional, default 0.1).

    Returns:
            A new Pydub AudioSegment with reduced noise.
    """
    sample_rate=audio_segment.frame_rate

    # Get the data from the segment
    data = audio_segment.get_array_of_samples()

    # Calculate the number of samples
    N = len(data)

    # Find noise ceiling (assuming first few milliseconds represent noise)
    noise_ceiling = max(data[:int(sample_rate * 0.01)])    # Adjust window size for noise estimation

    # Create a noise sample of the same length as the audio
    noise_sample = [noise_ceiling for _ in range(N)]

    # Perform FFT on both the audio data and noise sample
    audio_fft = fft(data, N)
    noise_fft = fft(noise_sample, N)

    # Apply smoothing (optional)
    smoothed_noise_fft = [val * (1 - smooth_factor) + noise_fft[i] * smooth_factor for i, val in enumerate(audio_fft)]

    # Subtract smoothed noise FFT from audio FFT
    filtered_fft = [a - b for a, b in zip(audio_fft, smoothed_noise_fft)]

    # Perform inverse FFT on the filtered data
    filtered_data = ifft(filtered_fft, N)

    # Convert the filtered data back to an AudioSegment
    filtered_segment = AudioSegment.from_mono(filtered_data, sample_width=audio_segment.sample_width, frame_rate=sample_rate)

    return filtered_segment

# Define helper functions for FFT and IFFT (replace with optimized implementations from NumPy or SciPy if available)
def fft(data, N):
    fft_result = [0] * N
    for k in range(N):
        for n in range(N):
            angle = 2 * math.pi * k * n / N
            fft_result[k] += data[n] * math.exp(-1j * angle)
    return fft_result

def ifft(data, N):
    ifft_result = [0] * N
    for n in range(N):
        for k in range(N):
            angle = 2 * math.pi * k * n / N
            ifft_result[n] += data[k] * math.exp(1j * angle)
    return [val / N for val in ifft_result]

if 0:
    # Example usage
    audio_segment = AudioSegment.from_file("your_audio_file.mp3")
    sample_rate = audio_segment.frame_rate

    # Reduce noise with adjustable smoothing factor (optional)
    filtered_segment = noise_reduction(audio_segment, smooth_factor=0.2)

    # Save the filtered audio (optional)
    filtered_segment.export("filtered_audio.mp3", format="mp3")

    # Play the original and filtered audio for comparison (optional)
    audio_segment.play()
    filtered_segment.play()

