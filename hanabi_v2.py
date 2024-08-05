import time
import random
import threading
import sense_hat
import pygame  # For sound effects

# Initialize Sense HAT and Pygame for sound
sense = sense_hat.SenseHat()
sense.low_light = True
pygame.mixer.init()
firework_sound = pygame.mixer.Sound('./explosiond.wav')

# Game state
state = {
    "fireworks": []
}

def play_firework_sound():
    """Play firework sound effect."""
    pygame.mixer.Sound.play(firework_sound)

def generate_firework():
    """Generate a new firework with random attributes."""
    x, y = random.randint(0, 7), random.randint(0, 7)
    size = random.randint(2, 4)
    duration = random.uniform(0.5, 1.0)
    colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)) for _ in range(size)]
    return {"x": x, "y": y, "size": size, "duration": duration, "colors": colors, "start_time": time.time()}

def update_fireworks():
    """Update firework effects and remove expired fireworks."""
    current_time = time.time()
    new_fireworks = []
    
    for fw in state["fireworks"]:
        age = current_time - fw["start_time"]
        if age < fw["duration"]:
            # Update firework based on age
            intensity = max(0, 1 - age / fw["duration"])
            size = int(fw["size"] * intensity)
            for i in range(size):
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(0, size)
                dx = int(distance * math.cos(angle))
                dy = int(distance * math.sin(angle))
                x, y = (fw["x"] + dx) % 8, (fw["y"] + dy) % 8
                color = fw["colors"][i % len(fw["colors"])]
                sense.set_pixel(x, y, color)
            new_fireworks.append(fw)
        else:
            # Firework has expired
            pass
    
    state["fireworks"] = new_fireworks

def firework_display():
    """Display fireworks with varying intensity and spread."""
    global state
    while True:
        if random.random() < 0.1:  # 10% chance to fire fireworks
            num_fireworks = random.randint(1, 5)
            for _ in range(num_fireworks):
                state["fireworks"].append(generate_firework())
                play_firework_sound()
        
        update_fireworks()
        time.sleep(0.1)

# Start fireworks display in a separate thread
firework_thread = threading.Thread(target=firework_display)
firework_thread.daemon = True
firework_thread.start()

# Keep the program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sense.clear()

