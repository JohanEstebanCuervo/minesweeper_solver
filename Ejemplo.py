import numpy as np

rows = 3
columns = 5

vect = np.arange(rows * columns)
matriz = vect.reshape((rows,columns))

print(matriz)
