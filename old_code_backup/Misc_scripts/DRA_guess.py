import numpy as np
from matplotlib import pyplot as plt


def eff(a, b, c, d, v, vi, m):
    return (((c * v * m) ** 0.25) / ((d * vi) ** 0.5) - a) / (b - a)


vi_lst = np.arange(0.5, 5.5, 0.1)*1e-6
v_lst = np.arange(0.5, 1.5, 0.1)
m_lst = np.arange(0, 10, 1)/1000


# for i in range(10000):
#     print('run ', i)
#     flag = 0
#     a = -50 + np.random.rand()*100
#     b = -50 + np.random.rand()*100
#     c = np.random.rand()*100
#     d = np.random.rand()*100
#     for vi in vi_lst:
#         for v in v_lst:
#             for m in m_lst:
#                 f = eff(a, b, c, d, v, vi, m)
#                 # print('f', f)
#                 if f>1 or f<0:
#                     flag = 1
#     if flag == 0:
#         print('a = ', a, ',b = ', b, ',c = ', c, ',d = ', d)
#         break

a = 45.705
b = -25.34
c = 0.1256
d = 41.9

# a = 28.54
# b = -39.49
# c = 0.0657
# d = 81.298

# v = 1.91
# vi = 0.000002
# m = 50/3600         # m3/s
# print(eff(a, b, c, d, v, vi, m))

efficiency = []
DRA_flow = 50/3600         # m3/s
vi = 0.000002
velocity = np.arange(0.4, 2, 0.1)      # m/s
for val in velocity:
    efficiency.append(eff(a, b, c, d, val, vi, DRA_flow)*100)

plt.plot(velocity, efficiency)
plt.plot(velocity, efficiency, 'o')
plt.xlabel('Product velocity m/s')
plt.ylabel('DRA Efficiency %')
plt.show()
