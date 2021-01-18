import numpy as np
import pandas as pd
import PySimpleGUI as sg
import os.path
import cv2
import pickle
import sys
import ntpath


def open_pkl_file(file_path, file_name):
    path = os.path.join(file_path, file_name)
    # Parent Directory path
    parent_dir = file_path

    object_file = pickle.load(open(path, 'rb'))
    list_img = []
    list_file_names = []
    for file, points in object_file.items():
        # Reading an image in default mode
        new_image = cv2.imread(file)
        for i in range(len(points)):
            # Start coordinate,represents the top left corner of rectangle
            start_point = (points[i][0], points[i][1])
            # Ending coordinate, represents the bottom right corner of rectangle
            end_point = (points[i][2], points[i][3])
            # Blue color in BGR
            color = (255, 0, 0)
            # Line thickness of 2 px
            thickness = 2
            # Using cv2.rectangle() method ,Draw a rectangle with blue line borders of thickness of 2 px
            new_image = cv2.rectangle(new_image, start_point, end_point, color, thickness)
        list_img.append(new_image)
        list_file_names.append(ntpath.basename(file).split('.')[0])

    for name, img in zip(list_file_names, list_img):
        new_path = os.path.join(parent_dir, '{}_new.png'.format(name))
        cv2.imwrite(new_path, img)
    return parent_dir


def draw_rectangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, img, dict, delete_image, sceneCopy, list_points
    # delete_image = img
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            pass
            # cv2.rectangle(img, pt1=(ix, iy), pt2=(x, y), color=(0, 255, 255), thickness=1)
            # rect = (min(ix, x), min(iy, y), abs(ix - x), abs(iy - y))

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        delete_image = img.copy()

        cv2.rectangle(img, pt1=(ix, iy), pt2=(x, y), color=(255, 0, 0), thickness=1)
        rect_over = True

        sceneCopy = img.copy()
        cv2.rectangle(sceneCopy, (ix, iy), (x, y), (0, 0, 255), 1)

        rect = (ix, iy, x, y)

        list_points.append(rect)
        cv2.imshow('result', sceneCopy)

    # # delete last rectangle
    # elif event == cv2.EVENT_LBUTTONDBLCLK:
    #     sceneCopy = delete_image.copy()
    #     # img = sceneCopy
    #     cv2.imshow('result', sceneCopy)

    return list_points, img, sceneCopy

def draw(file):
    global img, delete_image,sceneCopy, list_points
    img = cv2.imread(file)
    global dict
    cv2.namedWindow(winname="image for drawing")
    cv2.setMouseCallback("image for drawing", draw_rectangle_with_drag)

    while True:
        cv2.imshow("image for drawing", img)
        k = cv2.waitKey(0);
        if k == 27:
            dict[filename] = list_points
            with open(r'{}\filename.pickle'.format(values["-FOLDER-"]), 'wb') as handle:
                pickle.dump(dict, handle)
            break

        # if the 'd' key is pressed, reset the cropping region
        elif k == ord("d"):
            sceneCopy = delete_image

        elif k == ord("s"):
            dict[filename] = list_points
            with open(r'{}\filename.pickle'.format(values["-FOLDER-"]), 'wb') as handle:
                pickle.dump(dict, handle)

        # if the 'q' key is pressed, exit all program
        elif k == ord("q"):
            dict[filename] = list_points
            list_points = []
            with open(r'{}\filename.pickle'.format(values["-FOLDER-"]), 'wb') as handle:
                pickle.dump(dict, handle)
            # cv2.imwrite('a.jpg', sceneCopy)
            sys.exit()
    cv2.destroyAllWindows()


# variables
ix = -1
iy = -1
drawing = False
rect = (0, 0, 1, 1)
rectangle = False
rect_over = False
list_points = []
dict = {}
# First the window layout in 2 columns

file_list_column = [
    [sg.Text("Image Folder"), sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse(), ],
    [sg.Button('left'), sg.Button('right'), sg.Button('Quit')],
    [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-", no_scrollbar=False,
                bind_return_key=True, select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)]
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
    [sg.Button('draw rectangle', key="-DRAW-")],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Image Viewer", layout, return_keyboard_events=True)

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Quit" or event == sg.WIN_CLOSED:
        try:
            with open(r'{}\filename.pickle'.format(values["-FOLDER-"]), 'wb') as handle:
                pickle.dump(dict, handle)
            break
        except:
            break

    # Folder name was filled in, make a list of files in the folder
    elif event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [f for f in file_list if os.path.isfile(os.path.join(folder, f))and f.lower().endswith((".png", ".gif",'.pickle'))]
        # window["-FILE LIST-"].update(fnames)
        for f in file_list:
            if f.endswith('.pickle'):
                new_folder = open_pkl_file(values["-FOLDER-"], f)
                try:
                    # Get list of files in folder
                    file_list = os.listdir(new_folder)
                except:
                    file_list = []
                new_files = [f for f in file_list if
                          os.path.isfile(os.path.join(new_folder, f)) and f.lower().endswith(
                              (".png", ".gif", '.pickle', '.jpg'))]
                # need to return new path for folder
                window["-FILE LIST-"].update(new_files)
                window["-FOLDER-"].update(new_folder)
                break
            else:
                window["-FILE LIST-"].update(fnames)

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            file_list
            filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])

            window["-TOUT-"].update(values["-FILE LIST-"][0])
            window["-IMAGE-"].update(filename=filename)
        except:
            pass

    elif event == "-DRAW-":  # A file was chosen from the listbox
        try:
            window["-IMAGE-"].update(data=draw(filename))
            dict[filename] = list_points
            list_points = []
        except:
            pass

    elif event == "left":
        try:
            ind = file_list.index(values["-FILE LIST-"][0])
            filename = os.path.join(values["-FOLDER-"], file_list[ind + 1])
            values["-FILE LIST-"][0] = file_list[ind + 1]
            window["-TOUT-"].update(file_list[ind + 1])
            window["-IMAGE-"].update(filename=filename)

        except:
            pass

    elif event == "right":
        try:
            ind = file_list.index(values["-FILE LIST-"][0])
            filename = os.path.join(values["-FOLDER-"], file_list[ind - 1])
            values["-FILE LIST-"][0] = file_list[ind - 1]
            window["-TOUT-"].update(file_list[ind - 1])
            window["-IMAGE-"].update(filename=filename)
        except:
            pass

window.close()
