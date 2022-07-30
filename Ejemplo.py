import numpy as np

rows = 8
columns = 8

vect = np.arange(rows * columns)
matriz = vect.reshape((rows,columns))

print(matriz)
