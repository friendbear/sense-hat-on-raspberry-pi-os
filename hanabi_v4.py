import time
import random
import math
import threading
import sense_hat
import pygame
import numpy as np
import pyaudio

# Initialize Sense HAT
sense = sense_hat.SenseHat()
sense.low_light = True

# Initialize Pygame mixer for sound effects
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("./explosiond.wav")  # Add your explosion sound file here

# Initialize PyAudio for microphone input
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

# Function to play explosion sound
def play_explosion_sound():
    explosion_sound.play()

# Function to create a fireworks effect
def fireworks_effect(center_x, center_y, size):
    num_fireworks = random.randint(1, 5)  # Randomly decide number of fireworks
    for _ in range(num_fireworks):
        # Random delay between fireworks
        time.sleep(random.uniform(0.2, 1.0))

        # Random color
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        # Burst effect
        for radius in range(1, size + 1):
            for angle in range(0, 360, 15):
                x = int(center_x + radius * math.cos(math.radians(angle)))
                y = int(center_y + radius * math.sin(math.radians(angle)))
                if 0 <= x < 8 and 0 <= y < 8:
                    brightness = max(0, 255 - int(radius * 30))
                    sense.set_pixel(x, y, (color[0], color[1], color[2], brightness))

            # Randomly change brightness
            time.sleep(0.1)

        # Clear the screen for the next burst
        sense.clear()

        # Play sound effect
        play_explosion_sound()

def get_beats_per_minute():
    """ Calculate BPM from microphone input """
    data = np.frombuffer(stream.read(1024), dtype=np.int16)
    rms = np.sqrt(np.mean(np.square(data)))
    # Simple heuristic to approximate BPM (This part can be improved based on actual needs)
    return 60 / (rms / 1000.0)

def disco_effect():
    """ Display disco-like effects with flashing colors and brightness """
    global state
    while True:
        if state["disco_mode"]:
            size = random.randint(1, 8)  # Random size of the firework
            center_x = random.randint(0, 7)  # Random x position
            center_y = random.randint(0, 7)  # Random y position
            
            # Get BPM and adjust delay accordingly
            bpm = get_beats_per_minute()
            delay = 60 / bpm if bpm > 0 else 1

            for _ in range(random.randint(3, 10)):  # Number of fireworks bursts
                fireworks_effect(center_x, center_y, size)
                time.sleep(delay)  # Delay between bursts

        # Sleep briefly to reduce CPU usage
        time.sleep(1)

# Set initial state
state = {
    "disco_mode": True
}

# Start disco effect in a separate thread
disco_thread = threading.Thread(target=disco_effect)
disco_thread.daemon = True
disco_thread.start()

# Main loop to keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sense.clear()
    stream.stop_stream()
    stream.close()
    p.terminate()

