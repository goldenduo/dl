import torch
import numpy as np
import matplotlib.pyplot as plt

x=np.arange(0.001,1,0.001)
y=-np.log(x)*x

# plt.axis('equal')
plt.plot(x,y)

plt.grid(True)  # （可选）显示网格线
plt.show()
