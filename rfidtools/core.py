import tkinter as tk
from tkinter import ttk

from rfidtools.labels import add
from rfidtools.labels import print


class Mainframe(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(5))

        self.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(0, weight=1, minsize=0)

    def main_menu(self):
        self.clear()

        add_frame = ttk.LabelFrame(self, text='Add')
        add_frame.grid(row=0, column=0, pady=80)
        ttk.Button(add_frame, text='Add Porcelain Labels', command=self.add_porcelain).grid(row=0, column=0)
        ttk.Button(add_frame, text='Add Slab Labels', command=self.add_slabs).grid(row=1, column=0)

        print_frame = ttk.LabelFrame(self, text='Print')
        print_frame.grid(row=1, column=0, pady=80)
        ttk.Button(print_frame, text='Print Porcelain Labels', command=self.print_porcelain).grid(row=2, column=0)
        ttk.Button(print_frame, text='Print Slab Labels', command=self.print_slabs).grid(row=3, column=0)

    def print_porcelain(self):
        self.clear()

        print.Porcelain(self).draw()

    def print_slabs(self):
        self.clear()

        print.Slabs(self).draw()

    def add_porcelain(self):
        self.clear()

        add.Porcelain(self).draw()

    def add_slabs(self):
        self.clear()

        add.Slabs(self).draw()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


class Window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('RFID Tools')

        height = 480
        width = 480
        x = int((self.winfo_screenwidth() / 2) - (width / 2))
        y = int((self.winfo_screenheight() / 2) - (height / 2))
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        if self.tk.call('tk', 'windowingsystem') == 'x11':
            self.attributes('-type', 'utility')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.mainframe = Mainframe(self)
        self.mainframe.main_menu()

        self._menu_bar()

    def _menu_bar(self):
        self.menubar = tk.Menu(self)

        self.menubar.add_command(label='Menu', command=self.mainframe.main_menu)

        addmenu = tk.Menu(self.menubar, tearoff=False)
        addmenu.add_command(label='Porcelain', command=self.mainframe.add_porcelain)
        addmenu.add_command(label='Slabs', command=self.mainframe.add_slabs)
        self.menubar.add_cascade(menu=addmenu, label='Add')

        printmenu = tk.Menu(self.menubar, tearoff=False)
        printmenu.add_command(label='Porcelain', command=self.mainframe.print_porcelain)
        printmenu.add_command(label='Slabs', command=self.mainframe.print_slabs)
        self.menubar.add_cascade(menu=printmenu, label='Print')

        self['menu'] = self.menubar


def gui_loop():
    win = Window()

    win.mainloop()
