import time
import random
import math
import threading
import sense_hat
import pygame

# Initialize Sense HAT
sense = sense_hat.SenseHat()
sense.low_light = True

# Initialize Pygame mixer for sound effects
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("./explosiond.wav")  # Add your explosion sound file here

# Function to play explosion sound
def play_explosion_sound():
    explosion_sound.play()

# Function to create a fireworks effect
def fireworks_effect():
    center_x, center_y = 4, 4
    num_fireworks = random.randint(1, 5)  # Randomly decide number of fireworks
    for _ in range(num_fireworks):
        # Random delay between fireworks
        time.sleep(random.uniform(0.2, 1.0))
        
        # Random color
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        
        # Burst effect
        for radius in range(0, 4):
            for angle in range(0, 360, 30):
                x = int(center_x + radius * math.cos(math.radians(angle)))
                y = int(center_y + radius * math.sin(math.radians(angle)))
                if 0 <= x < 8 and 0 <= y < 8:
                    sense.set_pixel(x, y, color)
            
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

