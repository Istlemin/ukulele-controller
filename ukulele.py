from pathlib import Path

notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def note_to_num(note):
    s,n = note
    return 12*n+notes.index(s)

def note_diff(n1,n2):
    return note_to_num(n1)-note_to_num(n2)

class Song:
    def  __init__(self,path):
        self.notes = []
        for s in Path(path).read_text().split("\n"):
            if s:
                self.notes.append((s[:-1],int(s[-1])))
            else:
                self.notes.append(None)


class Tuning:
    def __init__(self,strings=[('G',4),('C',4),('E',4),('A',4)]):
        self.strings = strings
        self.lowest = min(strings, key=note_to_num)

    def note_to_string(self,note):
        best = (-1,1e18)
        while note_to_num(note) < note_to_num(self.lowest):
            note = (note[0],note[1] + 1)
        for i in range(1,4):
            diff = note_diff(note,self.strings[i])
            if diff>=0 and diff<best[1]:
                best = (i,diff)
        #print(best)
        return best


if __name__=="__main__":
    tuning = Tuning()
    for note in Song("songs/twinkletwinkle.song").notes:
        if note is not None:
            print(tuning.note_to_string(note))
        else:
            print()