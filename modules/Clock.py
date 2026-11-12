import time
from sensors import StepMotor

class Clock:
    GEAR_RATIO = 3.75
    
    def __init__(self, pins, delay=0.05, half=False):
        self.motor = StepMotor(pins, delay, half)
        self.steps_per_rev = self.motor.steps_per_revolution
        
        self.steps_per_minute = (self.steps_per_rev * self.GEAR_RATIO) / 60.0
        
        # Stato interno: tempo attuale in minuti (da 0 a 719, formato 12 ore)
        self.current_minutes = 0

    def setTime(self, hours, minutes):
        """Imposta l'orario attuale senza muovere le lancette (punto zero)."""
        self.current_minutes = (hours % 12) * 60 + minutes
        print(f"Orologio calibrato alle {hours:02d}:{minutes:02d}")

    def moveBy(self, hours=0, minutes=0, seconds=0):
        """Sposta in avanti o indietro di una quantità relativa."""
        total_minutes_to_move = (hours * 60) + minutes + (seconds / 60.0)
        
        steps_to_move = int(abs(total_minutes_to_move) * self.steps_per_minute)
        direction = 1 if total_minutes_to_move >= 0 else -1
        
        if steps_to_move > 0:
            self.motor.step(direction, steps_to_move)
            self.motor.turnOff()
            
        # Aggiorna lo stato interno
        self.current_minutes = (self.current_minutes + total_minutes_to_move) % 720

    def smartMoveTo(self, target_hours, target_minutes):
        """
        Sposta l'orologio all'orario indicato scegliendo il percorso più breve.
        Se la differenza è > 6 ore, gira in senso antiorario per fare prima.
        """
        target_total_minutes = (target_hours % 12) * 60 + target_minutes
        
        # Calcola la differenza in minuti
        diff = target_total_minutes - self.current_minutes
        
        # Normalizza la differenza tra -360 e +360 (percorso più breve su quadrante 12h)
        if diff > 360:
            diff -= 720
        elif diff < -360:
            diff += 720
            
        print(f"Spostamento intelligente: differenza di {diff} minuti.")
        self.move_by(minutes=diff)

    def test_mode(self, duration_sec):
        """
        Testa il motore alla massima velocità per X secondi, tiene traccia dei passi,
        e poi torna esattamente alla posizione di partenza.
        """
        print(f"Avvio test di {duration_sec} secondi a massima velocità...")
        original_delay = self.motor.delay
        
        # Imposta la velocità massima (delay minimo tollerato dal motore, es. 2ms)
        self.motor.setSpeed(0.002) 
        
        start_time = time.ticks_ms()
        steps_taken = 0
        direction = 1 # Senso orario
        
        # Gira finché non scade il tempo
        while time.ticks_diff(time.ticks_ms(), start_time) < (duration_sec * 1000):
            self.motor.step(direction, 1)
            steps_taken += 1
            
        print(f"Test completato. Eseguiti {steps_taken} passi. Ritorno alla posizione iniziale...")
        
        # Riavvolge esattamente i passi fatti in senso antiorario
        self.motor.step(-direction, steps_taken)
        
        # Ripristina lo stato
        self.motor.setSpeed(original_delay)
        self.motor.turnOff()
        print("Test terminato, orario inalterato.")