"""
Objeto que resuelve el juego buscaminas.

programmed by Johan Esteban Cuervo Chica
"""

import time
from cv2 import cv2
import numpy as np
import pyautogui

class MinesWeeperSolver():
    """
    Class that solves the classic minesweeper of the cell_unknown page
    https://minbusweeper.eu/

    You can automatically start the browser and start the game
    """
    def __init__(self, difficulty='beginner', random=False, sleep=0.1) -> None:

        self.calculate_rowcol(difficulty)

        self.logicmatrix = np.ones((self.rows, self.columns)).astype('int')*(-1)
        self.logicmatrix_after = np.copy(self.logicmatrix)
        self.cell_unknown = list(range(self.num_cells))
        self.active_cells = []
        self.random = random
        self.window = None
        self.points = None
        self.size_cell = None
        self.sleep = sleep
        self.imshow = False
        self.numbers = np.array([[0, 0, 255], [0, 123, 0],
                                 [255, 0, 0], [0, 0, 123], [123, 0, 0],
                                 [0, 123, 123], [0, 0, 0]]).astype('int')

        self.logic = {}
        for cell in range(self.num_cells):
            neighbours = self.calculate_neighbor(cell)
            self.logic[cell] = {}
            self.logic[cell]['emptys_neighbors'] = neighbours.copy()
            self.logic[cell]['neighbors'] = neighbours.copy()
            self.logic[cell]['emptys'] = len(neighbours)
            self.logic[cell]['val'] = -1
            self.logic[cell]['booms'] = 0

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

    def find_window(self) -> bool:
        """
        Calculate the position of window the game

        Returns:
            bool: True on failure, False on success
        """
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

                height = (approx[1] - approx[0])[0][1]
                width = (approx[2] - approx[0])[0][0]

                if width != 0:
                    relac = round(np.abs(height / width), 2)
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

            posy, posx = ventana[0][0]
            width = (ventana[1] - ventana[0])[0][1]
            height = (ventana[2] - ventana[0])[0][0]

            if self.imshow:
                game = image_gray[posx: posx + width, posy: posy + height]

                cv2.imshow('juego', game)
                cv2.waitKey(0)

            self.window = np.array([posy, posx, height, width])
            return False
        else:
            print('Ventanas equiv:', len(ventana))
        return True

    def find_matrix(self) -> bool:
        """
        Calculate the position of cells the game

        Returns:
            bool: True on failure, False on success
        """
        game = np.array(pyautogui.screenshot(region=self.window))
        game_gray = cv2.cvtColor(game, cv2.COLOR_BGR2GRAY)

        _, game_bin = cv2.threshold(game_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.imshow:
            cv2.imshow('Binaria', game_bin)
            cv2.waitKey(0)

        outlines, _ = cv2.findContours(game_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        if self.imshow:
            game_1 = cv2.cvtColor(game, cv2.COLOR_RGB2BGR)
            contornos2 = list(outlines)
            contornos2.append(
                np.array([[[0, 0]], [[0, 310]], [[310, 310]], [[310, 0]]]).astype('int32'))
            cv2.drawContours(game_1, contornos2, -1, (0, 0, 255), 2)
            cv2.imshow('outlines', game_1)
            cv2.waitKey(0)

        squares = []
        points = []
        tams = []
        for contorno in outlines:
            posx, posy, width, height = cv2.boundingRect(contorno)
            relac = round(float(width) / height, 1)
            if relac == 1.0:
                axes = np.array([
                    [posx, posy],
                    [posx + width, posy],
                    [posx + width, posy + height],
                    [posx, posy + height]
                    ]).astype('int32')
                init = np.array([posx, posy]).astype('int')
                points.append(init)
                tams.append(width)
                squares.append(axes)

        moda = np.median(tams)

        if len(squares) > self.num_cells:
            squares_mode = []
            points_mode = []
            for iterator, square in enumerate(squares):

                if tams[iterator] < moda + 2 and tams[iterator] > moda - 2:
                    squares_mode.append(square)
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
            return False

        else:
            print('Se encontraron:', len(squares), 'Cuadros de:', self.num_cells)

        return True

    def click_cells(self, indexs: list, button: str='left', tim: float=0.00) -> None:
        """
        click the given list of cells

        Args:
            indexs (list): list of cells
            button (str, optional): (left, right). Defaults to 'left'.
            tim (float, optional): time to move the pointer. Defaults to 0.00.
        """
        for index in indexs:
            point = self.points[index, :] + self.window[: 2]
            pyautogui.moveTo(int(point[0]), int(point[1]), tim)
            pyautogui.click(button=button)

    def calculate_cell(self, cell_pixels: object) -> int:
        """
        calculates the number of a cell

        Args:
            cell_pixels (object): numpy.Array the dim (n,n,3)

        Raises:
            ChildProcessError: If the cell is Boom -> Game Over

        Returns:
            int: number in cell
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

    def refresh_game(self, free_booms: list) -> None:
        """
        update the game given the cells free of bombs.
        also updates the neighbors of the cells with 0 bombs

        Args:
            free_booms (list): list of cell free bombs
        """
        free = free_booms.copy()
        juego = np.array(pyautogui.screenshot(region=self.window))

        for cell in free:
            if cell not in self.cell_unknown:
                continue

            inicix = int(self.points[cell, 1] - self.size_cell // 2)
            iniciy = int(self.points[cell, 0] - self.size_cell // 2)
            rect_cell = juego[inicix: inicix + self.size_cell, iniciy:iniciy + self.size_cell, :]

            num = self.calculate_cell(rect_cell)
            if num is None:
                continue

            self.update_neighbours(cell, num)
            if num == 0:
                free += self.logic[cell]['emptys_neighbors']

    def update_neighbours(self, cell: int, value: int)-> None:
        """
        update the neighbors of a discovered cell

        Args:
            cell (int): number of cell
            value (int): number in cell
        """
        self.cell_unknown.remove(cell)
        self.logic[cell]['val'] = value
        if value != 0:
            self.active_cells.append(cell)

        for neighbour in self.logic[cell]['neighbors']:
            self.logic[neighbour]['emptys'] -= 1
            self.logic[neighbour]['emptys_neighbors'].remove(cell)

    def is_boom(self, cell: int) -> None:
        """
        If a cell is a bomb,
        it updates the information on the neighbors and changes their value to posx.

        Args:
            cell (int): number of cell
        """
        self.booms -= 1
        self.cell_unknown.remove(cell)
        self.logic[cell]['val'] = 'X'

        for neighbour in self.logic[cell]['neighbors']:
            self.logic[neighbour]['emptys'] -= 1
            self.logic[neighbour]['booms'] += 1
            self.logic[neighbour]['emptys_neighbors'].remove(cell)

    def calculate_neighbor(self, cell: int, cant: str='all') -> list:
        """
        This function calculates the neighboring cells of a given cell.

        all <- Return list all neighbours
        rect <- Return non-diagonal neighbors

        Args:
            cell (int): number of cell
            cant (str, optional): (all, rect). Defaults to 'all'.

        Returns:
            list: cells neighbours
        """
        neighbours = []
        not_neighbours = []
        neighbours.append(cell - self.columns - 1)
        neighbours.append(cell - self.columns)
        neighbours.append(cell - self.columns + 1)
        neighbours.append(cell - 1)
        neighbours.append(cell + 1)
        neighbours.append(cell + self.columns - 1)
        neighbours.append(cell + self.columns)
        neighbours.append(cell + self.columns + 1)

        if cell % self.columns == 0:

            not_neighbours.append(cell - self.columns - 1)
            not_neighbours.append(cell - 1)
            not_neighbours.append(cell + self.columns - 1)

        if (cell + 1) % self.columns == 0:
            not_neighbours.append(cell - self.columns + 1)
            not_neighbours.append(cell + 1)
            not_neighbours.append(cell + self.columns + 1)

        if cell - self.columns < 0:
            not_neighbours.append(cell - self.columns - 1)
            not_neighbours.append(cell - self.columns)
            not_neighbours.append(cell - self.columns + 1)

        if cell + self.columns > self.num_cells - 1:
            not_neighbours.append(cell + self.columns - 1)
            not_neighbours.append(cell + self.columns)
            not_neighbours.append(cell + self.columns + 1)

        if cant == 'rect':
            not_neighbours.append(cell - self.columns - 1)
            not_neighbours.append(cell - self.columns + 1)
            not_neighbours.append(cell + self.columns - 1)
            not_neighbours.append(cell + self.columns + 1)

        not_neighbours = list(set(not_neighbours))

        for remove in not_neighbours:

            neighbours.remove(remove)

        return neighbours

    def difference_algorithm(self) -> tuple:
        """
        calculates the unknown cells by traversing the active cells
        and calculating the difference between their value and the
        number of empty neighbors. If it is the same, all the neighbors
        are bombs. If it is 0, all the neighbors are not bombs and if
        it is negative, there is an error in the solution.

        Raises:
            ChildProcessError: in case of inconsistency in the solution

        Returns:
            list: cells free bombs
            list: cells bombs
        """
        free_booms = []
        booms = []
        act_cells = self.active_cells.copy()
        for cell in act_cells:

            dif = self.logic[cell]['val'] - self.logic[cell]['booms']

            if dif == self.logic[cell]['emptys']:
                self.active_cells.remove(cell)
                emptys = self.logic[cell]['emptys_neighbors'].copy()
                for empty in emptys:
                    self.is_boom(empty)
                    booms.append(empty)

            elif dif == 0:
                self.active_cells.remove(cell)
                for empty in self.logic[cell]['emptys_neighbors']:
                    free_booms.append(empty)

            elif dif < 0:
                raise ChildProcessError(
                    f"Error en la solución celda {cell}: valor: {self.logic[cell]['val']}" +
                    f" , bombas: {self.logic[cell]['booms']}"
                )

        free_booms = list(set(free_booms))
        booms = list(set(booms))
        return free_booms, booms

    def neighbor_algorithm(self) -> tuple:
        """
        This algorithm can only be used in case the difference algorithm does
        not discover cells since otherwise it can generate a bug in the solution.
        This algorithm takes the rectangular neighbors of the active cells and calculates
        the difference between the cell value and the bombs by assigning it to a new dictionary.

        Then perform the same procedure for neighboring cells.Based on the resulting dictionary,
        it can be calculated that:

        if one of the cells contains all the neighbors of the other. and each cell needs a bomb.
        The cells that are not part of the intersection of neighbors are free of bombs.

        If you only have a list of 3 neighbors in the bombs, the minimum value of difference is 1
        and the total sum of differences is 3, the cells with the minimum sum are bombs.

        If the number of neighbors is 4, there is only one cell with the minimum value, a next cell
        with the minimum + 1 and the difference is 3, then the cell with the minimum value is not a
        bomb. And the next cell with the minimum + 1 if it is a bomb.

        This algorithm can be improved and made more versatile. In which there is a general rule.

        Raises:
            ChildProcessError: in case of inconsistency in the solution

        Returns:
            list: cells free bombs
            list: cells bombs
        """
        free_booms = []
        booms = []

        for cell in self.active_cells:
            emptys_sum = {}
            dif = self.logic[cell]['val'] - self.logic[cell]['booms']
            num_emptys = self.logic[cell]['emptys']
            for empty in self.logic[cell]['emptys_neighbors']:
                emptys_sum[empty] = dif

            neighbours4 = self.calculate_neighbor(cell, cant='rect')
            for cell2 in neighbours4:
                sumas = emptys_sum.copy()

                if cell2 not in self.active_cells:
                    continue

                if cell2 < cell:
                    continue

                dif2 = self.logic[cell2]['val'] - self.logic[cell2]['booms']

                for empty in self.logic[cell2]['emptys_neighbors']:

                    if empty in sumas:
                        sumas[empty] += dif2
                    else:
                        sumas[empty] = dif2

                minimum = min(sumas.values())
                valores = list(sumas.values())
                claves = list(sumas.keys())
                num_emptys2 = self.logic[cell2]['emptys']

                if ((len(sumas) == num_emptys or len(sumas) == num_emptys2) and
                   num_emptys != num_emptys2 and dif + dif2 == 2):
                    indexs = np.where(np.array(valores) == minimum)[0]
                    for index in indexs:
                        free_booms.append(claves[index])

                elif (len(sumas) == 3 and valores.count(minimum) == 1 and dif + dif2 == 3):

                    index = valores.index(minimum)
                    booms.append(claves[index])

                elif (len(sumas) == 4 and valores.count(minimum) == 1 and
                      valores.count(minimum + 1) == 1 and dif + dif2 == 3):

                    index = valores.index(minimum)
                    free_booms.append(claves[index])

                    index = valores.index(minimum + 1)
                    booms.append(claves[index])

        free_booms = list(set(free_booms))
        booms = list(set(booms))
        for cell in booms:
            if cell not in self.cell_unknown:
                raise ChildProcessError(f'Error calculando la celda: {cell}')

            self.is_boom(cell)

        return free_booms, booms

    def solve(self) -> None:
        """
        Main function that solves the minesweeper game:
        - Looking for the game window.
        - Applying the solution algorithms.
        - Clicking the cells

        Raises:
            RuntimeError: In case the error fin window
            ChildProcessError: In case the window close
        """
        if self.find_window():
            raise RuntimeError(
                'Fallo al encontrar el area del juego. asegurese que en su pantalla principal '+
                'el juego se encuentre abierto')

        if self.find_matrix():
            raise RuntimeError(
                'Fallo al encontrar la cuadricula del juego. '+
                'El juego no debe haber iniciado posy todas las celdas deben estar en blanco')

        cell_init = int(np.random.random() * self.num_cells)
        self.click_cells([cell_init])

        max_rand = 10
        free = [cell_init]
        try:
            while True:
                update_ok = False
                attemp = 0
                while not update_ok and attemp < 10:
                    update_ok = True
                    attemp += 1
                    self.refresh_game(free)
                    for cell in free:
                        if cell in self.cell_unknown:
                            update_ok = False
                            continue

                if attemp == 10 and not update_ok:

                    raise ChildProcessError('No fue posible actualizar los valores del juego')

                free, booms = self.difference_algorithm()

                if free:
                    self.click_cells(free)
                    print(free)

                if booms:
                    self.click_cells(booms, button='right')

                if not self.cell_unknown:

                    print('JUEGO TERMINADO :)')
                    break

                if not free and not booms and self.cell_unknown:

                    free, booms = self.neighbor_algorithm()
                    if free:
                        print('libres advance:')
                        self.click_cells(free)
                        print(free)

                    if booms:
                        print('Bombas Advance')
                        self.click_cells(booms, button='right')
                        print(booms)

                    if not free and not booms:
                        max_rand -= 1
                        if not self.random or max_rand < 1:
                            print('No se encontro solución')
                            break

                        else:
                            rand = int(np.random.random() * len(self.cell_unknown))
                            free = [self.cell_unknown[rand]]
                            self.click_cells(free)
                            print('Aleatorio!')

            self.print_game()

        except ChildProcessError as error:
            print(error)

    def print_game(self) -> None:
        """
        Prints the calculated current game frame
        """
        for cell in range(self.num_cells):
            if self.logic[cell]['val'] == -1:
                print(" ", end=" ")
            else:
                print(self.logic[cell]['val'], end=" ")
            if (cell + 1) % self.columns == 0:
                print(" ")
