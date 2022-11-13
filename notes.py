base = 4
note_map = {
    440: 'A',
    329.63: 'E',
    261.63: 'C',
    392: 'G',
    277.18: 'C#',
    293.66: 'D',
    311.13: 'D#',
    349.23: 'F',
    369.99: 'F#',
    415.3: 'G#',
    466.16: 'A#',
    493.88: 'B',
}

freqs = list(note_map.keys())
for freq in freqs:
    note = note_map[freq]
    for i in range(2):
        note_map[freq*(2**i)] = (note, i+base)

def freq_to_note(freq):
    closest = min(note_map.keys(), key = lambda x:abs(x-freq))
    dist = abs(freq-closest)
    if dist/freq > 0.05:
        print(freq, dist)
        return '?'
    return note_map[closest]

def filter_notes(notes):
    notes = [(n,a,f) for (n,a,f) in notes if n != '?']
    return [n for (n,a,f) in notes]