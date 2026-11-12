from machine import Pin, PWM, Timer
from time import sleep_ms


class Buzzer:

    DEFAULT_FREQUENCY = 440
    DEFAULT_DUTY = 512
    DEFAULT_NOTE_MS = 200
    DEFAULT_PAUSE_MS = 30

    # Frequenze standard (Hz) per facilitare la scrittura delle melodie
    NOTES = {
        "REST": 0, "P": 0,
        "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349,
        "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494,
        "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698,
        "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988,
        "C6": 1047,
    }

    # Inizializza il buzzer passivo sul pin PWM e prepara il timer asincrono
    def __init__(self, pin, default_duty=DEFAULT_DUTY, default_freq=DEFAULT_FREQUENCY, timer_id=-1):
        self._pwm = PWM(Pin(pin, Pin.OUT))
        self._pwm.duty(0)
        self._default_freq = default_freq
        self._default_duty = default_duty
        self._timer = Timer(timer_id)
        self._muted = False

    # Callback interna chiamata allo scadere del Timer
    def _on_timer(self, timer):
        self.stop()

    # Converte il nome della nota (es. 'C4') o un intero nella frequenza in Hz
    def _resolve_frequency(self, note):
        if isinstance(note, str):
            freq = self.NOTES.get(note.strip().upper())
            if freq is None:
                raise ValueError(f"Unknown note: {note}")
            return freq
        return int(note)

    # Analizza una melodia in formato stringa (es. 'C4:200 E4:200 G4:400') o lista
    def _parse_melody(self, melody, default_duration):
        if isinstance(melody, str):
            parsed = []
            for token in melody.split():
                if ":" in token:
                    note_part, dur_part = token.split(":", 1)
                    parsed.append((note_part, int(dur_part)))
                else:
                    parsed.append((token, default_duration))
            return parsed

        parsed = []
        for item in melody:
            if isinstance(item, (tuple, list)):
                parsed.append((item[0], item[1]))
            else:
                parsed.append((item, default_duration))
        return parsed

    # Attiva o disattiva la modalità silenziosa senza alterare il resto del codice
    def set_muted(self, muted):
        self._muted = bool(muted)
        if self._muted:
            self.stop()

    # Restituisce True se il buzzer è attualmente silenziato
    def is_muted(self):
        return self._muted

    # Silenzia immediatamente il buzzer
    def stop(self):
        self._pwm.duty(0)

    # Riproduce un singolo tono in modo bloccante
    def play_tone(self, duration_ms, frequency=None, duty=None):
        if self._muted:
            return

        freq = self._default_freq if frequency is None else self._resolve_frequency(frequency)
        pwm_duty = self._default_duty if duty is None else duty

        if freq > 0:
            self._pwm.freq(freq)
            self._pwm.duty(pwm_duty)
        else:
            self.stop()

        sleep_ms(duration_ms)
        self.stop()

    # Riproduce un singolo tono senza bloccare il programma tramite Timer
    def play_tone_async(self, duration_ms, frequency=None, duty=None):
        self._timer.deinit()
        if self._muted:
            return

        freq = self._default_freq if frequency is None else self._resolve_frequency(frequency)
        pwm_duty = self._default_duty if duty is None else duty

        if freq > 0:
            self._pwm.freq(freq)
            self._pwm.duty(pwm_duty)
            self._timer.init(
                mode=Timer.ONE_SHOT,
                period=duration_ms,
                callback=self._on_timer,
            )
        else:
            self.stop()

    # Riproduce una melodia da stringa ('C4:200 E4:200'), lista di tuple o lista di note
    def play_melody(self, melody, note_duration_ms=DEFAULT_NOTE_MS, pause_ms=DEFAULT_PAUSE_MS, duty=None):
        if self._muted:
            return

        pwm_duty = self._default_duty if duty is None else duty
        steps = self._parse_melody(melody, note_duration_ms)

        for note, duration in steps:
            freq = self._resolve_frequency(note)

            if freq == 0:
                self.stop()
            else:
                self._pwm.freq(freq)
                self._pwm.duty(pwm_duty)

            sleep_ms(duration)
            self.stop()

            if pause_ms > 0:
                sleep_ms(pause_ms)

    # Ferma il suono e rilascia Timer e PWM
    def deinit(self):
        self._timer.deinit()
        self.stop()
        self._pwm.deinit()