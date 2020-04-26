#!/usr/bin/env python3
#
# Copyright (c) 2015 Hyeshik Chang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from collections import Counter
import numpy as np
from random import randrange

class Emitter:

    def __init__(self, events):
        count = Counter(events)

        counts_sorted = sorted(count.items())

        self.edges = list(np.cumsum([cnt for e, cnt in counts_sorted]))
        self.emissions = [e for e, cnt in counts_sorted]

    def __call__(self):
        rv = randrange(self.edges[-1] + 1)
        for edge, emission in zip(self.edges, self.emissions):
            if rv <= edge:
                return emission
        raise ValueError


class ChainGenerator:

    def __init__(self, emitters):
        self.emitters = emitters

    def generate(self, num):
        ret = []

        for i in range(num):
            position, seq = 0, ['>']
            while seq[-1] != '<':
                emission = self.emitters[position, seq[-1]]()
                seq.append(emission)
                position += 1

            yield ''.join(seq)[1:-1]

def load_sequence_pattern():
    sequences = open('training.txt').read().split()
    events = {}

    for seq in sequences:
        for pos, (a, b) in enumerate(zip('>' + seq, seq + '<')):
            events.setdefault((pos, a), [])
            events[pos, a].append(b)

    emitters = {prev: Emitter(emit) for prev, emit in events.items()}
    return ChainGenerator(emitters)


if __name__ == '__main__':
    pat = load_sequence_pattern()
    for i, seq in enumerate(pat.generate(100000)):
        print('>{}'.format(i+1))
        print(seq.replace('U', 'T'))


