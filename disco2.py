import time
import random
import threading
import sense_hat

# Initialize Sense HAT
sense = sense_hat.SenseHat()
sense.low_light = True

# Disco state
state = {
    "intensity": 5,
    "speed": 0.1
}

def display_disco():
    """Display disco-like effects with flashing colors."""
    global state
    while True:
        for x in range(8):
            for y in range(8):
                if random.random() > 1 - (state["intensity"] / 10.0):  # Intensity controls how many LEDs light up
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    sense.set_pixel(x, y, (r, g, b))
                else:
                    sense.set_pixel(x, y, (0, 0, 0))
        time.sleep(state["speed"])

def adjust_intensity(event):
    """Adjust the intensity of the disco effect based on joystick up/down."""
    global state
    if event.action == sense_hat.ACTION_RELEASED:
        return
    if event.direction == sense_hat.DIRECTION_UP:
        state["intensity"] = min(10, state["intensity"] + 1)
    elif event.direction == sense_hat.DIRECTION_DOWN:
        state["intensity"] = max(1, state["intensity"] - 1)

def adjust_speed(event):
    """Adjust the speed of the disco effect based on joystick left/right."""
    global state
    if event.action == sense_hat.ACTION_RELEASED:
        return
    if event.direction == sense_hat.DIRECTION_RIGHT:
        state["speed"] = max(0.01, state["speed"] - 0.01)
    elif event.direction == sense_hat.DIRECTION_LEFT:
        state["speed"] = min(1, state["speed"] + 0.01)

# Event listeners for joystick
sense.stick.direction_up = adjust_intensity
sense.stick.direction_down = adjust_intensity
sense.stick.direction_left = adjust_speed
sense.stick.direction_right = adjust_speed

# Start displaying disco mode in a separate thread
disco_thread = threading.Thread(target=display_disco)
disco_thread.daemon = True
disco_thread.start()

# Pause indefinitely, awaiting joystick events
sense.stick.wait_for_event()

