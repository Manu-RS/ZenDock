from machine import ADC, Pin


class Ldr:

    ADC_MAX = 4095
    DEFAULT_MIN_VALUE = 0
    DEFAULT_MAX_VALUE = 100

    # Inizializza il sensore LDR sul pin analogico ESP32 (0 - 3.3V)
    def __init__(self, pin, min_value=DEFAULT_MIN_VALUE, max_value=DEFAULT_MAX_VALUE):
        if min_value >= max_value:
            raise ValueError("Min value must be strictly less than max value.")

        self._adc = ADC(Pin(pin, mode=Pin.IN))
        self._adc.atten(ADC.ATTN_11DB)
        self._min_value = min_value
        self._max_value = max_value

    # Legge il valore analogico grezzo dall'ADC (0 - 4095) con media opzionale
    def read_raw(self, samples=1):
        if samples <= 1:
            return self._adc.read()

        total = 0
        for _ in range(samples):
            total += self._adc.read()
        return total // samples

    # Legge e scala il valore nell'intervallo configurato [min_value, max_value]
    def read_value(self, samples=1):
        raw = self.read_raw(samples)
        return self._min_value + (self._max_value - self._min_value) * raw / self.ADC_MAX

    # Legge la luminosità rilevata in percentuale (0 - 100)
    def read_percentage(self, samples=1):
        raw = self.read_raw(samples)
        return round((raw * 100) / self.ADC_MAX, 1)

    # Restituisce True se la luminosità percentuale è inferiore alla soglia indicata
    def is_dark(self, threshold_percentage=30, samples=3):
        return self.read_percentage(samples) < threshold_percentage