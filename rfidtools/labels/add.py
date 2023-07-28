import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from rfidtools.labels import utils


class Add(ttk.LabelFrame):
    def __init__(self, parent, text):
        super().__init__(parent, text=text)

        self.type = type(self).__name__.lower()
        self.logs = utils.listlogs(self.type)

    def _update_logs(self):
        self.logs = utils.listlogs(self.type)
        self.logChoices.set(self.logs)

    def draw(self):
        self.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.logChoices = tk.StringVar(value=self.logs)
        self.logsListBox = tk.Listbox(self, listvariable=self.logChoices, selectmode='single')
        self.logsListBox.grid(row=0, column=0, rowspan=3, sticky='nsew')

        ttk.Label(self, text='Bin:').grid(row=0, column=1, sticky='s')
        self.bin = tk.StringVar()
        self.binEntry = ttk.Entry(self, textvariable=self.bin, state=tk.DISABLED)
        self.binEntry.grid(row=1, column=1)
        self.useBin = tk.BooleanVar(value=False)
        ttk.Checkbutton(self,
                        text='Use bin?',
                        command=lambda: self.binEntry.config(state=tk.NORMAL) if self.useBin.get() else self.binEntry.config(state=tk.DISABLED),
                        variable=self.useBin,
                        onvalue=True,
                        offvalue=False
                        ).grid(row=2, column=1, sticky='n')

        ttk.Button(self,
                   text='Remove Log',
                   command=lambda: self.remove_log()
                   ).grid(row=3, column=0, pady=5)

        ttk.Button(self,
                   text='Add Labels',
                   command=lambda: self.add_labels
                   ).grid(row=3, column=1, pady=5)

    def remove_log(self) -> None:
        log = self.logs[self.logsListBox.curselection()[0]]

        if messagebox.askyesno(message=f'You are about to delete\n{log}\nAre you sure?'):
            if utils.rmlog(log):
                messagebox.showwarning('Deletion', 'The selected log was deleted.')
                self._update_logs()
            else:
                messagebox.showerror('Error', 'Something went wrong, log could not be removed.')

    def add_labels(self, query) -> None:
        log = self.logs[self.logsListBox.curselection()[0]]
        bin = self.bin.get() if self.useBin.get() else None

        data = utils.parse_log(self.type, log, bin)
        if len(data) == 0:
            messagebox.showerror('Error', 'File was empty or no data was read.')
            return

        if utils.query(data, query):
            if utils.archive(log):
                messagebox.showinfo(log, 'Successfully commited logged labels to database and moved log to archives.')

            else:
                messagebox.showerror('Error', 'Archival error.')

        else:
            messagebox.showwarning('Error', 'Database error.')

        self._update_logs()


class Porcelain(Add):
    def __init__(self, parent) -> None:
        super().__init__(parent, 'Porcelain: Add Labels')

    def draw(self) -> None:
        super().draw()

    def add_labels(self) -> None:
        INSERT_QUERY = """\
                INSERT INTO porcelain_stock(ProductTagID, WarehouseCode, Status, ReceivedDateTimeStamp, CreatedBy, Bin, ProductTagName, ProductCode)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)\
                """

        super().add_labels(INSERT_QUERY)


class Slabs(Add):
    def __init__(self, parent) -> None:
        super().__init__(parent, 'Slabs: Add Labels')

    def draw(self) -> None:
        super().draw()

    def add_labels(self) -> None:
        INSERT_QUERY = """\
                INSERT INTO Stock(Barcode, TagID, ProductCode, BlockNumber, SlabNumber, Length, Width, WarehouseCode, LocationCode, StatusID, ReceivedDateTimeStamp)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\
                """

        super().add_labels(INSERT_QUERY)
