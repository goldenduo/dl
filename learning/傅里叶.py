import torch
import matplotlib.pyplot as plt
import numpy as np

# 设置字体支持，使用更通用的配置
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 创建x轴数据点
x = torch.linspace(-np.pi, np.pi, 1000, device=device)

# 定义目标矩形函数
def rectangle(x):
    result = torch.zeros_like(x)
    result[(x >= -np.pi/2) & (x <= np.pi/2)] = 1.0
    return result

# 计算傅里叶级数逼近
def fourier_series(x, n_terms):
    result = torch.zeros_like(x)
    for n in range(1, n_terms + 1, 2):  # 只取奇数项
        result += (4 / (n * np.pi)) * torch.sin(n * x)
    return result

# 创建子图
fig, axs = plt.subplots(3, 2, figsize=(15, 12))
axs = axs.flatten()

# 原始矩形函数
rect = rectangle(x)
axs[0].plot(x.cpu().numpy(), rect.cpu().numpy(), 'b-', linewidth=2)
axs[0].set_title('Original Rectangle Function', fontsize=14)
axs[0].set_ylim(-0.2, 1.2)
axs[0].grid(True)

# 不同阶数的傅里叶级数逼近
n_terms_list = [1, 3, 5, 15, 51]
for i, n_terms in enumerate(n_terms_list):
    approx = fourier_series(x, n_terms)
    axs[i+1].plot(x.cpu().numpy(), approx.cpu().numpy(), 'r-', linewidth=2)
    axs[i+1].plot(x.cpu().numpy(), rect.cpu().numpy(), 'b--', linewidth=1, alpha=0.5)
    axs[i+1].set_title(f'Fourier Series ({n_terms} terms)', fontsize=14)
    axs[i+1].set_ylim(-0.2, 1.2)
    axs[i+1].grid(True)

plt.tight_layout()
plt.show()

# 创建动态演示图 - 展示不同项数的叠加效果
fig, ax = plt.subplots(figsize=(10, 6))
rect_line, = ax.plot(x.cpu().numpy(), rect.cpu().numpy(), 'b--', linewidth=1, alpha=0.5, label='Ideal Rectangle')
approx_line, = ax.plot([], [], 'r-', linewidth=2, label='Fourier Series Approximation')
ax.set_ylim(-0.2, 1.2)
ax.set_xlim(-np.pi, np.pi)
ax.grid(True)
ax.set_title('Dynamic Demonstration of Fourier Series Approximation', fontsize=16)
ax.legend()

# 绘制个别正弦项
n_max = 21  # 最大项数
for n_terms in range(1, n_max + 1, 2):
    approx = fourier_series(x, n_terms)
    approx_line.set_data(x.cpu().numpy(), approx.cpu().numpy())
    ax.set_title(f'Fourier Series Approximation ({n_terms} terms)', fontsize=16)
    plt.pause(0.5)

plt.show()

# 附加可视化：单个正弦项的贡献
fig, ax = plt.subplots(figsize=(12, 6))
x_np = x.cpu().numpy()
rect_np = rect.cpu().numpy()

ax.plot(x_np, rect_np, 'k--', linewidth=1.5, label='Ideal Rectangle')
ax.set_ylim(-1.0, 1.5)
ax.set_xlim(-np.pi, np.pi)
ax.grid(True)
ax.set_title('Contributions of Fourier Series Terms', fontsize=16)

# 绘制前5个奇数项及其部分和
colors = ['r', 'g', 'b', 'm', 'c']
partial_sum = np.zeros_like(x_np)

for i, n in enumerate(range(1, 10, 2)):
    term = (4 / (n * np.pi)) * np.sin(n * x_np)
    partial_sum += term

    if i < len(colors):
        ax.plot(x_np, term, colors[i], linewidth=1, alpha=0.7, label=f'n={n} term')

    if i == 2:  # 显示前5项的部分和
        ax.plot(x_np, partial_sum, 'r-', linewidth=2, label='Sum of first 5 terms')

ax.legend()
plt.tight_layout()
plt.show()