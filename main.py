# Johan Esteban Cuervo Chica
import time
import pyautogui
import os
from minesweeper_solver import MinesWeeperSolver


print('espera')
time.sleep(2)
print('inicia')
sol = 0
iterations = 3
for i in range(iterations):
    solver = MinesWeeperSolver(difficulty='expert', random=False)
    #  solver.InitGame(tim=5, browser='chrome')
    solver.solve()

    if not solver.cell_unknown:
        sol +=1
        pyautogui.moveTo(960, 5)
        pyautogui.click()

    os.system('cls')
    pyautogui.press('F2')
    time.sleep(0.5)

    print(sol)

print(sol/iterations)
