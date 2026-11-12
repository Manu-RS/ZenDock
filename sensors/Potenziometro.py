from machine import Pin, ADC
import time
"""
ADC.ATTN_0DB -> 0 - 1,2 V
ADC.ATTN_2_5DB -> 0 - 1,5 V
ADC.ATTN_6DB -> 0 - 2,0 V
ADC.ATTN_11DB -> 0 - 3,3 V
"""

class Potenziometro:


    def init(self,nPin:int,dB:str ):
        self.adc = ADC(Pin(nPin, mode=Pin.IN))
        self.ADC_ATTN_XXDB = dB

        if dB == "ADC.ATTN_0DB":
            self.adc.atten(ADC.ATTN_0DB)
        elif dB == "ADC.ATTN_2_5DB":
            self.adc.atten(ADC.ATTN_2_5DB)
        elif dB == "ADC.ATTN_6DB":
            self.adc.atten(ADC.ATTN_6DB)
        elif dB == "ADC.ATTN_11DB":
            self.adc.atten(ADC.ATTN_11DB)


    def read(self):
        val = self.adc.read()
        match self.ADC_ATTN_XXDB:
            case "ADC.ATTN_0DB":
                # Fino a 1.2V
                val = val * (1.1 / 4095)
            case "ADC.ATTN_2_5DB":
                # Fino a 1.5V
                val = val * (1.34 / 4095)
            case "ADC.ATTN_6DB":
                # Fino a 2.0V
                val = val * (2.0 / 4095)
            case "ADC.ATTN_11DB":
                # Fino a 3.3V 
                val = val * (3.6 / 4095)
            case _:
                val = val * (3.3 / 4095)
        return val

    def readByRange(self, out_min, out_max):
        raw_val = self.adc.read() 
        
        return int((raw_val / 4095.0) * (out_max - out_min) + out_min)
        
    
    