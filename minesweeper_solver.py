"""
Objeto que resuelve el juego buscaminas.

programmed by Johan Esteban Cuervo Chica
"""

import sys
import time
import cv2
import numpy as np
import pyautogui

class MinesWeeperSolver():
    """
    Clase que resuelve el buscaminas clasico de la pagina cell_unknown
    https://buscaminas.eu/

    Puede iniciar automaticamente el navegador e iniciar el juego
    """
    def __init__(self, difficulty='beginner', random=False, sleep=0.1):

        self.calculate_rowcol(difficulty)

        self.logicmatrix = np.ones((self.rows, self.columns)).astype('int')*(-1)  # -1 sin información
        self.logicmatrix_After = np.copy(self.logicmatrix)
        self.cell_unknown = list(range(self.num_cells))
        self.active_cells = []
        self.random = random
        self.sleep = sleep
        self.imshow = False
        self.numbers = np.array([[0, 0, 255], [0, 123, 0],
                                 [255, 0, 0], [0, 0, 123], [123, 0, 0],
                                 [0, 123, 123], [0, 0, 0]]).astype('int')

        self.Logic = {}
        for Cell in range(self.num_cells):
            Neighbours = self.CalculateNeigt(Cell)
            self.Logic[Cell] = {}
            self.Logic[Cell]['emptys_neighbors'] = Neighbours.copy()
            self.Logic[Cell]['neighbors'] = Neighbours.copy()
            self.Logic[Cell]['emptys'] = len(Neighbours)
            self.Logic[Cell]['val'] = -1
            self.Logic[Cell]['booms'] = 0

    def init_game(self, tim: float= 0.1, browser:str='chrome') -> None:
        """
        Open the browser and charge buscaminas.eu
        Args:
            tim (float, optional): time sleep for each action, depends on the 
                                   internet and computer. Defaults to 0.1.
            browser (str, optional): Name navigator. Defaults to 'chrome'.
        """
        pyautogui.press('win')
        time.sleep(tim / 2)
        pyautogui.write(browser)
        time.sleep(tim / 15)
        pyautogui.press('enter')
        time.sleep(tim / 3)
        pyautogui.press('tab')
        time.sleep(tim / 3)
        pyautogui.press('enter')
        time.sleep(tim / 10)
        pyautogui.hotkey('ctrl', 't')
        time.sleep(tim / 15)
        pyautogui.write('buscaminas.eu')
        pyautogui.press('enter')
        time.sleep(tim)

    def calculate_rowcol(self, difficulty: str) -> None:
        """
        Calculate the number rows, columns, cells
        according to the given difficulty

        Args:
            difficulty (str): (beginner, intermediate, expert)

        Raises:
            ChildProcessError: Non-existent option
        """
        if difficulty == 'beginner':
            self.rows = 8
            self.columns = 8
            self.booms = 10
            self.relac1 = 1.24
            self.relac2 = 1.25

        elif difficulty == 'intermediate':
            self.rows = 16
            self.columns = 16
            self.booms = 40
            self.relac1 = 1.12
            self.relac2 = 1.13

        elif difficulty == 'expert':
            self.rows = 16
            self.columns = 31
            self.booms = 99
            self.relac1 = 0.61
            self.relac2 = 0.61

        else:

            raise ChildProcessError(f'Dificultad no Validad: {difficulty}')

        self.num_cells = self.rows * self.columns

    def FindWindow(self):
        image = np.array(pyautogui.screenshot())
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        borders = cv2.Canny(image_gray, 10, 150)
        borders = cv2.dilate(borders, None, iterations=2)
        borders = cv2.erode(borders, None, iterations=1)

        if self.imshow:
            cv2.imshow('imagen', borders)
            cv2.waitKey(0)

        outlines, _ = cv2.findContours(borders, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if self.imshow:
            image2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.drawContours(image2, outlines, -1, (0, 0, 255), 2)
            cv2.imshow('imagen', image2)
            cv2.waitKey(0)

        ventana = []
        for contorno in outlines:
            approx = cv2.approxPolyDP(contorno, 10, True)
            if len(approx) == 4:

                h = (approx[1] - approx[0])[0][1]
                w = (approx[2] - approx[0])[0][0]
                # print(str(w) + ', ' + str(h))

                if w != 0:
                    relac = round(np.abs(h / w), 2)
                else:
                    relac = 0

                if relac == self.relac1 or relac == self.relac2:

                    ventana.append(approx)

        if self.imshow:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.drawContours(image, ventana, -1, (0, 0, 255), 2)
            cv2.imshow('imagen', image)
            cv2.waitKey(0)

        if len(ventana) == 1:

            ventana = ventana[0]

            y, x = ventana[0][0]
            w = (ventana[1] - ventana[0])[0][1]
            h = (ventana[2] - ventana[0])[0][0]

            if self.imshow:
                game = image_gray[x: x + w, y: y + h]

                cv2.imshow('juego', game)
                cv2.waitKey(0)

            self.ventana = np.array([y, x, h, w])
            return 0
        else:
            print('Ventanas equiv:', len(ventana))
        return 1

    def FindMatrix(self):
        game = np.array(pyautogui.screenshot(region=self.ventana))
        game_gray = cv2.cvtColor(game, cv2.COLOR_BGR2GRAY)

        _, game_bin = cv2.threshold(game_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.imshow:
            cv2.imshow('Binaria', game_bin)
            cv2.waitKey(0)

        outlines, _ = cv2.findContours(game_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        if self.imshow:
            game_1 = cv2.cvtColor(game, cv2.COLOR_RGB2BGR)
            contornos2 = list(outlines)
            contornos2.append(np.array([[[0, 0]], [[0, 310]], [[310, 310]], [[310, 0]]]).astype('int32'))
            cv2.drawContours(game_1, contornos2, -1, (0, 0, 255), 2)
            cv2.imshow('outlines', game_1)
            cv2.waitKey(0)

        squares = []
        points = []
        tams = []
        for contorno in outlines:
            x, y, w, h = cv2.boundingRect(contorno)
            relac = round(float(w) / h, 1)
            if relac == 1.0:
                axes = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]).astype('int32')
                init = np.array([x, y]).astype('int')
                points.append(init)
                tams.append(w)
                squares.append(axes)

        moda = np.median(tams)

        if len(squares) > self.num_cells:
            squares_mode = []
            points_mode = []
            for iterator in range(len(squares)):

                if tams[iterator] < moda + 2 and tams[iterator] > moda - 2:
                    squares_mode.append(squares[iterator])
                    points_mode.append(points[iterator])

            squares = squares_mode
            points = points_mode
            if self.imshow:
                game_2 = cv2.cvtColor(game, cv2.COLOR_RGB2BGR)
                cv2.drawContours(game_2, squares, -1, (0, 0, 255), 2)
                cv2.imshow('outlines', game_2)
                cv2.waitKey(0)

        if len(squares) == self.num_cells:
            points = np.array(points)
            points += int(moda // 2)  # Num_celd * 2

            args = np.argsort(points[:, 1])

            points = points[list(args), :]

            for i in range(self.rows):
                args = np.argsort(points[i * self.columns: (i + 1) * self.columns, 0])
                args += i * self.columns
                points[i * self.columns: (i + 1) * self.columns, :] = points[list(args), :]

            self.points = points
            self.size_cell = int(moda) - 3
            return 0

        else:
            print('Se encontraron:', len(squares), 'Cuadros de:', self.num_cells)

        return 1

    def ClickCells(self, indexs, button='left', tim=0.00):

        for index in indexs:
            point = self.points[index, :] + self.ventana[: 2]
            pyautogui.moveTo(int(point[0]), int(point[1]), tim)
            pyautogui.click(button=button)

    def calculate_cell(self, cell_pixels: np) -> int:
        """
        Esta función calcula el número de una celda enviada
        """
        black = False
        white = False
        pixels = self.size_cell**2
        rect_list = cell_pixels.reshape((-1, 3))  # Num_pixeles * 3 RGB

        sum_rec = np.sum(rect_list, axis=1)
        if list(np.where(sum_rec==0)[0]):
            black = True
        if list(np.where(sum_rec>=735)[0]):
            white = True

        if white and black:
            raise ChildProcessError('Juego Perdido')

        if white and not black:
            return

        for index in range(len(rect_list)):
            equal = np.where(np.sum(np.abs(self.numbers - rect_list[index, :]), axis=1) == 0)[0]

            if len(equal):
                return equal[0] + 1

            if index > pixels / 4:
                return 0

    def RefreshGame(self, free_booms):
        free = free_booms.copy()
        juego = np.array(pyautogui.screenshot(region=self.ventana))

        for cell in free:
            if not(cell in self.cell_unknown):
                continue

            inicix = int(self.points[cell, 1] - self.size_cell // 2)
            iniciy = int(self.points[cell, 0] - self.size_cell // 2)
            rect_cell = juego[inicix: inicix + self.size_cell, iniciy:iniciy + self.size_cell, :]

            num = self.calculate_cell(rect_cell)
            if num is None:
                continue
                    
            self.ActualiceNeighbour(cell, num)
            if num == 0:
                free += self.Logic[cell]['emptys_neighbors']

    def ActualiceNeighbour(self, Cell, value):
        self.cell_unknown.remove(Cell)
        self.Logic[Cell]['val'] = value
        if value != 0:
            self.active_cells.append(Cell)

        for Neighbour in self.Logic[Cell]['neighbors']:
            self.Logic[Neighbour]['emptys'] -= 1
            self.Logic[Neighbour]['emptys_neighbors'].remove(Cell)

    def IsBoom(self, Cell):
        self.booms -= 1
        self.cell_unknown.remove(Cell)
        self.Logic[Cell]['val'] = 'X'

        for Neighbour in self.Logic[Cell]['neighbors']:
            self.Logic[Neighbour]['emptys'] -= 1
            self.Logic[Neighbour]['booms'] += 1
            self.Logic[Neighbour]['emptys_neighbors'].remove(Cell)

    def CalculateBooms(self):

        free_booms = []
        booms = []
        act_cells = self.active_cells.copy()
        for Cell in act_cells:

            Dif = self.Logic[Cell]['val'] - self.Logic[Cell]['booms']

            if Dif == self.Logic[Cell]['emptys']:
                self.active_cells.remove(Cell)
                emptys = self.Logic[Cell]['emptys_neighbors'].copy()
                for empty in emptys:
                    self.IsBoom(empty)
                    booms.append(empty)

            elif Dif == 0:
                self.active_cells.remove(Cell)
                for empty in self.Logic[Cell]['emptys_neighbors']:
                    free_booms.append(empty)

            elif Dif < 0:
                print('Error en la solucion')
                print('diferencia', Dif)
                print('Celda', Cell)
                self.Solve_Act

        free_booms = list(set(free_booms))
        booms = list(set(booms))
        return free_booms, booms

    def CalculateNeigt(self, Cell, cant='All'):
        Neighbours = []
        Remove = []
        Neighbours.append(Cell - self.columns - 1)
        Neighbours.append(Cell - self.columns)
        Neighbours.append(Cell - self.columns + 1)
        Neighbours.append(Cell - 1)
        Neighbours.append(Cell + 1)
        Neighbours.append(Cell + self.columns - 1)
        Neighbours.append(Cell + self.columns)
        Neighbours.append(Cell + self.columns + 1)

        if Cell % self.columns == 0:

            Remove.append(Cell - self.columns - 1)
            Remove.append(Cell - 1)
            Remove.append(Cell + self.columns - 1)

        if (Cell + 1) % self.columns == 0:
            Remove.append(Cell - self.columns + 1)
            Remove.append(Cell + 1)
            Remove.append(Cell + self.columns + 1)

        if Cell - self.columns < 0:
            Remove.append(Cell - self.columns - 1)
            Remove.append(Cell - self.columns)
            Remove.append(Cell - self.columns + 1)

        if Cell + self.columns > self.num_cells - 1:
            Remove.append(Cell + self.columns - 1)
            Remove.append(Cell + self.columns)
            Remove.append(Cell + self.columns + 1)

        if cant == 'rect':
            Remove.append(Cell - self.columns - 1)
            Remove.append(Cell - self.columns + 1)
            Remove.append(Cell + self.columns - 1)
            Remove.append(Cell + self.columns + 1)

        Remove = list(set(Remove))

        for R in Remove:

            Neighbours.remove(R)

        return Neighbours

    def advance_methods(self):

        free_booms = []
        booms = []

        for Cell in self.active_cells:
            emptys_sum = {}
            Dif = self.Logic[Cell]['val'] - self.Logic[Cell]['booms']
            Num_emptys = self.Logic[Cell]['emptys']
            for empty in self.Logic[Cell]['emptys_neighbors']:
                emptys_sum[empty] = Dif

            Neighbours4 = self.CalculateNeigt(Cell, cant='rect')
            for Cell2 in Neighbours4:
                sumas = emptys_sum.copy()

                if Cell2 < Cell:
                    continue

                if not (Cell2 in self.active_cells):
                    continue

                if self.Logic[Cell2]['val'] < 1:
                    continue

                Dif2 = self.Logic[Cell2]['val'] - self.Logic[Cell2]['booms']

                for empty in self.Logic[Cell2]['emptys_neighbors']:

                    if empty in list(sumas.keys()):
                        sumas[empty] += Dif2
                    else:
                        sumas[empty] = Dif2

                minimum = min(sumas.values())
                valores = list(sumas.values())
                claves = list(sumas.keys())
                Num_emptys2 = self.Logic[Cell2]['emptys']

                if (len(sumas) == Num_emptys or len(sumas) == Num_emptys2) and Num_emptys2 != Num_emptys and Dif + Dif2 == 2:
                    indexs = np.where(np.array(valores) == minimum)[0]
                    for index in indexs:
                        free_booms.append(claves[index])

                elif len(sumas) == 3 and valores.count(minimum) == 1 and Dif + Dif2 == 3:

                    index = valores.index(minimum)
                    booms.append(claves[index])

                elif len(sumas) == 4 and valores.count(minimum) == 1 and valores.count(minimum + 1) == 1:

                    if Dif + Dif2 == 3:
                        index = valores.index(minimum)
                        free_booms.append(claves[index])

                        index = valores.index(minimum + 1)
                        booms.append(claves[index])

        free_booms = list(set(free_booms))
        booms = list(set(booms))
        for Cell in booms:
            if not (Cell in self.cell_unknown):
                print('error al calcular: ', Cell)
                self.Solve_Act

            self.IsBoom(Cell)

        return free_booms, booms

    def solve(self):

        if self.FindWindow():
            print('Fallo al encontrar el area del juego')
            sys.exit()

        if self.FindMatrix():
            print('Fallo al encontrar la cuadricula del juego')
            sys.exit()

        cell_init = int(np.random.random() * self.num_cells)
        self.ClickCells([cell_init])

        self.Solve_Act = True
        max_rand = 10
        free = [cell_init]
        try:
            while self.Solve_Act:
                Actualice_ok = False
                Attemp = 0
                while not Actualice_ok and Attemp < 10:
                    Actualice_ok = True
                    Attemp += 1
                    self.RefreshGame(free)
                    for cell in free:
                        if cell in self.cell_unknown:
                            Actualice_ok = False
                            continue

                if Attemp == 10 and not Actualice_ok:

                    print('No fue posible actualizar los valores del juego')
                    break

                free, booms = self.CalculateBooms()

                if free:
                    self.ClickCells(free)
                    print(free)

                if booms:
                    self.ClickCells(booms, button='right')

                if not self.cell_unknown:

                    print('JUEGO TERMINADO :)')
                    self.Solve_Act = False

                if not free and not booms and self.cell_unknown:

                    free, booms = self.advance_methods()
                    if free:
                        print('libres advance:')
                        self.ClickCells(free)
                        print(free)

                    if booms:
                        print('Bombas Advance')
                        self.ClickCells(booms, button='right')
                        print(booms)

                    if not free and not booms:
                        max_rand -= 1
                        if not self.random or max_rand < 1:
                            print('No se encontro solución')
                            self.Solve_Act = False

                        else:
                            rand = int(np.random.random() * len(self.cell_unknown))
                            free.append(self.cell_unknown[rand])
                            self.ClickCells(free)
                            print('Aleatorio!')

            self.print_game()

        except ChildProcessError as error:
            print(error)

    def print_game(self):
        for Cell in range(self.num_cells):
            if self.Logic[Cell]['val'] == -1:
                print(" ", end=" ")
            else:
                print(self.Logic[Cell]['val'], end=" ")
            if (Cell + 1) % self.columns == 0:
                print(" ")
