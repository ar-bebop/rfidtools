import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from rfidtools.labels import utils


class Print(ttk.LabelFrame):
    def __init__(self, parent, text):
        self.parent = parent
        super().__init__(self.parent, text=text, padding=(3, 3, 12, 12))

        self.type = type(self).__name__.lower()
        self.kwargs = dict()

        self.serial = tk.IntVar(value=1)
        self.serial_numbers = tk.IntVar(value=1)

    def draw(self):
        self.grid(row=0, column=0, columnspan=6, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        ttk.Label(self.parent, text='Serial: ').grid(row=1, column=0, sticky='e')
        ttk.Entry(self.parent, textvariable=self.serial, width=3).grid(row=1, column=1, sticky='w')

        ttk.Label(self.parent, text='Serial Numbers: ').grid(row=1, column=2, sticky='e', padx=(20, 0))
        ttk.Entry(self.parent, textvariable=self.serial_numbers, width=3).grid(row=1, column=3, sticky='w')

        ttk.Button(self.parent, text='Print', command=self.print_labels).grid(row=1, column=4, padx=20, pady=5)

    def print_labels(self, payload):
        if utils.send_print(self.type, payload):
            messagebox.showinfo('Success', 'Print job was sent successfully.')

        else:
            messagebox.showerror('Error', 'Error sending sending print job.')


class Porcelain(Print):
    def __init__(self, parent) -> None:
        super().__init__(parent, 'Porcelain: Print Labels')

        self.code = tk.StringVar()
        self.desc = tk.StringVar()
        self.thickness = tk.IntVar()

    def print_labels(self):
        payload = {'Task': 'Print',
                   'Printer': 'SATO CL4NX Plus 203dpi',
                   'code': self.code.get(),
                   'desc': self.desc.get(),
                   'thickness': self.thickness.get(),
                   'serial': self.serial.get(),
                   'serial_numbers': self.serial_numbers.get()}

        super().print_labels(payload)

    def draw(self) -> None:
        super().draw()

        ttk.Label(self, text='Product Code:').grid(row=0, column=0, columnspan=2, sticky='s')
        ttk.Entry(self, textvariable=self.code).grid(row=1, column=0, columnspan=2, sticky='new')

        ttk.Label(self, text='Name & Description:').grid(row=2, column=0, columnspan=2, sticky='s')
        ttk.Entry(self, textvariable=self.desc).grid(row=3, column=0, columnspan=2, sticky='new')

        ttk.Label(self, text='Thickness:').grid(row=4, column=0, columnspan=2, sticky='s')
        ttk.Entry(self, textvariable=self.thickness, width=2).grid(row=5, column=0, columnspan=2, sticky='n')


class Slabs(Print):
    def __init__(self, parent) -> None:
        super().__init__(parent, 'Slabs: Print Labels')

        self.code = tk.StringVar()
        self.desc = tk.StringVar()
        self.dim_x = tk.IntVar()
        self.dim_y = tk.IntVar()
        self.lot = tk.StringVar()

    def print_labels(self):
        payload = {'Task': 'Print',
                   'Printer': 'SATO CL6NX Plus 203dpi',
                   'code': self.code.get(),
                   'desc': self.desc.get(),
                   'dim_x': self.dim_x.get(),
                   'dim_y': self.dim_y.get(),
                   'lot': self.lot.get(),
                   'serial': self.serial.get(),
                   'serial_numbers': self.serial_numbers.get()}

        super().print_labels(payload)

    def draw(self) -> None:
        super().draw()

        ttk.Label(self, text='Product Code:').grid(row=0, column=0, columnspan=2, sticky='s')
        ttk.Entry(self, textvariable=self.code).grid(row=1, column=0, columnspan=2, sticky='new')

        ttk.Label(self, text='Name & Description:').grid(row=2, column=0, columnspan=2, sticky='s')
        ttk.Entry(self, textvariable=self.desc).grid(row=3, column=0, columnspan=2, sticky='new')

        ttk.Label(self, text='Length: ').grid(row=4, column=0, sticky='e')
        ttk.Entry(self, textvariable=self.dim_x, width=4).grid(row=4, column=1, sticky='w')

        ttk.Label(self, text='Height: ').grid(row=5, column=0, sticky='e')
        ttk.Entry(self, textvariable=self.dim_y, width=4).grid(row=5, column=1, sticky='w')

        ttk.Label(self, text='Lot:').grid(row=6, column=0, columnspan=2, sticky='s')
        ttk.Entry(self, textvariable=self.lot).grid(row=7, column=0, columnspan=2, sticky='n')
