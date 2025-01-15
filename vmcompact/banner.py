import logging
import tkinter as tk
from tkinter import ttk

from .data import _base_values, _configuration

logger = logging.getLogger(__name__)


class Banner(ttk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.subject.add(self)
        self.logger = logger.getChild(self.__class__.__name__)
        self.submix = tk.StringVar(value=self.target.bus[_configuration.submixes].label)

        self.label = ttk.Label(
            self,
            text=f'SUBMIX: {self.submix.get().upper()}',
        )
        self.label.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

    @property
    def target(self):
        """returns the current interface"""

        return self.parent.target

    def on_update(self, subject):
        if subject == 'submix':
            if not _base_values.dragging:
                self.logger.debug('checking submix for banner')
                self.submix.set(self.target.bus[_configuration.submixes].label)
                self.label['text'] = f'SUBMIX: {self.submix.get().upper()}'
