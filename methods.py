import cv2
import numpy as np
import pyautogui
import time


def FindWindow(image, imshow=False):

    imagen_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    bordes = cv2.Canny(imagen_gray, 10, 150)
    bordes = cv2.dilate(bordes, None, iterations=2)
    bordes = cv2.erode(bordes, None, iterations=1)
    if imshow:
        cv2.imshow('imagen', bordes)
        cv2.waitKey(0)

    contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if imshow:
        image2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.drawContours(image2, contornos, -1, (0, 0, 255), 2)
        cv2.imshow('imagen', image2)
        cv2.waitKey(0)

    ventana = []
    for contorno in contornos:
        approx = cv2.approxPolyDP(contorno, 10, True)
        if len(approx) == 4:

            h = (approx[1] - approx[0])[0][1]
            w = (approx[2] - approx[0])[0][0]
            # print(str(w) + ', ' + str(h))

            if w != 0:
                relac = round(np.abs(h / w), 2)
            else:
                relac = 0

            if relac == 1.24 or relac == 1.25:

                ventana.append(approx)

    if imshow:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.drawContours(image, ventana, -1, (0, 0, 255), 2)
        cv2.imshow('imagen', image)
        cv2.waitKey(0)

    if len(ventana) == 1:

        ventana = ventana[0]

        y, x = ventana[0][0]
        w = (ventana[1] - ventana[0])[0][1]
        h = (ventana[2] - ventana[0])[0][0]

        if imshow:
            juego = imagen_gray[x: x + w, y: y + h]

            cv2.imshow('juego', juego)
            cv2.waitKey(0)

        return y, x, h, w

    return 1


