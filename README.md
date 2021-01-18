# annotation-tool
to implement an implementing annotation tool  using PySimpleGUI and OpenCV - GUI tool which allows the creating of a labelled image dataset.

1. Programming

implement an annotation tool in python.
Annotation tool is a GUI tool which allows the creating of a labelled image dataset.

The aim of the specific tool is to specify locations of people's HEAD in images.

The tool will receive, as input, a path to a folder, containing images. It will read the images and will present each image to the user. The user will specify the locations of all the heads in each image. When all the images are annotated (or on a command, specified below), the data (locations of heads for each image) will then be saved to a single file 'results.pkl' (in pickle format) in the specified folder.

Location of a head is a rectangle in the following format: [c, r, w, h]. 
Where: 
c - is a column coordinate of the upper-left corner of the head rectangle, 
r - is a row coordinate of the upper-left corner of the head rectangle, 
w - width of the rectangle, 
h - height of the rectangle.

Annotations of all the images together in a dictionary, with 
keys = image name 
value = list of rectangles of all the heads in the image (i.e. [[c1, r1, w1, h1],[c2, r2, w2, h2],...]), can be empty, if no heads were specified for the image.

The GUI tool support the following interface:
- 'q' - when 'q' is pressed, the program saves all the data and exits
- 's' - save current data
- 'left' - when left arrow key is pressed, go to the previous image
- 'right' - when right arrow key is pressed, go to the next image
- 'd' - when d is pressed - delete last specified rectangle in the current image (if no rectangles specified - do nothing)
- left mouse button press - start drawing rectangle
- mouse move (while left button is pressed) - change rectangle according to mouse coordinates
- left mouse button release - end drawing rectangle, save the rectangle to the database

On each presented image all the existing rectangles shown in blue color (only boundary, no fill). The rectangle in the process of drawing shown in red.

On start the program should check if there exists a previously created 'results.pkl' file. If the file exists - annotation continue from the image where it was stopped previously.

