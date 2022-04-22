import tkinter as tk
from tkinter import ttk

from .data import _base_vals


class Banner(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self.submix = tk.StringVar()
        self.submix.set(self.target.bus[_base_vals.submixes].label)

        self.label = ttk.Label(
            self,
            text=f"SUBMIX: {self.submix.get().upper()}",
        )
        self.label.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

        self.upd_submix()

    @property
    def target(self):
        """use the correct interface"""
        return self._parent.target

    def upd_submix(self):
        self.after(1, self.upd_submix_step)

    def upd_submix_step(self):
        if not _base_vals.dragging:
            self.submix.set(self.target.bus[_base_vals.submixes].label)
            self.label["text"] = f"SUBMIX: {self.submix.get().upper()}"
        self.after(100, self.upd_submix_step)
