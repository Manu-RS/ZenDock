from machine import Pin, PWM
import time

class Servo:

    def __init__(self, pin):
        self.servo 				= PWM(Pin(pin, Pin.OUT))
        self.servo.freq(50)
        self.servo.duty(26)
        # Variabile interna per tenere traccia della posizione
        self.__currentDegree = 0
    
    
    def getCurrentDegree(self):
        return self.__currentDegree


    def moveToMinPos(self):
        self.servo.duty(26)
        self.__currentDegree = 0
    
    
    def moveToMaxPos(self):
        self.servo.duty(123)
        self.__currentDegree = 180
    
    def __setValue(self, value):
        
        if value < 26 or value > 123:
            raise Exception('Duty Cicle must be a value in range [26; 123].')
        self.servo.duty(value)
    
    
    def setDegree(self, degree):
    
        if degree < 0 or degree > 180:
            raise Exception('Degree must be a value in range [0; 180].')
        value = int((degree / 180) * (123 - 26) + 26)
        self.__setValue(value)
        self.__currentDegree = degree
