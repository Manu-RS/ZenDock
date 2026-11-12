import time
from sensors import StepMotor


class Clock:

    GEAR_RATIO = 3.75
    MINUTES_PER_CYCLE = 720
    MIN_TEST_DELAY = 0.002

    # Inizializza l'orologio analogico motorizzato con rapporto di riduzione meccanico
    def __init__(self, pins, delay=0.05, half_step=False):
        self._delay = delay
        self._half_step = half_step
        self._motor = StepMotor(pins, delay=delay, half_step=half_step)

        steps_per_rev = (
            StepMotor.HALF_STEPS_PER_REV if half_step else StepMotor.FULL_STEPS_PER_REV
        )
        self._steps_per_minute = (steps_per_rev * self.GEAR_RATIO) / 60.0

        # Stato interno: tempo attuale in minuti (0 - 719, formato 12 ore)
        self._current_minutes = 0.0
        # Accumulatore per non perdere frazioni di passo nei piccoli avanzamenti
        self._step_remainder = 0.0

    # Imposta l'orario attuale senza muovere le lancette (calibrazione punto zero)
    def set_time(self, hours, minutes):
        if not (0 <= minutes < 60):
            raise ValueError("Minutes must be in range [0; 59].")

        self._current_minutes = float((hours % 12) * 60 + minutes)
        self._step_remainder = 0.0
        print(f"Orologio calibrato alle {hours % 12 or 12:02d}:{minutes:02d}")

    # Restituisce l'orario corrente delle lancette come tupla (ore_12h, minuti)
    def get_time(self):
        total_min = int(round(self._current_minutes)) % self.MINUTES_PER_CYCLE
        hours = total_min // 60
        minutes = total_min % 60
        return (12 if hours == 0 else hours, minutes)

    # Restituisce l'orario corrente formattato come stringa 'HH:MM'
    def get_formatted_time(self):
        hours, minutes = self.get_time()
        return f"{hours:02d}:{minutes:02d}"

    # Sposta le lancette in avanti o indietro di una quantità relativa
    def move_by(self, hours=0, minutes=0, seconds=0):
        total_minutes = (hours * 60) + minutes + (seconds / 60.0)
        exact_steps = (total_minutes * self._steps_per_minute) + self._step_remainder

        steps_to_move = int(exact_steps)
        self._step_remainder = exact_steps - steps_to_move

        if steps_to_move != 0:
            direction = StepMotor.CW if steps_to_move > 0 else StepMotor.CCW
            self._motor.step(abs(steps_to_move), direction=direction, auto_off=True)

        self._current_minutes = (self._current_minutes + total_minutes) % self.MINUTES_PER_CYCLE

    # Fa avanzare l'orologio di un singolo minuto
    def tick_minute(self):
        self.move_by(minutes=1)

    # Sposta l'orologio all'orario indicato scegliendo il percorso più breve su 12 ore
    def smart_move_to(self, target_hours, target_minutes):
        if not (0 <= target_minutes < 60):
            raise ValueError("Target minutes must be in range [0; 59].")

        target_total_minutes = (target_hours % 12) * 60 + target_minutes
        diff = target_total_minutes - self._current_minutes

        # Normalizza la differenza tra -360 e +360 minuti per il percorso più breve
        if diff > 360:
            diff -= self.MINUTES_PER_CYCLE
        elif diff < -360:
            diff += self.MINUTES_PER_CYCLE

        print(f"Spostamento intelligente: differenza di {diff:.1f} minuti.")
        self.move_by(minutes=diff)

    # Imposta la velocità di movimento delle lancette (ritardo tra passi in secondi)
    def set_speed(self, delay):
        self._motor.set_speed(delay)
        self._delay = delay

    # Testa il motore alla massima velocità per X secondi e torna alla posizione iniziale
    def test_mode(self, duration_sec):
        print(f"Avvio test di {duration_sec} secondi a massima velocità...")
        original_delay = self._delay

        self._motor.set_speed(self.MIN_TEST_DELAY)
        start_time = time.ticks_ms()
        steps_taken = 0

        while time.ticks_diff(time.ticks_ms(), start_time) < (duration_sec * 1000):
            self._motor.step(1, direction=StepMotor.CW, auto_off=False)
            steps_taken += 1

        self._motor.turn_off()
        print(f"Test completato. Eseguiti {steps_taken} passi. Ritorno alla posizione iniziale...")

        # Riavvolge esattamente i passi fatti in senso antiorario
        self._motor.step(steps_taken, direction=StepMotor.CCW, auto_off=True)

        # Ripristina la velocità originale
        self._motor.set_speed(original_delay)
        print("Test terminato, orario inalterato.")