import numpy as np


x = np.array([[2,3],[0,0]])

y = x.sum(axis=1)
print(y)

if list(np.where(y==0)[0]):
    print('si')
else:
    print('no')
