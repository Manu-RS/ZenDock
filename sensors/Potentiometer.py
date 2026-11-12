from machine import Pin, ADC


class Potentiometer:

    ADC_MAX = 4095
    DEFAULT_ATTN = ADC.ATTN_11DB

    # Mappa ogni attenuazione ESP32 alla sua tensione massima misurabile (V)
    ATTN_VOLTAGE_MAP = {
        ADC.ATTN_0DB: 1.1,
        ADC.ATTN_2_5DB: 1.5,
        ADC.ATTN_6DB: 2.0,
        ADC.ATTN_11DB: 3.3,
    }

    # Permette di passare anche stringhe legibili oltre alle costanti ADC
    ATTN_STRING_MAP = {
        "0DB": ADC.ATTN_0DB,
        "ADC.ATTN_0DB": ADC.ATTN_0DB,
        "2_5DB": ADC.ATTN_2_5DB,
        "ADC.ATTN_2_5DB": ADC.ATTN_2_5DB,
        "6DB": ADC.ATTN_6DB,
        "ADC.ATTN_6DB": ADC.ATTN_6DB,
        "11DB": ADC.ATTN_11DB,
        "ADC.ATTN_11DB": ADC.ATTN_11DB,
    }

    # Inizializza il potenziometro sul pin ADC con l'attenuazione specificata (default 3.3V)
    def __init__(self, pin, attn=DEFAULT_ATTN):
        self._adc = ADC(Pin(pin, mode=Pin.IN))
        self._attn = self._resolve_attn(attn)
        self._adc.atten(self._attn)
        self._max_voltage = self.ATTN_VOLTAGE_MAP[self._attn]

    # Converte una stringa o costante nella costante ADC.ATTN_* valida per ESP32
    def _resolve_attn(self, attn):
        if isinstance(attn, str):
            resolved = self.ATTN_STRING_MAP.get(attn.upper())
            if resolved is None:
                raise ValueError(f"Unsupported attenuation: {attn}")
            return resolved
        if attn not in self.ATTN_VOLTAGE_MAP:
            raise ValueError(f"Unsupported attenuation value: {attn}")
        return attn

    # Legge il valore grezzo dell'ADC (0 - 4095), con media opzionale su più campioni
    def read_raw(self, samples=1):
        if samples <= 1:
            return self._adc.read()

        total = 0
        for _ in range(samples):
            total += self._adc.read()
        return total // samples

    # Calcola la tensione in Volt in base all'attenuazione configurata
    def read_voltage(self, samples=1):
        raw = self.read_raw(samples)
        return round((raw / self.ADC_MAX) * self._max_voltage, 3)

    # Mappa la lettura del potenziometro in un intervallo intero [out_min, out_max]
    def read_range(self, out_min, out_max, samples=1):
        if out_min >= out_max:
            raise ValueError("out_min must be strictly less than out_max.")

        raw = self.read_raw(samples)
        return int((raw / self.ADC_MAX) * (out_max - out_min) + out_min)

    # Restituisce la posizione del potenziometro in percentuale (0 - 100)
    def read_percentage(self, samples=1):
        raw = self.read_raw(samples)
        return round((raw / self.ADC_MAX) * 100, 1)