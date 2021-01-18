import numpy as np
import pandas as pd
import PySimpleGUI as sg
import os.path
import cv2
import pickle
import sys
import ntpath


class ImageSelectWindow(object):

    def __init__(self):
        self.ix = -1
        self.iy = -1
        self.drawing = False
        self.rect = (0, 0, 1, 1)
        self.rectangle = False
        self.rect_over = False
        self.list_points = []
        self.dict = {}
        self.img = None
        self.delete_image = None
        self.filename = None
        self.values = {}

    def open_pkl_file(self, file_path, file_name):
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

    def draw_rectangle_with_drag(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix = x
            self.iy = y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing is True:
                pass

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.delete_image = self.img.copy()

            cv2.rectangle(self.img, pt1=(self.ix, self.iy), pt2=(x, y), color=(255, 0, 0), thickness=1)
            self.rect_over = True

            self.sceneCopy = self.img.copy()
            cv2.rectangle(self.sceneCopy, (self.ix, self.iy), (x, y), (0, 0, 255), 1)
            c, r, w, h = self.ix, self.iy, x, y
            rect = [c, r, w, h]

            self.list_points.append(rect)
            cv2.imshow('result', self.sceneCopy)

        # # delete last rectangle
        # elif event == cv2.EVENT_LBUTTONDBLCLK:
        #     sceneCopy = delete_image.copy()
        #     # img = sceneCopy
        #     cv2.imshow('result', sceneCopy)


    def draw(self, file):
        self.img = cv2.imread(file)
        cv2.namedWindow(winname="image for drawing")
        cv2.setMouseCallback("image for drawing", self.draw_rectangle_with_drag)

        while True:
            cv2.imshow("image for drawing", self.img)
            k = cv2.waitKey(0);
            if k == 27:
                self.dict[file] = self.list_points
                with open(r'{}\filename.pickle'.format(self.values["-FOLDER-"]), 'wb') as handle:
                    pickle.dump(self.dict, handle)
                break

            # if the 'd' key is pressed, reset the cropping region
            elif k == ord("d"):
                self.sceneCopy = self.delete_image

            elif k == ord("s"):
                self.dict[file] = self.list_points
                with open(r'{}\filename.pickle'.format(self.values["-FOLDER-"]), 'wb') as handle:
                    pickle.dump(self.dict, handle)

            # if the 'q' key is pressed, exit all program
            elif k == ord("q"):
                self.dict[file] = self.list_points
                self.list_points = []
                with open(r'{}\filename.pickle'.format(self.values["-FOLDER-"]), 'wb') as handle:
                    pickle.dump(self.dict, handle)
                cv2.destroyAllWindows()
                break
        cv2.destroyAllWindows()

    def run_window(self):
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
        layout = [[sg.Column(file_list_column), sg.VSeperator(), sg.Column(image_viewer_column), ]]
        window = sg.Window("Image Viewer", layout, return_keyboard_events=True)

        # Run the Event Loop
        while True:
            event, self.values = window.read()
            if event == "Quit" or event == sg.WIN_CLOSED:
                try:
                    with open(r'{}\filename.pickle'.format(self.values["-FOLDER-"]), 'wb') as handle:
                        pickle.dump(self.dict, handle)
                    break
                except:
                    break

            # Folder name was filled in, make a list of files in the folder
            elif event == "-FOLDER-":
                folder = self.values["-FOLDER-"]
                try:
                    # Get list of files in folder
                    file_list = os.listdir(folder)
                except:
                    file_list = []

                fnames = [f for f in file_list if os.path.isfile(os.path.join(folder, f))and f.lower().endswith(
                    (".png", ".gif", '.pickle'))]
                for f in file_list:
                    if f.endswith('.pickle'):
                        new_folder = self.open_pkl_file(self.values["-FOLDER-"], f)
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
                    filename_and_path = os.path.join(self.values["-FOLDER-"], self.values["-FILE LIST-"][0])
                    window["-TOUT-"].update(self.values["-FILE LIST-"][0])
                    window["-IMAGE-"].update(filename=filename_and_path)
                except:
                    pass

            elif event == "-DRAW-":  # A file was chosen from the listbox
                try:
                    window["-IMAGE-"].update(data=self.draw(filename_and_path))
                    self.dict[self.filename] = self.list_points
                    list_points = []
                except:
                    pass

            elif event == "left":
                try:
                    ind = file_list.index(self.values["-FILE LIST-"][0])
                    filename_and_path = os.path.join(self.values["-FOLDER-"], file_list[ind + 1])
                    self.values["-FILE LIST-"][0] = file_list[ind + 1]
                    window["-TOUT-"].update(file_list[ind + 1])
                    window["-IMAGE-"].update(filename=filename_and_path)

                except:
                    pass

            elif event == "right":
                try:
                    ind = file_list.index(self.values["-FILE LIST-"][0])
                    filename_and_path = os.path.join(self.values["-FOLDER-"], file_list[ind - 1])
                    self.values["-FILE LIST-"][0] = file_list[ind - 1]
                    window["-TOUT-"].update(file_list[ind - 1])
                    window["-IMAGE-"].update(filename=filename_and_path)
                except:
                    pass

        window.close()


if __name__ == '__main__':

    obj1 = ImageSelectWindow()
    obj1.run_window()
