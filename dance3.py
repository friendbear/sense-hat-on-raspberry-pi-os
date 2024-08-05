import time
import random
import threading
import math
import numpy as np
from scipy.fftpack import fft
import sense_hat

# Initialize Sense HAT
sense = sense_hat.SenseHat()
sense.low_light = True

# Game state
starting_enemies = [[4, 6], [0, 4]]
state = {
    "bug_x": 4,
    "bug_y": 4,
    "bug_rgb": (250, 250, 250),
    "food_x": 2,
    "food_y": 7,
    "food_rgb": (0, 255, 50),
    "level": 1,
    "enemies": starting_enemies,
    "enemy_rgb": (255, 50, 0),
    "game_started": False,
    "game_over": False,
    "disco_mode": False
}

# Store initial state to reset game
start_over_state = dict(state)

def setscreen():
    """Update LED matrix based on game state."""
    global state
    if sense.low_light:
        zero = 8
    else:
        zero = 48
    brightness = 255 - zero
    sense.clear((50, 100, 150))
    sense.set_pixel(state["food_x"], state["food_y"], state["food_rgb"])
    sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])
    for e in state["enemies"]:
        sense.set_pixel(e[0], e[1], state["enemy_rgb"])

def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)

def clip(pixels, nmin=0, nmax=255):
    """Clip RGB values to ensure they are within 0-255 range."""
    return tuple(max(min(nmax, n), nmin) for n in pixels)

def check_pos():
    """Check bug position for collisions or food consumption."""
    global state
    bug_x = state["bug_x"]
    bug_y = state["bug_y"]
    food_x = state["food_x"]
    food_y = state["food_y"]
    level = state["level"]

    fdist = distance(bug_x, bug_y, food_x, food_y)

    # Check for collisions with enemies
    for e in state["enemies"]:
        edist = distance(bug_x, bug_y, e[0], e[1])
        if edist == 0:
            # Game over
            sense.show_message("Game Over, Level {}".format(state["level"]))
            state = dict(start_over_state)
            return

    # Check distance to food
    if fdist == 0.0:
        # Bug eats food and gets healthier
        state["bug_rgb"] = (255, 255, 255)
        state["level"] += 1
        state["enemies"].append([random.randint(0, 7), random.randint(0, 7)])
        sense.show_message(str(state["level"]))
        time.sleep(1)
        # Move food to a new location that's not under the bug
        while True:
            state["food_x"] = random.randint(0, 7)
            if state["food_x"] != state["bug_x"]:
                break
        while True:
            state["food_y"] = random.randint(0, 7)
            if state["food_y"] != state["bug_y"]:
                break

    elif fdist < 2.5:
        # Bug is close to food; strengthen bug
        state["bug_rgb"] = clip([min(i + 10, 255) for i in state["bug_rgb"]])

def rand_step(xy):
    """Take one random step in a 2D space."""
    x, y = xy
    new_x = x + random.choice([-1, 0, 1])
    new_y = y + random.choice([-1, 0, 1])
    return [max(0, min(7, new_x)), max(0, min(7, new_y))]

def move_enemies():
    """Move enemies randomly on the grid."""
    global state
    reserved = [[state["bug_x"], state["bug_y"]], [state["food_x"], state["food_y"]]]
    new_enemies = []
    for e in state["enemies"]:
        while True:
            new_e = rand_step(e)
            if new_e not in reserved:
                break
        new_enemies.append(new_e)
    state["enemies"] = new_enemies
    setscreen()

def draw_bug(event):
    """Handle joystick events to move the bug."""
    global state
    if state["game_over"]:
        return
    if not state["game_started"]:
        state["game_started"] = True
        sense.show_message("Game Started")
        time.sleep(1)
    if event.action == sense_hat.ACTION_RELEASED:
        return
    elif event.direction == sense_hat.DIRECTION_UP:
        state["bug_y"] = max(0, state["bug_y"] - 1)
    elif event.direction == sense_hat.DIRECTION_DOWN:
        state["bug_y"] = min(7, state["bug_y"] + 1)
    elif event.direction == sense_hat.DIRECTION_RIGHT:
        state["bug_x"] = min(7, state["bug_x"] + 1)
    elif event.direction == sense_hat.DIRECTION_LEFT:
        state["bug_x"] = max(0, state["bug_x"] - 1)
    setscreen()
    check_pos()

def display_disco():
    """Display disco-like effects with flashing colors."""
    global state
    while True:
        if state["game_over"]:
            time.sleep(30)  # Display disco for 30 seconds after game over
        elif not state["game_started"]:
            time.sleep(1)  # Wait for game start
        else:
            for x in range(8):
                for y in range(8):
                    if random.random() > 0.2:  # 80% chance to flash
                        r = random.randint(0, 255)
                        g = random.randint(0, 255)
                        b = random.randint(0, 255)
                        sense.set_pixel(x, y, (r, g, b))
                    else:
                        sense.set_pixel(x, y, (0, 0, 0))
            time.sleep(0.05)  # Increase speed for more dynamic effect

def get_audio_input():


def display_disco_with_audio():
    audio_gen = get_audio_input()
    global state
    while True:
        if state["game_over"]:
            time.sleep(30)  # Display disco for 30 seconds after game over
        elif not state["game_started"]:
            time.sleep(1)  # Wait for game start
        else:
            dominant_freq = next(audio_gen)
            for x in range(8):
                for y in range(8):
                    if random.random() > 0.2:  # 80% chance to flash
                        r = int(dominant_freq % 256)
                        g = int((dominant_freq // 2) % 256)
                        b = int((dominant_freq // 3) % 256)
                        sense.set_pixel(x, y, (r, g, b))
                    else:
                        sense.set_pixel(x, y, (0, 0, 0))
            time.sleep(0.05)  # Increase speed for more dynamic effect

# Event listeners for joystick
sense.stick.direction_up = draw_bug
sense.stick.direction_down = draw_bug
sense.stick.direction_left = draw_bug
sense.stick.direction_right = draw_bug
sense.stick.direction_middle = draw_bug

# Start displaying disco mode in a separate thread
disco_thread = threading.Thread(target=display_disco_with_audio)
disco_thread.daemon = True
disco_thread.start()

# Initial setup of the game screen
setscreen()
sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])

# Game loop
last_tick = round(time.time(), 1) * 10
while True:
    timer = 20 - (state["level"] % 20)
    tick = round(time.time(), 1) * 10

    # Move enemies periodically
    if (tick % timer == 0) and (tick > last_tick):
        move_enemies()
        last_tick = tick

    time.sleep(0.1)  # Reduce CPU usage

# Pause indefinitely, awaiting joystick events
sense.stick.wait_for_event()

