from tkinter import *
from gui import GUI

root = Tk()
root.configure(background='black')
my_gui = GUI(root, '/path/to/image/folder/')
root.mainloop()
root.destroy()
