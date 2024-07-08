#!/usr/bin/python
from sense_hat import SenseHat
import time
import sys

sense = SenseHat()
sense.clear()

try:
    while True:
        temp = sense.get_temperature()
        temp = round(temp,1)

        sense.show_message("Temperature C",temp)

        humidity = sense.get_humidity()  
        humidity = round(humidity, 1)  
        sense.show_message("Humidity :",humidity)  

        pressure = sense.get_pressure()
        pressure = round(pressure, 1)
        sense.show_message("pressure :", pressure)

        time.sleep(15)

except KeyboardInterrupt:
    pass

       
