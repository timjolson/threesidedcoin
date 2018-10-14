
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 15:39:47 2018

@author: t
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

def read_results(file='./results.dat'):
    ratios, percents, iters = [], [], []
    
    with open(file, 'r') as f:
        line = f.readline()
        num = 1
        while line:
            res = eval(line)
            assert isinstance(res, tuple), f'line {num} is not a tuple {res}'
            assert all([isinstance(item, (float, int)) for item in res]), f'line {num} contains non-number {res}'
            ratios.append(res[0])
            percents.append(res[1])
            iters.append(res[2])
            
            line = f.readline()
            num += 1
    
    return ratios, percents, iters

ratios, percents, iters = read_results()
results = sorted(zip(ratios, percents, iters), key=lambda x: x[0])
losses = sorted(results, key=lambda x: x[1])

ratios, percents = [], []
for i in results:
    # each 200 flips counts the data point again
    # ~~weights more flips heavier (assume more accurate result)
    for _ in range(int(np.round(i[2]/200))):
    #for _ in range(i[2]):
        ratios.append(i[0])
        percents.append(i[1])

plt.scatter(ratios, percents)

coeffs = np.polyfit(ratios, percents, deg=2)
line = np.poly1d(coeffs)
plt.plot(ratios, line(ratios))

best = minimize(line, x0=losses[0][0])
print(f'projected best: at ratio: {best.x} with loss: {best.fun}')

plt.plot([best.x, best.x], [-.01, 1/3])
plt.title(label=f"{coeffs[0]}*r^2 + {coeffs[1]}*r + {coeffs[2]}")
plt.show()
