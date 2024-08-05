import time
import random
import math
import threading
from sense_hat import SenseHat
import pygame

# Initialize Sense HAT
sense = SenseHat()
sense.low_light = True

# Initialize Pygame mixer for sound effects
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("./explosiond.wav")  # Add your explosion sound file here

# Function to play explosion sound
def play_explosion_sound():
    explosion_sound.play()

# Function to get motion data
def get_motion_data():
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    
    # Calculate the magnitude of the motion (combined accelerometer and gyroscope)
    accel_magnitude = math.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
    gyro_magnitude = math.sqrt(gyro['x']**2 + gyro['y']**2 + gyro['z']**2)
    
    # Combine accelerometer and gyroscope magnitudes
    motion_magnitude = accel_magnitude + gyro_magnitude
    
    return motion_magnitude

# Function to create a fireworks effect with motion sensitivity
def fireworks_effect():
    # Get the motion magnitude to influence firework size and burst
    motion_magnitude = get_motion_data()
    
    # Determine the center and number of fireworks
    center_x = random.randint(0, 7)
    center_y = random.randint(0, 7)
    num_fireworks = random.randint(1, 5)
    
    # Adjust the maximum radius based on motion magnitude
    max_radius = min(4, max(1, int(motion_magnitude * 5)))  # Scale the radius

    for _ in range(num_fireworks):
        # Random delay between fireworks
        time.sleep(random.uniform(0.2, 1.0))

        # Random color
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        # Burst effect
        for radius in range(1, max_radius + 1):
            for angle in range(0, 360, 30):
                x = int(center_x + radius * math.cos(math.radians(angle)))
                y = int(center_y + radius * math.sin(math.radians(angle)))
                if 0 <= x < 8 and 0 <= y < 8:
                    # Create a gradient effect for the firework
                    distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    brightness = max(0, 255 - int(distance * 30))
                    # Adjust color by brightness
                    r = min(255, color[0] + brightness)
                    g = min(255, color[1] + brightness)
                    b = min(255, color[2] + brightness)
                    sense.set_pixel(x, y, (r, g, b))

            # Randomly change brightness
            time.sleep(0.1)

        # Clear the screen for the next burst
        sense.clear()

        # Play sound effect
        play_explosion_sound()

def disco_effect():
    """ Display disco-like effects with flashing colors and brightness """
    global state
    while True:
        if state["disco_mode"]:
            for _ in range(random.randint(3, 10)):  # Number of fireworks bursts
                fireworks_effect()
                time.sleep(random.uniform(0.2, 1.0))  # Delay between bursts

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

