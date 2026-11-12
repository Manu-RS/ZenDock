from machine import Pin, PWM, Timer
import time 
#import sleep_ms


class Buzzer:
    def __init__(self, sig_pin:int,pDuty:int,pFreq:int):
        self.pwm = PWM(Pin(sig_pin, Pin.OUT))
        self.pwm.duty(0)  # Inizialmente spento
        self.freq = pFreq
        self.duty = pDuty

    
    """
     
    def play(self, melodies, wait, duty):
        for note in melodies:
            if note == 0:
                self.pwm.duty(0) # Pausa
            else:
                self.pwm.freq(note)
                self.pwm.duty(duty) 
            sleep_ms(wait) # Durata della nota
        self.stop() # Ferma il suono alla fine
    """   
    def stop(self):
        self.pwm.duty(0)  # Spegne il suono

    def riproduciSuono(self,freq:int,ms: int,duty):
        self.pwm.freq(freq)
        self.pwm.duty(duty) 
        sleep_ms(ms)
        self.stop()

    def riproduciSuonoNoSleep(self, freq: int, ms: int, duty: int):
        self.timer.deinit()
        
        self.pwm.freq(freq)
        self.pwm.duty(duty)
        
        self.timer.init(
            mode=Timer.ONE_SHOT,  
            period=ms,            
            callback=self.stop    
        )