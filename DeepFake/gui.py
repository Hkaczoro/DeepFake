from tkinter import *
import DeepFake

root = Tk()


def prt():
    print(text1.get("1.0", END))

label1 = Label(root, text="Nazwa pierwszego zdjęcia")
label2 = Label(root, text="Nazwa drugiego zdjęcia")

text1 = Text(root, height=1, width=30, font=('Helvetica', 18))
text2 = Text(root, height=1, width=30, font=('Helvetica', 18))

button = Button(root, text="Zamień", command=lambda: prt(),font=18, width=40)

label1.grid(row=0, column=0)
label2.grid(row=0, column=1)
text1.grid(row=1, column=0)
text2.grid(row=1, column=1)
button.grid(row=2, columnspan=2)

root.mainloop()

