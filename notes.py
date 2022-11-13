
note_map = {
    440: 'A4',
    329.63: 'E4',
    261.63: 'C4',
    392: 'G4',
    277.18: 'C#4',
    293.66: 'D4',
    311.13: 'D#4',
    349.23: 'F4',
    369.99: 'F#4',
    415.3: 'G#4',
    466.16: 'A#4',
    493.88: 'B4',
}

notes = list(note_map.keys())
for freq in notes:
    for i in range(2):
        note_map[freq*(2**i)] = note_map[freq][:-1]+str(i+4)

def to_note(freq):
    closest = min(note_map.keys(), key = lambda x:abs(x-freq))
    dist = abs(freq-closest)
    if dist/freq > 0.05:
        print(freq, dist)
        return '?'
    return note_map[closest]

def filter_notes(notes):
    notes = [(n,a,f) for (n,a,f) in notes if n != '?']
    return [n for (n,a,f) in notes]