# Johan Esteban Cuervo Chica
from methods import *
import time

print('espera')
time.sleep(4)
print('inicia')
solver = solver_mw(difficulty='expert', random=False)
#solver.InitGame(tim=5, browser='chrome')
solver.solve()