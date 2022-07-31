# Johan Esteban Cuervo Chica.

import cv2
import numpy as np
import pyautogui
import time
import sys


class solver_mw():

    def __init__(self, difficulty='beginner', random=False):

        self.CalculateRowsCol(difficulty)

        self.Logic_Matrix = np.ones((self.rows, self.columns)).astype('int') * (-1)  # -1 sin información
        self.Logic_Matrix_After = np.copy(self.Logic_Matrix)
        self.Cell_unknown = list(range(self.Num_Cells))
        self.Active_cells = []
        self.random = random
        self.imshow = False
        self.one = np.array([0, 0, 255]).astype('int')
        self.two = np.array([0, 123, 0]).astype('int')
        self.three = np.array([255, 0, 0]).astype('int')
        self.four = np.array([0, 0, 123]).astype('int')
        self.five = np.array([123, 0, 0]).astype('int')
        self.six = np.array([0, 123, 123]).astype('int')
        self.empty = np.array([123, 123, 123]).astype('int')

    def InitGame(self, tim, browser='chrome'):

        # Open the browser and charge buscaminas.eu
        # Tim -> time sleep for each action, depends on the internet and computer
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

    def CalculateRowsCol(self, difficulty):

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

            print('Dificultad no Validad')
            sys.exit()

        self.Num_Cells = self.rows * self.columns

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

        if len(squares) > self.Num_Cells:
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

        if len(squares) == self.Num_Cells:
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
            print('Se encontraron:', len(squares), 'Cuadros de:', self.Num_Cells)

        return 1

    def ClickCells(self, indexs, button='left', tim=0.00):

        for index in indexs:
            point = self.points[index, :] + self.ventana[: 2]
            pyautogui.moveTo(int(point[0]), int(point[1]), tim)
            pyautogui.click(button=button)

    def RefreshGame(self):

        juego = np.array(pyautogui.screenshot(region=self.ventana))

        delete = []
        pixels = self.size_cell**2
        for cell in self.Cell_unknown:
            inicix = int(self.points[cell, 1] - self.size_cell // 2)
            iniciy = int(self.points[cell, 0] - self.size_cell // 2)
            rect_cell = juego[inicix: inicix + self.size_cell, iniciy:iniciy + self.size_cell, :]
            rect_list = rect_cell.reshape((-1, 3))  # Num_pixeles * 3 RGB

            for index in range(len(rect_list)):

                if np.array_equal(self.one, rect_list[index, :]):

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 1
                    self.Active_cells.append(cell)
                    delete.append(cell)
                    break

                if np.array_equal(self.two, rect_list[index, :]):

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 2
                    self.Active_cells.append(cell)
                    delete.append(cell)
                    break

                if np.array_equal(self.three, rect_list[index, :]):

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 3
                    self.Active_cells.append(cell)
                    delete.append(cell)
                    break

                if np.array_equal(self.four, rect_list[index, :]):

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 4
                    self.Active_cells.append(cell)
                    delete.append(cell)
                    break

                if np.array_equal(self.five, rect_list[index, :]):

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 5
                    self.Active_cells.append(cell)
                    delete.append(cell)
                    break

                if np.array_equal(self.six, rect_list[index, :]):

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 6
                    self.Active_cells.append(cell)
                    delete.append(cell)
                    break

                if np.array_equal(self.empty, rect_list[index, :]):

                    break

                if index > pixels / 4:

                    self.Logic_Matrix[cell // self.columns, cell % self.columns] = 0
                    delete.append(cell)
                    break

        for dele in delete:
            self.Cell_unknown.remove(dele)

    def CalculateBooms(self):

        free_booms = []
        booms = []
        Remove_act_cells = []

        for Cell in self.Active_cells:

            Neighbours = self.CalculateNeigt(Cell)

            Num_Booms = 0
            Num_emptys = 0
            emptys = []
            for Neighbour in Neighbours:
                val = self.Logic_Matrix[Neighbour // self.columns, Neighbour % self.columns]
                if val == -1:
                    Num_emptys += 1
                    emptys.append(Neighbour)

                if val == -2:
                    Num_Booms += 1

            Dif = int(self.Logic_Matrix[Cell // self.columns, Cell % self.columns]) - Num_Booms

            if Dif == Num_emptys:
                Remove_act_cells.append(Cell)
                for empty in emptys:
                    if not(empty in self.Cell_unknown):
                        print('error! celda:', empty)
                        print(self.Logic_Matrix)
                        sys.exit()

                    self.Cell_unknown.remove(empty)
                    self.Logic_Matrix[empty // self.columns, empty % self.columns] = -2
                    booms.append(empty)

            elif Dif == 0:
                Remove_act_cells.append(Cell)
                for empty in emptys:
                    free_booms.append(empty)

            elif Dif < 0:
                print('Error en la solucion')
                print('diferencia', Dif)
                print('bombas', Num_Booms)
                print('vacios', Num_emptys)
                print('Celda', Cell)
                print('Cantidad de vacios', len(emptys))
                print(self.Logic_Matrix)
                sys.exit()

        for re in Remove_act_cells:
            self.Active_cells.remove(re)

        free_booms = list(set(free_booms))
        booms = list(set(booms))
        return free_booms, booms

    def CalculateNeigt(self, Cell):
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

        if Cell + self.columns > self.Num_Cells - 1:
            Remove.append(Cell + self.columns - 1)
            Remove.append(Cell + self.columns)
            Remove.append(Cell + self.columns + 1)

        Remove = list(set(Remove))

        for R in Remove:

            Neighbours.remove(R)

        return Neighbours

    def advance_methods(self):

        free_booms = []
        booms = []

        for Cell in self.Active_cells:

            Neighbours = self.CalculateNeigt(Cell)

            Num_Booms = 0
            Num_emptys = 0
            emptys = []
            emptys_sum = {}
            for Neighbour in Neighbours:
                val = self.Logic_Matrix[Neighbour // self.columns, Neighbour % self.columns]
                if val == -1:
                    Num_emptys += 1
                    emptys.append(Neighbour)

                if val == -2:
                    Num_Booms += 1

            Val = self.Logic_Matrix[Cell // self.columns, Cell % self.columns]
            Dif = Num_emptys - (Val + Num_Booms)
            for empty in emptys:
                emptys_sum[empty] = Val - Num_Booms

            for Cell2 in Neighbours:
                sumas = emptys_sum.copy()
                if self.Logic_Matrix[Cell2 // self.columns, Cell2 % self.columns] < 1:
                    continue

                if Cell2 < Cell:
                    continue

                Neighbours2 = self.CalculateNeigt(Cell2)
                Num_Booms2 = 0
                Num_emptys2 = 0
                emptys2 = []

                for Neighbour in Neighbours2:
                    val = self.Logic_Matrix[Neighbour // self.columns, Neighbour % self.columns]
                    if val == -1:
                        Num_emptys2 += 1
                        emptys2.append(Neighbour)

                    if val == -2:
                        Num_Booms2 += 1

                Val2 = self.Logic_Matrix[Cell2 // self.columns, Cell2 % self.columns]
                Dif2 = Num_emptys2 - (Val2 + Num_Booms2)

                for empty in emptys2:

                    if empty in emptys:
                        sumas[empty] += Val2 - Num_Booms2

                    else:

                        sumas[empty] = Val2 - Num_Booms2

                minimum = min(sumas.values())
                valores = list(np.array(list(sumas.values())) - minimum)

                if minimum == 1:
                    if valores.count(0) == 1 and np.abs(Dif2 - Dif) == 1 and np.abs(Val - Val2) != 1:
                        index_0 = valores.index(0)
                        free_booms.append(list(sumas.keys())[index_0])

                    if valores.count(1) == 1 and Dif2 == Dif:
                        index_b = valores.index(1)
                        booms.append(list(sumas.keys())[index_b])

                else:

                    if valores.count(0) == 1:
                        index_b = valores.index(0)
                        booms.append(list(sumas.keys())[index_b])

        free_booms = list(set(free_booms))
        booms = list(set(booms))
        booms_quit = []
        for boom in booms:
            if boom in free_booms:
                print('error!')
                booms_quit.append(boom)

        for boom in booms_quit:
            booms.remove(boom)

        for Cell in booms:
            if not (Cell in self.Cell_unknown):
                print('error al calcular: ', Cell)
                sys.exit()

            self.Logic_Matrix[Cell // self.columns, Cell % self.columns] = -2
            self.Cell_unknown.remove(Cell)

        return free_booms, booms

    def solve(self):

        if self.FindWindow():
            print('Fallo al encontrar el area del juego')
            sys.exit()

        if self.FindMatrix():
            print('Fallo al encontrar la cuadricula del juego')
            sys.exit()

        cell_init = int(np.random.random() * self.Num_Cells)
        self.ClickCells([cell_init])

        dif = True
        max_rand = 10
        free = [cell_init]
        while dif:
            Actualice_ok = False
            Attemp = 0
            while not Actualice_ok and Attemp < 10:
                bandera = 1
                Attemp += 1
                self.RefreshGame()
                for point_free in free:
                    if point_free in self.Cell_unknown:
                        bandera = 0
                        continue
                if bandera:
                    Actualice_ok = True

            if Attemp == 10 and not Actualice_ok:

                print('No fue posible actualizar los valores del juego')
                sys.exit()

            free, booms = self.CalculateBooms()

            if free:
                self.ClickCells(free)
                print(free)

            if booms:
                self.ClickCells(booms, button='right')

            if np.array_equal(self.Logic_Matrix_After, self.Logic_Matrix) and not free and not booms:
                free, booms = self.advance_methods()
                if free:
                    print('libres advance:')
                    self.ClickCells(free)
                    print(free)

                if booms:
                    print('Bombas Advance')
                    self.ClickCells(booms, button='right')
                    print(booms)
                if free or booms:
                    pass #print(self.Logic_Matrix_After)
                if not free and not booms:
                    max_rand -= 1
                    if not self.random or max_rand < 1:
                        print('No se encontro solución')
                        print(self.Cell_unknown)
                        dif = False

                    else:
                        rand = int(np.random.random() * len(self.Cell_unknown))
                        free.append(self.Cell_unknown[rand])
                        self.ClickCells(free)
                        print('Aleatorio!')

            if not self.Cell_unknown:

                print('JUEGO TERMINADO :)')
                dif = False

            else:

                self.Logic_Matrix_After = np.copy(self.Logic_Matrix)

        if not self.random and self.rows == 8:

            print('Ultima Matriz')
            print(self.Logic_Matrix)
            print('Celdas desconocidas')
            print(self.Cell_unknown)
            print('Celdas Activas')
            print(self.Active_cells)
