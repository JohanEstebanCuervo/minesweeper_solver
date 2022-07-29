import pyautogui
import time
import cv2
import numpy as np

from methods import *

size_monitor = pyautogui.size()

#Abre Chrome y carga buscaminas.eu
pyautogui.press('win')
time.sleep(0.5)
pyautogui.write('chrome')
time.sleep(0.1)
pyautogui.press('enter')
time.sleep(2)
pyautogui.press('tab')
time.sleep(1)
pyautogui.press('enter')
time.sleep(0.3)
pyautogui.hotkey('ctrl', 't')
time.sleep(0.2)
pyautogui.write('buscaminas.eu')
pyautogui.press('enter')
time.sleep(6)


imagen = np.array(pyautogui.screenshot())

ventana = FindWindow(imagen, imshow=False)

juego = np.array(pyautogui.screenshot(region=ventana))

points, tam = FindMatrix(juego, imshow=False)


inicio = int(np.random.random() * 63)
ClickCells([inicio], points, ventana)

Logic_Matrix = np.ones((8, 8)).astype('int') * (-1)  # -1 sin información
Ant = np.copy(Logic_Matrix)
dif = True
Cell_unlock = list(range(64))
Active_cells = []
auto = 0

while dif:
    Logic_Matrix, Cell_unlock, Active_cells = RefreshGame(ventana, points, tam, Logic_Matrix, Cell_unlock, Active_cells)
    Logic_Matrix, Cell_unlock, Active_cells, free = CalculateBooms(Logic_Matrix, Cell_unlock, Active_cells)
    free = list(set(free))
    ClickCells(free, points, ventana)
    # Logic_Matrix, Cell_unlock, Active_cells = RefreshGame(ventana, points, tam, Logic_Matrix, Cell_unlock, Active_cells)
    if free:
        print(free)
    if np.sum(np.abs(Ant - Logic_Matrix)) == 0:
        auto += 1
        if auto == 1:
            dif = False
        else:
            rand = int(np.random.random() * len(Cell_unlock))

            ClickCells([Cell_unlock[rand]], points, ventana)

            print('Aleatorio!')

    if not Cell_unlock:

        print('JUEGO TERMINADO :)')
        dif = False

    else:

        Ant = np.copy(Logic_Matrix)

print(Logic_Matrix)

cv2.destroyAllWindows()
