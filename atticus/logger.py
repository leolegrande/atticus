##### Atticus the Cactus Data Logger #####
##### Created by Leo Grandinetti #####

# libraries
from gpiozero import LightSensor
from RPi.GPIO as GPIO
from time import sleep, strftime, localtime
import datetime
from sense_hat import SenseHat

# fields
ldr = LightSensor(4)
sense = SenseHat()
delay = 3600
day = strftime("%d", localtime())
date = strftime("%m-%d-%y", localtime())
filename = "logs/" + date + "_atticus_log.csv"
header = "timestamp, temperature, humidity, pressure, light\n"


# functions
def get_sense_data():
    sense_data = []
    sense_data.append(strftime("%m/%d/%y %H:%M:%S", localtime()))
    sense_data.append(sense.get_temperature_from_humidity)
    sense_data.append(sense.get_humidity())
    sense_data.append(sense.get_pressure())
    return sense_data

def check_day():
    global day
    global date
    global filename
    curDay = strftime("%d", localtime())
    if curDay != day:
        day = curDay
        date = strftime("%m-%d-%y", localtime())
        filename = "logs/" + date + "_atticus_log.csv"
        return True
    else:
        return False

def file_setup():
    log = open(filename, "w")
    log.write(header + "\n")
    log.close()

def log_data(data):
    log = open(filename, "a")
    logString = ",".join(str(value) for value in data)
    log.write(logString)
    log.close()
    print("Logged: " + logString)

# main
def main():
    file_setup()
    while True:
        if check_day():
            file_setup()
        log_data(get_sense_data())
        sleep(delay)

main()
