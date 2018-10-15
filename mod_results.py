
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
    if 0.92<i[0]<1.01:
        for _ in range(int(i[2]/100)):
            ratios.append(i[0])
            percents.append(i[1])

fig = plt.figure(figsize=(7,4))
plt.scatter(ratios, percents)

coeffs = np.polyfit(ratios, percents, deg=2)
line = np.poly1d(coeffs)
plt.plot(ratios, line(ratios))

best = minimize(line, x0=losses[0][0])
print(f'projected best: at ratio: {best.x[0]} with loss: {best.fun}')

plt.plot([best.x, best.x], [-0.01, 1/3])
plt.title(label=f"Projected best ratio:{best.x[0]}")
plt.show()
fig.savefig('results.png')
