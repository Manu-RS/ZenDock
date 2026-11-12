from machine import Pin, PWM
import time

class Led:

    def __init__(self, pin, frequency):
        
        if frequency < 1000 or frequency > 5000:
            raise Exception('Led Frequency must be a value in range [1000; 5000].')
        
        self.led 			= PWM(Pin(pin, Pin.OUT))
        self.led.freq(frequency)
        self.led.duty(0)
    
    
    def on(self):
        self.led.duty(1023)
    
    
    def off(self):
        self.led.duty(0)
    
    
    def setValue(self, value):
        
        if value < 0 or value > 1023:
            raise Exception('Duty Cicle must be a value in range [0; 1023].')
        self.led.duty(value)
    
    
    def setPercentage(self, percentage):
    
        if percentage < 0 or percentage > 100:
            raise Exception('Percentage must be a value in range [0; 100].')
        value = int(percentage * 1023 / 100)
        self.setValue(value)