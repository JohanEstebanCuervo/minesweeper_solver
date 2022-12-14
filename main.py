# Johan Esteban Cuervo Chica
from methods import *
import time
import pyautogui
import os

print('espera')
time.sleep(3)
print('inicia')
sol = 0
iterations = 10
for i in range(iterations):
    solver = solver_mw(difficulty='expert', random=True)
    #  solver.InitGame(tim=5, browser='chrome')
    solver.solve()

    if not solver.Cell_unknown:
        sol +=1
        pyautogui.moveTo(960, 5)
        pyautogui.click()

    os.system('cls')
    pyautogui.press('F2')
    time.sleep(0.5)

    print(sol)

print(sol/iterations)
