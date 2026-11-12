from machine import Pin, PWM
from time import sleep_ms


class Led:

    MIN_FREQUENCY = 1000
    MAX_FREQUENCY = 5000
    DEFAULT_FREQUENCY = 1000
    MIN_DUTY = 0
    MAX_DUTY = 1023

    # Inizializza il LED sul pin PWM specificato
    def __init__(self, pin, frequency=DEFAULT_FREQUENCY):
        if not (self.MIN_FREQUENCY <= frequency <= self.MAX_FREQUENCY):
            raise ValueError(
                f"Frequency must be in range [{self.MIN_FREQUENCY}; {self.MAX_FREQUENCY}]."
            )

        self._pwm = PWM(Pin(pin, Pin.OUT))
        self._pwm.freq(frequency)
        self._current_duty = self.MIN_DUTY
        self._pwm.duty(self._current_duty)

    # Accende il LED alla massima luminosità
    def on(self):
        self.set_value(self.MAX_DUTY)

    # Spegne il LED
    def off(self):
        self.set_value(self.MIN_DUTY)

    # Inverte lo stato attuale del LED (acceso <-> spento)
    def toggle(self):
        if self.is_on():
            self.off()
        else:
            self.on()

    # Restituisce True se il LED è acceso (duty > 0)
    def is_on(self):
        return self._current_duty > self.MIN_DUTY

    # Imposta il duty cycle grezzo (0 - 1023)
    def set_value(self, value):
        if not (self.MIN_DUTY <= value <= self.MAX_DUTY):
            raise ValueError(
                f"Duty cycle must be in range [{self.MIN_DUTY}; {self.MAX_DUTY}]."
            )
        self._current_duty = int(value)
        self._pwm.duty(self._current_duty)

    # Imposta la luminosità in percentuale (0 - 100)
    def set_percentage(self, percentage):
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be in range [0; 100].")

        value = int(percentage * self.MAX_DUTY / 100)
        self.set_value(value)

    # Restituisce la luminosità corrente in percentuale (0 - 100)
    def get_percentage(self):
        return round((self._current_duty * 100) / self.MAX_DUTY, 1)

    # Esegue una dissolvenza graduale verso una percentuale target
    def fade_to(self, target_percentage, duration_ms=500, steps=25):
        if not (0 <= target_percentage <= 100):
            raise ValueError("Percentage must be in range [0; 100].")

        start_duty = self._current_duty
        target_duty = int(target_percentage * self.MAX_DUTY / 100)
        step_delay = max(1, duration_ms // steps)

        for i in range(1, steps + 1):
            new_duty = start_duty + ((target_duty - start_duty) * i) // steps
            self.set_value(new_duty)
            sleep_ms(step_delay)

    # Rilascia la risorsa PWM
    def deinit(self):
        self.off()
        self._pwm.deinit()