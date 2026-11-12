from machine import Pin
import utime


class StepMotor:

    CW = 1
    CCW = -1

    FULL_STEPS_PER_REV = 2048
    HALF_STEPS_PER_REV = 4096

    FULL_STEP_SEQUENCE = (
        (1, 0, 0, 1),
        (1, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 1, 1),
    )

    HALF_STEP_SEQUENCE = (
        (1, 0, 0, 0),
        (1, 0, 0, 1),
        (0, 0, 0, 1),
        (0, 0, 1, 1),
        (0, 0, 1, 0),
        (0, 1, 1, 0),
        (0, 1, 0, 0),
        (1, 1, 0, 0),
    )

    # Inizializza il motore passo-passo (es. 28BYJ-48) dai numeri di pin o oggetti Pin
    def __init__(self, pins, delay=0.005, half_step=False):
        if len(pins) != 4:
            raise ValueError("StepMotor requires exactly 4 control pins.")

        self._pins = [
            p if isinstance(p, Pin) else Pin(p, Pin.OUT) for p in pins
        ]
        self._delay = delay
        self._step_index = 0

        if half_step:
            self._sequence = self.HALF_STEP_SEQUENCE
            self._steps_per_rev = self.HALF_STEPS_PER_REV
        else:
            self._sequence = self.FULL_STEP_SEQUENCE
            self._steps_per_rev = self.FULL_STEPS_PER_REV

        self._seq_len = len(self._sequence)
        self.turn_off()

    # Esegue un numero specifico di passi nella direzione indicata (CW=1, CCW=-1)
    def step(self, steps, direction=CW, auto_off=True):
        if direction not in (self.CW, self.CCW):
            raise ValueError("Direction must be StepMotor.CW (1) or StepMotor.CCW (-1).")

        for _ in range(abs(steps)):
            self._step_index = (self._step_index + direction) % self._seq_len

            for pin_idx in range(4):
                self._pins[pin_idx].value(self._sequence[self._step_index][pin_idx])

            utime.sleep(self._delay)

        if auto_off:
            self.turn_off()

    # Ruota il motore di un angolo specifico in gradi
    def rotate_degrees(self, degrees, direction=CW, auto_off=True):
        steps = int((abs(degrees) / 360.0) * self._steps_per_rev)
        self.step(steps, direction=direction, auto_off=auto_off)

    # Ruota il motore di un numero specificato di giri completi
    def rotate_revolutions(self, revolutions, direction=CW, auto_off=True):
        steps = int(abs(revolutions) * self._steps_per_rev)
        self.step(steps, direction=direction, auto_off=auto_off)

    # Imposta il ritardo tra un passo e il successivo in secondi
    def set_speed(self, delay):
        if delay <= 0:
            raise ValueError("Delay must be strictly positive.")
        self._delay = delay

    # Toglie alimentazione a tutte le bobine per evitare surriscaldamento
    def turn_off(self):
        for pin in self._pins:
            pin.value(0)