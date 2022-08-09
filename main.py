# Johan Esteban Cuervo Chica
from methods import *
import time
import pyautogui
import os

print('espera')
time.sleep(3)
print('inicia')

for i in range(20):
    solver = solver_mw(difficulty='expert', random=True)
    #  solver.InitGame(tim=5, browser='chrome')
    solver.solve()

    if not solver.Cell_unknown:
        time.sleep(13)
        os.system('cls')
        pyautogui.press('F2')
        time.sleep(2)

    else:
        os.system('cls')
        pyautogui.press('F2')
        time.sleep(2)
