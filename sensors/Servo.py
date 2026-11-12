from machine import Pin, PWM


class Servo:

    DEFAULT_FREQ = 50
    MIN_DUTY = 26
    MAX_DUTY = 123
    MIN_DEGREE = 0
    MAX_DEGREE = 180

    # Inizializza il servomotore sul pin PWM e lo porta a 0 gradi
    def __init__(self, pin, initial_degree=MIN_DEGREE):
        self._pwm = PWM(Pin(pin, Pin.OUT))
        self._pwm.freq(self.DEFAULT_FREQ)
        self._current_degree = self.MIN_DEGREE
        self.set_angle(initial_degree)

    # Imposta direttamente il duty cycle verificando i limiti meccanici
    def _set_duty(self, value):
        if not (self.MIN_DUTY <= value <= self.MAX_DUTY):
            raise ValueError(
                f"Duty cycle must be in range [{self.MIN_DUTY}; {self.MAX_DUTY}]."
            )
        self._pwm.duty(value)

    # Restituisce l'angolo corrente del servomotore (0 - 180)
    def get_degree(self):
        return self._current_degree

    # Imposta l'angolo del servomotore in gradi (0 - 180)
    def set_angle(self, degree):
        if not (self.MIN_DEGREE <= degree <= self.MAX_DEGREE):
            raise ValueError(
                f"Degree must be in range [{self.MIN_DEGREE}; {self.MAX_DEGREE}]."
            )

        duty = int((degree / self.MAX_DEGREE) * (self.MAX_DUTY - self.MIN_DUTY) + self.MIN_DUTY)
        self._set_duty(duty)
        self._current_degree = degree

    # Sposta il servomotore nella posizione minima (0 gradi)
    def move_to_min(self):
        self.set_angle(self.MIN_DEGREE)

    # Sposta il servomotore nella posizione centrale (90 gradi)
    def move_center(self):
        self.set_angle((self.MIN_DEGREE + self.MAX_DEGREE) // 2)

    # Sposta il servomotore nella posizione massima (180 gradi)
    def move_to_max(self):
        self.set_angle(self.MAX_DEGREE)

    # Sposta il servomotore di un incremento relativo rispetto all'angolo attuale
    def move_by(self, delta_degree):
        target = max(self.MIN_DEGREE, min(self.MAX_DEGREE, self._current_degree + delta_degree))
        self.set_angle(target)

    # Rilascia la risorsa PWM disalimentando il segnale del servo
    def deinit(self):
        self._pwm.duty(0)
        self._pwm.deinit()