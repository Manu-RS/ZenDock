from sensors import StepMotor, Servo, Buzzer, Led, Ldr, Potentiometer
from machine import Pin
import time

# --- CONFIGURAZIONE PIN ---
PIN_LDR = 34
PIN_POT = 35
PIN_LED = 5
PIN_SERVO = 15
PIN_STEPPER = [26, 25, 33, 32]
PIN_BTN = 14
PIN_BUZZER = 12

# --- COSTANTI ---
SOGLIA_MIN = 1000
SOGLIA_MAX = 3000
SOGLIA_BUIO_ALLARME = 500
TEMPO_BUIO_ALLARME_MS = 5000
DEBOUNCE_MS = 200
STEPPER_DELAY_MS = 2
STEPPER_TARGET_BUIO = 512

# --- INIZIALIZZAZIONE OGGETTI ---
fotoresistore = Ldr(PIN_LDR, min_value=0, max_value=4095)
potenziometro = Potentiometer(PIN_POT)

led = Led(PIN_LED, frequency=5000)
servo = Servo(PIN_SERVO)
stepper = StepMotor(PIN_STEPPER, delay=STEPPER_DELAY_MS / 1000.0, half_step=True)

button = Pin(PIN_BTN, Pin.IN, Pin.PULL_UP)
buzzer = Buzzer(PIN_BUZZER, default_duty=512, default_freq=1000)

# --- VARIABILI GLOBALI ---
modalita = "AUTO"

# Valori sensori
luminosita = 0
soglia = 0

# Stato Stepper
stepper_pos = 0
stepper_target = 0
stepper_last_ms = 0
stato_illuminazione_precedente = None

# Stato Pulsante (Debouncing)
last_press_ms = 0

# Stato Buzzer e Allarme
inizio_buio_ms = 0
allarme_emesso = False
buzzer_coda = []
buzzer_timeout_ms = 0

ultimo_tempo_stampa_ms = 0

# --- FUNZIONI DI CONTROLLO ---

# Legge la luminosità dall'LDR e la soglia dal Potentiometer
def leggi_sensori():
    global luminosita, soglia

    luminosita = fotoresistore.read_raw(samples=3)
    soglia = Potentiometer.read_range(SOGLIA_MIN, SOGLIA_MAX, samples=3)


# Regola l'intensità del LED in modalità automatica o manuale
def controlla_led():
    if modalita == "AUTO":
        diff = soglia - luminosita
        if diff > 800:
            led.set_percentage(100)
        elif 400 <= diff <= 800:
            led.set_percentage(70)
        elif 100 <= diff < 400:
            led.set_percentage(30)
        else:
            led.set_percentage(0)
    else:
        percentuale = ((soglia - SOGLIA_MIN) / (SOGLIA_MAX - SOGLIA_MIN)) * 100
        led.set_percentage(max(0, min(100, int(percentuale))))


# Muove gradualmente il servomotore di 5 gradi alla volta senza bloccare il ciclo
def controlla_servo():
    if modalita == "AUTO":
        if luminosita < soglia:
            target_degree = 0
        elif luminosita < (soglia + 500):
            target_degree = 45
        else:
            target_degree = 90

        current_degree = servo.get_degree()
        if current_degree < target_degree:
            servo.move_by(min(5, target_degree - current_degree))
        elif current_degree > target_degree:
            servo.move_by(-min(5, current_degree - target_degree))
    else:
        servo.move_center()


# Gestisce il posizionamento non bloccante del motore passo-passo
def controlla_stepper():
    global stepper_pos, stepper_target, stepper_last_ms, stato_illuminazione_precedente

    tempo_corrente = time.ticks_ms()

    if modalita == "AUTO":
        is_luminoso = luminosita >= soglia
        if is_luminoso != stato_illuminazione_precedente:
            stepper_target = 0 if is_luminoso else STEPPER_TARGET_BUIO
            stato_illuminazione_precedente = is_luminoso

    if stepper_pos != stepper_target:
        if time.ticks_diff(tempo_corrente, stepper_last_ms) >= STEPPER_DELAY_MS:
            direzione = StepMotor.CW if stepper_target > stepper_pos else StepMotor.CCW
            stepper.step(1, direction=direzione, auto_off=False)
            stepper_pos += direzione
            stepper_last_ms = tempo_corrente

            if stepper_pos == stepper_target:
                stepper.turn_off()


# Gestisce la pressione del pulsante con antirimbalzo (compatibile con IRQ)
def gestisci_pulsante(pin=None):
    global last_press_ms, modalita

    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_press_ms) > DEBOUNCE_MS:
        last_press_ms = current_time

        if modalita == "AUTO":
            modalita = "MANUAL"
            buzzer_coda.append((2000, 300))
        else:
            modalita = "AUTO"
            buzzer_coda.extend([(1500, 100), (0, 50), (1500, 100)])


# Gestisce l'allarme buio prolungato e riproduce la coda sonora in modo non bloccante
def gestisci_buzzer():
    global inizio_buio_ms, allarme_emesso, buzzer_timeout_ms

    tempo_corrente = time.ticks_ms()

    # Logica di allarme se resta buio per oltre 5 secondi in modalità AUTO
    if modalita == "AUTO":
        if luminosita < SOGLIA_BUIO_ALLARME:
            if inizio_buio_ms == 0:
                inizio_buio_ms = tempo_corrente
            elif time.ticks_diff(tempo_corrente, inizio_buio_ms) >= TEMPO_BUIO_ALLARME_MS and not allarme_emesso:
                buzzer_coda.extend([(800, 150), (0, 150)] * 3)
                allarme_emesso = True
        else:
            inizio_buio_ms = 0
            allarme_emesso = False

    # Esecutore non bloccante della coda suoni tramite Timer hardware del Buzzer
    if time.ticks_diff(tempo_corrente, buzzer_timeout_ms) >= 0:
        if buzzer_coda:
            freq, durata = buzzer_coda.pop(0)
            if freq > 0:
                buzzer.play_tone_async(durata, frequency=freq)
            else:
                buzzer.stop()
            buzzer_timeout_ms = time.ticks_add(tempo_corrente, durata)


# --- SETUP INIZIALE ---
button.irq(trigger=Pin.IRQ_FALLING, handler=gestisci_pulsante)
buzzer.play_tone(200, frequency=1000)

# --- MAIN LOOP ---
while True:
    tempo_corrente = time.ticks_ms()

    leggi_sensori()
    controlla_led()
    controlla_servo()
    controlla_stepper()
    gestisci_buzzer()

    if time.ticks_diff(tempo_corrente, ultimo_tempo_stampa_ms) >= 1000:
        print(f"Lum: {luminosita:.0f} | Soglia: {soglia:.0f} | Mod: {modalita}")
        ultimo_tempo_stampa_ms = tempo_corrente

    time.sleep_ms(1)