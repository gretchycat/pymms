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

