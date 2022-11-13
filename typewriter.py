from device import Device, Microphone
from whackamole import UkuleleInput
from keyboard import strum_to_key
from ukulele import Tuning
import pyautogui as pg

class UkeInputStream:
    def __init__(self, tuning:Tuning = Tuning(), thresh = 0.001):
        self.mic = Microphone()
        self.device = Device()
        self.last = None
        self.amplitude = None
        self.tuning = tuning
        self.thresh = thresh

        self.should_run=True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.should_run:
            self.mic.tick(self.device)

    def get_note(self):
        note, amplitude = self.device.get_state()
        if note is not None and amplitude > self.thresh:
            if self.amplitude is None or amplitude > self.amplitude or self.last!=note:
                self.last = note
                self.amplitude = amplitude
                return self.tuning.note_to_string(note)
        self.amplitude = amplitude
        self.last = note


inp = UkuleleInput(tuning = Tuning([('F#', 4), ('B', 3), ('E', 4), ('A', 4)]))
shift=False
while True:
    strum = inp.get_note()
    if strum is not None:
        #print(strum)
        if shift:
            strum = (strum[0],strum[1]+5)
            shift=False        
        c = strum_to_key(strum)
        if c is None:
            c = strum_to_key((strum[0],strum[1]-12))
        if c is not None:
            if c=='z':
                shift=True
            elif c=='x':
                pg.press('backspace')
            else:
                #print(c,flush=True, end='')
                pg.press(c)

