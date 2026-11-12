from sensors import StepMotor, Servo, Buzzer, Led, LDR, Potenziometro
from machine import Pin, ADC
import time

# --- CONFIGURAZIONE PIN ---
PIN_LDR = 34
PIN_POT = 35
PIN_LED = 5
PIN_SERVO = 15
PIN_STEPPER = [26, 25, 33, 32]
PIN_BTN = 14
PIN_BUZZER = 12

# --- INIZIALIZZAZIONE OGGETTI ---

fotoresistore = LDR(PIN_LDR, min_value=0, max_value=4095)
potenziometro = Potenziometro(PIN_POT, "ADC.ATTN_11DB")

led = Led(PIN_LED, frequency=5000)
servo = Servo(PIN_SERVO)

stepper_pins = [Pin(p, Pin.OUT) for p in PIN_STEPPER]
stepper = StepMotor(stepper_pins, delay=0.002, half=True)

button = Pin(PIN_BTN, Pin.IN, Pin.PULL_UP)
buzzer = Buzzer(PIN_BUZZER, pDuty=0, pFreq=1000)

# --- VARIABILI GLOBALI ---
modalita = "AUTO"

# Valori sensori
luminosita = 0
soglia = 0

# Valori soglie potenziometro
sogliaMin = 1000
sogliaMax = 3000

# Stato Stepper
stepper_pos = 0
stepper_target = 0
stepper_last = 0
stato_illuminazione_precedente = None 

# Stato Pulsante (Debouncing)
last_press = 0

# Stato Buzzer e Allarme
buzzer_inizio_fase = 0
buzzer_durata_corrente = 0
inizio_buio = 0
allarme_emesso = False
buzzer_sequenza = []
buzzer_timeout = 0

ultimo_tempo_stampa = 0

# --- FUNZIONI DI CONTROLLO ---

def leggi_sensori():
    global luminosita
    global soglia
    
    luminosita = fotoresistore.read()
    soglia = potenziometro.readByRange(sogliaMin, sogliaMax)


def controlla_led():
    # Modalità AUTO
    if modalita == "AUTO":
        diff = soglia - luminosita
        if diff > 800:
            led.setPercentage(100)
        elif 400 <= diff <= 800:
            led.setPercentage(70)
        elif 100 <= diff < 400:
            led.setPercentage(30)
        else:
            led.setPercentage(0)
    # Modalità MANUAL
    else:
        percentuale = ((soglia - 1000) / 2000) * 100
        led.setPercentage(max(0, min(100, int(percentuale))))


def controlla_servo():
    # Modalità AUTO
    # controlla_servo() non impone al servo di andare subito all'angolo calcolato di 5 gradi in 5, bensì sposta avanti o dietro
    # di 5 gradi in base a dove si trova e non blocca il resto del programma
    # viene chiamato continuamente dal main, quindi si comporta come un ciclo ma non è bloccante
    
    if modalita == "AUTO":    
        if luminosita < soglia:
            degree = 0
        elif luminosita > soglia and luminosita < (soglia+500):
            degree = 45
        elif luminosita > (soglia+500):
            degree = 90
            
        if (servo.getCurrentDegree() < degree):
            servo.setDegree(getCurrentDegree() + 5)
        elif (servo.getCurrentDegree() > degree):
            servo.setDegree(getCurrentDegree() - 5)
            
    # Modalità MANUAL
    else:
        servo.setDegree(90)


def controlla_stepper():
    global stepper_pos, stepper_target, stepper_last
    global stato_illuminazione_precedente
    
    tempo_corrente = time.ticks_ms()
    
    if modalita == "AUTO":
        is_luminoso = (luminosita >= soglia)
        if is_luminoso != stato_illuminazione_precedente:
            if not is_luminoso: 
                stepper_posizione_target = 512
            else:               
                stepper_posizione_target = 0
            stato_illuminazione_precedente = is_luminoso

    if stepper_po != stepper_target:
        if time.ticks_diff(tempo_corrente, stepper_last) >= 2:		# 2 è delay
            direzione = 1 if stepper_target > stepper_pos else -1
         
            stepper.step(direzione, 1)    
            stepper_pos += direzione
            stepper_last = tempo_corrente
            
            if stepper_pos == stepper_target:
                stepper.turnOff()


def gestisci_pulsante():
    global last_press
    global modalita
    current_time = time.ticks_ms()
    
    # Gestione del debounce
    if time.ticks_diff(current_time, last_press) > 200:
        last_press = current_time
    
        if modalita == "AUTO":
            modalita = "MANUAL"
            buzzer_sequenza.append((2000, 300)) 	# Un beep 2000 Hz 300ms
        else:
            modalita = "AUTO"
            buzzer_sequenza.extend([(1500, 100), (0, 50), (1500, 100)])		# Due beep 1500 Hz 100ms


def gestisci_buzzer():
    global inizio_buio, allarme_emesso, buzzer_coda, buzzer_timeout
    tempo_corrente = time.ticks_ms()

    # Logica di allarme
    if modalita == "AUTO":
        if luminosita < 500:
            if inizio_buio == 0:
                inizio_buio = tempo_corrente
            elif time.ticks_diff(tempo_corrente, inizio_buio) >= 5000 and not allarme_emesso:
                buzzer_coda.extend([(800, 150), (0, 150)] * 3)
                allarme_emesso = True
        else:
            inizio_buio = 0
            allarme_emesso = False 
            
    # Esecutore non bloccante della coda
    if tempo_corrente >= buzzer_timeout:
        if buzzer_coda:
            freq, durata = buzzer_coda.pop(0)
            if freq > 0:
                buzzer.pwm.freq(freq)
                buzzer.pwm.duty(512)
            else:
                buzzer.pwm.duty(0)
            buzzer_timeout = tempo_corrente + durata
        else:
            buzzer.pwm.duty(0)


# --- SETUP INIZIALE ---
button.irq(trigger=Pin.IRQ_RISING, handler=gestisci_pulsante)
buzzer.riproduciSuono(1000, 200, 512) # Un beep all'avvio
buzzer.stop()

# --- MAIN LOOP ---
while True:
    tempo_corrente = time.ticks_ms()
    
    leggi_sensori()
    gestisci_pulsante()
    
    controlla_led()
    controlla_servo()
    controlla_stepper()
    gestisci_buzzer()
    
    if time.ticks_diff(tempo_corrente, ultimo_tempo_stampa) >= 1000:
        print(f"Lum: {luminosita:.0f} | Soglia: {soglia:.0f} | Mod: {modalita}")
        ultimo_tempo_stampa = tempo_corrente
        
    time.sleep_ms(1)