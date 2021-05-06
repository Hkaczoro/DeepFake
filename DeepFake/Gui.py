import numpy as np
import cv2
import dlib
from tkinter import *
from tkinter import filedialog

from DeepFake import Deepfake

df = Deepfake()

root = Tk()

lista = ['rock.jpg', 'atkin.jpg']

def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Wybierz zdjęcie",
                                          filetypes = (("Text files",
                                                        "*.jpg*"),
                                                       ("all files",
                                                        "*.*")))
    result = filename
    if len(result) > 1:
        lista.append(filename)

def popUp():
    windowPop = Toplevel(root)
    Label(windowPop, text=str(lista[-1]) ).pack(side=TOP)
    Button(windowPop, text="OK", command=lambda:windowPop.destroy()).pack(side=BOTTOM)


def clearUp():
    lista.clear()
    text1.delete("1.0", END)


def swapWindow():
    window1 = Toplevel(root)
    text1 = Text(window1, height=1, width=30, font=('Helvetica', 18))
    browseButton = Button(window1, text = "Wybierz zdjęcie", command=lambda:browseFiles(), font=18, width=40)
    swapButton = Button(window1, text="Zamień twarz w czasie rzeczywistym", command=lambda:[df.swap(lista[-1]), window1.destroy()],font=18, width=40)
    browseButton.pack(side= TOP)
    swapButton.pack(side= BOTTOM)

def twoFaceWindow():
    window2 = Toplevel(root)
    browseButton = Button(window2, text = "Wybierz zdjęcie", command=lambda:browseFiles(), font=18, width=40)
    browseButton.pack(side= TOP)
    twoFaceButton = Button(window2, text="Zamień twarze ze dwóch zdjęć", command=lambda:df.change_face(lista[-1], lista[-2]),font=18, width=40)
    twoFaceButton.pack(side=BOTTOM)



root.title("Projekt Deepfake")

swapButtonMenu = Button(root, text="Zamień twarz w czasie rzeczywistym", command=swapWindow, font=18, width=40)
twoFaceButtonMenu = Button(root, text="Zamień dwie twarze ze zdjęć", command=twoFaceWindow, font=18, width=40)
pointButtonMenu = Button(root, text="Pokaż punkty charakterystyczne twarzy", command=lambda:df.points(),font=18, width=40)


swapButtonMenu.grid(row=0, columnspan=2)
twoFaceButtonMenu.grid(row=1, columnspan=2)
pointButtonMenu.grid(row=2, columnspan=2)

root.mainloop()