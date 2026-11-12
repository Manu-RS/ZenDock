import utime

class StepMotor:
    step_sequence = [
        [1, 0, 0, 1],  
        [1, 1, 0, 0],  
        [0, 1, 1, 0],  
        [0, 0, 1, 1],  
    ]
    
    step_sequence_half = [
        [1,0,0,0],  
        [1,0,0,1],  
        [0,0,0,1],  
        [0,0,1,1],  
        [0,0,1,0],  
        [0,1,1,0],  
        [0,1,0,0],  
        [1,1,0,0],  
    ]
    
    def __init__(self, pins, delay=0.05, half=False):
        self.pins = pins
        self.delay = delay
        self.step_index = 0
        self.num_pins = len(pins)
        
        if half:
            self.seq_len = len(self.step_sequence_half)
            self.sequence = self.step_sequence_half
            self.steps_per_revolution = 4096
        else:
            self.seq_len = len(self.step_sequence)
            self.sequence = self.step_sequence
            self.steps_per_revolution = 2048

    def step(self, direction, steps):
        for _ in range(steps):
            self.step_index = (self.step_index + direction) % self.seq_len
            
            for pin_idx in range(self.num_pins):
                pin_value = self.sequence[self.step_index][pin_idx]
                self.pins[pin_idx].value(pin_value)
            
            utime.sleep(self.delay)
        
        self.turnOff()

    def setSpeed(self, delay):
        self.delay = delay

    def turnOff(self):
        for pin in self.pins:
            pin.value(0)