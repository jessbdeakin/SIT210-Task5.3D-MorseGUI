import tkinter as tk
import tkinter.messagebox as tkmessagebox
import RPi.GPIO as gpio
import time


window = tk.Tk()

def loop(func, period):
    def wrapped():
        func()
        window.after(period, wrapped)
    wrapped()
    
#####################

gpio.setmode(gpio.BOARD)

class Blink():
    pin = None
    
    cycle = 0
    period = 50 # milliseconds
    
    pulses = []
    
    @staticmethod
    def set_pin(pin):
        for p in pin:
            gpio.output(p, gpio.LOW)
        Blink.pin = pin
        
    @staticmethod
    def push(pulse):
        Blink.pulses.append(pulse)
        
    @staticmethod
    def clear():
        Blink.pulses = []
        
    @staticmethod
    def do_cycle():
        if len(Blink.pulses) == 0:
            return
        
        pulse = Blink.pulses[0]
        
        inner = Blink.cycle
        inner %= ((pulse[0] + pulse[1]) // Blink.period)
        
        if inner == pulse[0] // Blink.period:
            gpio.output(Blink.pin, gpio.LOW)
        elif inner == 0:
            gpio.output(Blink.pin, gpio.HIGH)
        
        if (inner + 1) == ((pulse[0] + pulse[1]) // Blink.period):
            Blink.pulses.pop(0)
            Blink.cycle = 0
        else:
            Blink.cycle += 1
    
led = 11
gpio.setup(led, gpio.OUT)
Blink.set_pin([led])

###################

class Morse():
    
    unit_length = 100
    
    SILENT_DOT = 0b000
    LOUD_DOT = 0b001
    SILENT_DASH = 0b010
    LOUD_DASH = 0b011
    SPACE = 0b100
    
    pulse_types = [
        (0, unit_length),
        (unit_length, unit_length),
        (0, 3 * unit_length),
        (3 * unit_length, unit_length),
        (0, 6 * unit_length)
    ]
    
    pulse_notation = ['', '.', '/', '-', ' ']
    
    encoding = {
        ' ': "4",
        
        '.': "131313",
        ',': "331133",
        '?': "113311",
        "'": "133331",
        '/': "31131",
        ':': "333111",
        ';': "313131",
        '+': "13131",
        '-': "311113",
        '=': "31113",
        
        '1': "33333",
        '3': "13333",
        '2': "11333",
        '3': "11133",
        '4': "11113",
        '5': "11111",
        '6': "31111",
        '7': "33111",
        '8': "33311",
        '9': "33331",
        
        'a': "13",
        'b': "3111",
        'c': "3131",
        'd': "311",
        'e': "1",
        'f': "1131",
        'g': "331",
        'h': "1111",
        'i': "11",
        'j': "1333",
        'k': "313",
        'l': "1311",
        'm': "33",
        'n': "31",
        'o': "333",
        'p': "1331",
        'q': "3313",
        'r': "131",
        's': "111",
        't': "3",
        'u': "113",
        'v': "1113",
        'w': "133",
        'x': "3113",
        'y': "3133",
        'z': "3311"
    }
    
    @staticmethod
    def print(message):
        clean = message.lower()
        
        print(f"Encoded \"{clean}\" as: ", end="")
        
        for char in clean:
            encoding = Morse.encoding[char]
            
            for symbol in encoding:
                symbol = ord(symbol) - ord('0')
                
                print(Morse.pulse_notation[symbol], Morse.pulse_notation[Morse.SILENT_DOT], end="", sep="")
                
            print(Morse.pulse_notation[Morse.SILENT_DASH],end="")
        print()
    
    @staticmethod
    def push(message):
        
        clean = message.lower()
        
        for char in clean:
            encoding = Morse.encoding[char]
            
            for symbol in encoding:
                symbol = ord(symbol) - ord('0')
                
                Blink.push( Morse.pulse_types[symbol] )
                Blink.push( Morse.pulse_types[Morse.SILENT_DOT] )
                
            Blink.push( Morse.pulse_types[Morse.SILENT_DASH] )
       
###################
            
message_max_length = 12
    
def validate_text(text):
    if len(text) > message_max_length:
        window.after(10, lambda : tkmessagebox.showinfo("Error", "Message too long."))
        return False
    
    return True
       
def handle_signal(text_field):
    Blink.clear()
    Morse.push( text_field.get() )
    Morse.print( text_field.get() )

###################
    
text_field = tk.Entry(
    validate = 'key',
    validatecommand = (window.register(validate_text), '%P')
)
    
signal_button = tk.Button(
    text = "Signal",
    command = lambda : handle_signal(text_field)
)
    
exit_button = tk.Button(
    text = "Exit",
    command = window.destroy
)

text_field.grid(row=0, column=0, columnspan=2)
signal_button.grid(row=1, column=0)
exit_button.grid(row=1, column=1)

###########W

window.eval(f'tk::PlaceWindow {window.winfo_pathname(window.winfo_id())} center')

loop(Blink.do_cycle, Blink.period)
window.mainloop()

gpio.cleanup()

