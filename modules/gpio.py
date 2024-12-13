# GPIO module for MeshLink, concept code, not implemented
# K7MHI Kelly Keeton 2024

# https://pypi.org/project/gpio/
#import gpio

# https://pythonhosted.org/RPIO/
import RPIO

from modules.log import *
trap_list_gpio = ("gpio", "pin", "relay", "switch", "pwm")

# set up input channel without pull-up
RPIO.setup(7, RPIO.IN)

# set up input channel with pull-up
RPIO.setup(8, RPIO.IN, pull_up_down=RPIO.PUD_UP)

# set up GPIO output channel
RPIO.setup(8, RPIO.OUT)

# change to BOARD numbering schema
RPIO.setmode(RPIO.BOARD)

# set up PWM channel
RPIO.setup(12, RPIO.OUT)
p = RPIO.PWM(12)

def gpio_status():
    # get status of GPIO pins
    gpio_status = ""
    gpio_status += "GPIO 7: " + str(RPIO.input(7)) + "\n"
    gpio_status += "GPIO 8: " + str(RPIO.input(8)) + "\n"
    gpio_status += "GPIO 12: " + str(RPIO.input(12)) + "\n"
    return gpio_status

def gpio_toggle():
    # toggle GPIO pin 8
    RPIO.output(8, not RPIO.input(8))
    return "GPIO 8 toggled"

def gpio_pwm():
    # set PWM on GPIO pin 12
    p.start(50)
    return "PWM started"

def gpio_stop():
    # stop PWM on GPIO pin 12
    p.stop()
    return "PWM stopped"

def gpio_shutdown():
    # shutdown GPIO
    RPIO.cleanup()
    return "GPIO shutdown"

def trap_gpio(message):
    # trap for GPIO commands
    if "status" in message:
        return gpio_status()
    elif "toggle" in message:
        return gpio_toggle()
    elif "pwm" in message:
        return gpio_pwm()
    elif "stop" in message:
        return gpio_stop()
    elif "shutdown" in message:
        return gpio_shutdown()
    else:
        return "GPIO command not recognized"
    

    
