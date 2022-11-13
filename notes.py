base = 4
note_map = {
    261.63: 'C',
    277.18: 'C#',
    293.66: 'D',
    311.13: 'D#',
    329.63: 'E',
    349.23: 'F',
    369.99: 'F#',
    392: 'G',
    415.3: 'G#',
    440: 'A',
    466.16: 'A#',
    493.88: 'B',
}

freqs = list(note_map.keys())
for freq in freqs:
    note = note_map[freq]
    for i in range(3):
        note_map[freq*(2**i)] = (note, i+base)
note_map[246.94] = ('B', 3)

def freq_to_note(freq):
    closest = min(note_map.keys(), key = lambda x:abs(x-freq))
    dist = abs(freq-closest)
    if dist/freq > 0.05:
        #print(freq, dist)
        return '?'
    return note_map[closest]

def filter_notes(notes):
    notes = [(n,a,f) for (n,a,f) in notes if n != '?']
    return notes