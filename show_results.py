#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.optimize import minimize


def read_results(file='./results.dat'):
    if not os.path.exists(file):
        return None
    data = []
    with open(file, 'r') as f:
        line = f.readline()
        num = 1
        while line:
            res = eval(line)
            assert isinstance(res, tuple), f'line {num} is not a tuple {res}'
            assert all([isinstance(item, (float, int)) for item in res]), f'line {num} contains non-number {res}'
            data.append(res)
            line = f.readline()
            num += 1
    return data

data = read_results()
results = sorted(data, key=lambda x: x[0])
ratios = [r[0] for r in results]
percents = [r[1] for r in results]

# # Weight ratio data by 'accuracy' (how many flips were taken)
# ratios, percents = [], []
# for i in results:
#     for _ in range(int(np.round(i[2]/1000))):  # every 1000 flips gets another data point
#         ratios.append(i[0])
#         percents.append(i[1])

fig = plt.figure(figsize=(7,4))
plt.scatter(ratios, percents)

coeffs = np.polyfit(ratios, percents, deg=3)
line = np.poly1d(coeffs)
plt.plot(ratios, line(ratios), color='r')

best = minimize(line, x0=min(percents))
print(f'Projected best: at ratio: {best.x[0]} with loss: {best.fun}')

plt.plot([best.x, best.x], [-0.01, 1/4])
plt.title(f"Projected best ratio:{best.x[0]}")
fig.savefig('results.png')
plt.show()
