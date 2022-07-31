import numpy as np

rows = 16
columns = 16

vect = np.arange(rows * columns)
matriz = vect.reshape((rows,columns))

print(matriz)
