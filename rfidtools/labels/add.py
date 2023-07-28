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

    def _get_selected_log(self) -> str or None:
        try:
            log = self.logs[self.logsListBox.curselection()[0]]

        except IndexError:
            messagebox.showerror('Error', 'No log is selected.')
            return None

        return log

    def draw(self):
        self.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.logChoices = tk.StringVar(value=self.logs)
        self.logsListBox = tk.Listbox(self, listvariable=self.logChoices, selectmode='single')
        self.logsListBox.grid(row=0, column=0, rowspan=4, sticky='nsew')

        ttk.Button(self, text='View Log', command=self.view_log).grid(row=0, column=1)

        ttk.Label(self, text='Bin:').grid(row=1, column=1, sticky='s')
        self.bin = tk.StringVar()
        self.binEntry = ttk.Entry(self, textvariable=self.bin, state=tk.DISABLED)
        self.binEntry.grid(row=2, column=1)
        self.useBin = tk.BooleanVar(value=False)
        ttk.Checkbutton(self,
                        text='Use bin?',
                        command=lambda: self.binEntry.config(state=tk.NORMAL) if self.useBin.get() else self.binEntry.config(state=tk.DISABLED),
                        variable=self.useBin,
                        onvalue=True,
                        offvalue=False
                        ).grid(row=3, column=1, sticky='n')

        ttk.Button(self, text='Remove Log', command=self.remove_log).grid(row=4, column=0, pady=5)

        ttk.Button(self, text='Add Labels', command=self.add_labels).grid(row=4, column=1, pady=5)

    def view_log(self) -> None:
        log = self._get_selected_log()
        if log is None:
            return

        view = tk.Toplevel()
        view.title('Viewing: ' + log)
        if view.tk.call('tk', 'windowingsystem') == 'x11':
            view.attributes('-type', 'utility')

        data = utils.read_log(log)

        ttk.Button(view, text='Close', command=view.destroy).grid(row=len(data), column=len(data[0]) // 2 - 1, columnspan=2, stick='ew')

        for i, colname in enumerate(data[0]):
            ttk.Label(view, text=colname).grid(row=0, column=i, padx=50)
        data = data[1:]

        for i, row in enumerate(data):
            for j, col in enumerate(row):
                ttk.Label(view, text=col).grid(row=i + 1, column=j)

    def remove_log(self) -> None:
        log = self._get_selected_log()
        if log is None:
            return

        if messagebox.askyesno(message=f'You are about to delete\n{log}\nAre you sure?'):
            if utils.rmlog(log):
                messagebox.showwarning('Deletion', 'The selected log was deleted.')
                self._update_logs()
            else:
                messagebox.showerror('Error', 'Something went wrong, log could not be removed.')

    def add_labels(self, query) -> None:
        log = self._get_selected_log()
        if log is None:
            return

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
            messagebox.showerror('Error', 'Database error.\nIt\'s possible one of the labels is already in the database.\nOr there is a connection issue.')

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