def FindMatrix(game, imshow=False):

    game_gray = cv2.cvtColor(game, cv2.COLOR_BGR2GRAY)

    _, game_bin = cv2.threshold(game_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if imshow:
        cv2.imshow('Binaria', game_bin)
        cv2.waitKey(0)

    contornos, _ = cv2.findContours(game_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    if imshow:
        game_1 = cv2.cvtColor(game, cv2.COLOR_RGB2BGR)
        contornos2 = list(contornos)
        contornos2.append(np.array([[[0, 0]], [[0, 310]], [[310, 310]], [[310, 0]]]).astype('int32'))
        cv2.drawContours(game_1, contornos2, -1, (0, 0, 255), 2)
        cv2.imshow('contornos', game_1)
        cv2.waitKey(0)

    squares = []
    points = []
    tams = []
    for contorno in contornos:
        x, y, w, h = cv2.boundingRect(contorno)
        relac = round(float(w) / h, 1)
        if relac == 1.0:
            axes = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]).astype('int32')
            init = np.array([x, y]).astype('int')
            points.append(init)
            tams.append(w)
            squares.append(axes)

    moda = np.median(tams)

    if len(squares) > 64:
        squares_mode = []
        points_mode = []
        for iterator in range(len(squares)):

            if tams[iterator] < moda + 2 and tams[iterator] > moda - 2:
                squares_mode.append(squares[iterator])
                points_mode.append(points[iterator])

        squares = squares_mode
        points = points_mode
        if imshow:
            game_2 = cv2.cvtColor(game, cv2.COLOR_RGB2BGR)
            cv2.drawContours(game_2, squares, -1, (0, 0, 255), 2)
            cv2.imshow('contornos', game_2)
            cv2.waitKey(0)

    if len(squares) == 64:
        points = np.array(points)
        points += int(moda // 2)

        args = np.argsort(points[:, 1])

        points = points[list(args), :]

        for i in range(8):
            args = np.argsort(points[i * 8: (i + 1) * 8, 0])
            args += i * 8
            points[i * 8: (i + 1) * 8, :] = points[list(args), :]

        return points, int(moda)

    return 1


def ClickCells(indexs, points, ventana, button='left', tiempo=0.07):

    for index in indexs:
        point = points[index, :] + ventana[: 2]
        pyautogui.moveTo(int(point[0]), int(point[1]), tiempo)
        pyautogui.click(button=button)

    time.sleep(0.5)


def RefreshGame(ventana, points, tam, Logic_matrix, Cell_unlock, Active_cells):

    juego = np.array(pyautogui.screenshot(region=ventana))
    one = np.array([0, 0, 255]).astype('int')
    two = np.array([0, 123, 0]).astype('int')
    three = np.array([255, 0, 0]).astype('int')
    four = np.array([0, 0, 123]).astype('int')
    five = np.array([123, 0, 0]).astype('int')
    empty = np.array([123, 123, 123]).astype('int')
    delete = []
    tam -= 2
    pixels = tam**2
    for cell in Cell_unlock:
        inicix = int(points[cell, 1] - tam // 2)
        iniciy = int(points[cell, 0] - tam // 2)
        rect_cell = juego[inicix: inicix + tam, iniciy:iniciy + tam, :]
        rect_list = rect_cell.reshape((-1, 3))

        for index in range(len(rect_list)):

            if np.array_equal(one, rect_list[index, :]):

                Logic_matrix[cell // 8, cell % 8] = 1
                Active_cells.append(cell)
                delete.append(cell)
                break

            if np.array_equal(two, rect_list[index, :]):

                Logic_matrix[cell // 8, cell % 8] = 2
                Active_cells.append(cell)
                delete.append(cell)
                break

            if np.array_equal(three, rect_list[index, :]):

                Logic_matrix[cell // 8, cell % 8] = 3
                Active_cells.append(cell)
                delete.append(cell)
                break

            if np.array_equal(four, rect_list[index, :]):

                Logic_matrix[cell // 8, cell % 8] = 4
                Active_cells.append(cell)
                delete.append(cell)
                break

            if np.array_equal(five, rect_list[index, :]):

                Logic_matrix[cell // 8, cell % 8] = 5
                Active_cells.append(cell)
                delete.append(cell)
                break

            if np.array_equal(empty, rect_list[index, :]):

                break

            if index > pixels / 4:

                Logic_matrix[cell // 8, cell % 8] = 0
                delete.append(cell)
                break

    for dele in delete:
        Cell_unlock.remove(dele)

    return Logic_matrix, Cell_unlock, Active_cells


def CalculateBooms(Logic_matrix, Cell_unlock, Active_cells):

    free_booms = []
    Remove_act_cells = []
    Remove_Cell_unlock = []

    for Cell in Active_cells:

        Vecinos = CalculateNeigt(Cell)

        Num_Booms = 0
        Num_emptys = 0
        emptys = []
        for vecino in Vecinos:
            val = Logic_matrix[vecino // 8, vecino % 8]
            if val == -1:
                Num_emptys += 1
                emptys.append(vecino)

            if val == -2:
                Num_Booms += 1

        Dif2 = int(Logic_matrix[Cell // 8, Cell % 8]) - Num_Booms

        if Dif2 == Num_emptys:
            Remove_act_cells.append(Cell)
            for empty in emptys:
                Remove_Cell_unlock.append(empty)
                Logic_matrix[empty // 8, empty % 8] = -2

        elif Dif2 == 0:
            Remove_act_cells.append(Cell)
            for empty in emptys:
                free_booms.append(empty)

        elif Dif2 < 0:
            print('Error en la solucion')
            print('diferencia', Dif2)
            print('bombas', Num_Booms)
            print('vacios', Num_emptys)
            print('Celda', Cell)
            print('Cantidad de vacios', len(emptys))
            print(Logic_matrix)
            exit()

    for re in Remove_act_cells:
        Active_cells.remove(re)

    for re in Remove_Cell_unlock:
        Cell_unlock.remove(re)

    return Logic_matrix, Cell_unlock, Active_cells, free_booms


def CalculateNeigt(Cell):
    Vecinos = []
    Remove = []
    Vecinos.append(Cell - 8 - 1)
    Vecinos.append(Cell - 8)
    Vecinos.append(Cell - 8 + 1)
    Vecinos.append(Cell - 1)
    Vecinos.append(Cell + 1)
    Vecinos.append(Cell + 8 - 1)
    Vecinos.append(Cell + 8)
    Vecinos.append(Cell + 8 + 1)

    if Cell % 8 == 0:

        Remove.append(Cell - 8 - 1)
        Remove.append(Cell - 1)
        Remove.append(Cell + 8 - 1)

    if (Cell + 1) % 8 == 0:
        Remove.append(Cell - 8 + 1)
        Remove.append(Cell + 1)
        Remove.append(Cell + 8 + 1)

    if Cell - 8 < 0:
        Remove.append(Cell - 8 - 1)
        Remove.append(Cell - 8)
        Remove.append(Cell - 8 + 1)

    if Cell + 8 > 63:
        Remove.append(Cell + 8 - 1)
        Remove.append(Cell + 8)
        Remove.append(Cell + 8 + 1)

    Remove = list(set(Remove))

    for R in Remove:

        Vecinos.remove(R)

    return Vecinos