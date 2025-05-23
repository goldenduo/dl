import matplotlib.pyplot as plt
import numpy as np

# 生成示例数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 绘制网格线
plt.grid(True)

# 绘制蓝色实线，linewidth=2
plt.plot(x, y, 'b-', linewidth=2)

# 显示图形
plt.show()