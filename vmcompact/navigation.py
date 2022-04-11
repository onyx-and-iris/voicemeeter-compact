import tkinter as tk
from tkinter import ttk

from .channels import ChannelFrame
from .gainlayer import SubMixFrame
from .data import _base_vals


class Navigation(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.s = parent.styletable

        self.submix = tk.BooleanVar()
        self.channel = tk.BooleanVar()
        self.extend = tk.BooleanVar()
        self.info = tk.BooleanVar()

        self.channel_text = tk.StringVar()
        self.channel_text.set(parent.channel_frame.identifier.upper())
        self.extend_text = tk.StringVar()
        self.extend_text.set("EXTEND")
        self.info_text = tk.StringVar()
        self._parent.submix_frame = None

        self._make_widgets()

        self.col_row_configure()

    def _make_widgets(self):
        """Creates the navigation buttons"""
        self.submix_button = ttk.Checkbutton(
            self,
            text="SUBMIX",
            command=self.show_submix,
            style=f"{'Toggle.TButton' if _base_vals.using_theme else f'Submix.TButton'}",
            variable=self.submix,
        )
        self.channel_button = ttk.Checkbutton(
            self,
            textvariable=self.channel_text,
            command=self.switch_channel,
            style=f"{'Toggle.TButton' if _base_vals.using_theme else f'Channel.TButton'}",
            variable=self.channel,
        )
        self.extend_button = ttk.Checkbutton(
            self,
            textvariable=self.extend_text,
            command=self.extend_frame,
            style=f"{'Toggle.TButton' if _base_vals.using_theme else f'Extend.TButton'}",
            variable=self.extend,
        )
        self.info_button = ttk.Checkbutton(
            self,
            textvariable=self.info_text,
            style=f"{'Toggle.TButton' if _base_vals.using_theme else f'Rec.TButton'}",
            variable=self.info,
        )
        self.info_button["state"] = "active"

        """ Position navigation buttons """
        self.submix_button.grid(column=0, row=0)
        self.channel_button.grid(column=0, row=1, rowspan=1)
        self.extend_button.grid(column=0, row=2)
        self.info_button.grid(column=0, row=3)

        if self._parent.kind.name != "Potato":
            self.submix_button["state"] = "disabled"

    def show_submix(self):
        if self.submix.get():
            if _base_vals.extends_horizontal:
                self._parent.submix_frame = SubMixFrame(self._parent)
                self._parent.submix_frame.grid(row=0, column=2)
                if self._parent.bus_frame:
                    self._parent.bus_frame.grid_remove()
            else:
                self._parent.submix_frame = SubMixFrame(self._parent)
                self._parent.submix_frame.grid(row=2, column=0, sticky=(tk.W))
                if self._parent.bus_frame:
                    self._parent.bus_frame.grid_remove()
        else:
            if _base_vals.extends_horizontal:
                self._parent.submix_frame.destroy()
                if self._parent.bus_frame:
                    self._parent.bus_frame.grid()
                else:
                    self._parent.columnconfigure(1, weight=0)
            else:
                self._parent.submix_frame.destroy()
                if self._parent.bus_frame:
                    self._parent.bus_frame.grid()
                else:
                    self._parent.rowconfigure(2, weight=0, minsize=0)

        if not _base_vals.using_theme:
            self.s.configure(
                f"Submix.TButton",
                background=f'{"purple" if self.submix.get() else "white"}',
            )

    def switch_channel(self):
        if self.channel_text.get() == "STRIP":
            self._parent.bus_frame = ChannelFrame.make_buses(self._parent)
            self._parent.bus_frame.grid(row=0, column=0)
            self._parent.channel_frame.destroy()
        else:
            self._parent.channel_frame = ChannelFrame.make_strips(self._parent)
            self._parent.channel_frame.grid(row=0, column=0)
            self._parent.bus_frame.destroy()

        self.extend_button["state"] = (
            "disabled" if self.channel_text.get() == "STRIP" else "normal"
        )
        [frame.destroy() for frame in self._parent.configframes]
        self.channel_text.set("BUS" if self.channel_text.get() == "STRIP" else "STRIP")

    def extend_frame(self):
        if self.extend.get():
            self.channel_button["state"] = "disabled"
            self._parent.bus_frame = ChannelFrame.make_buses(self._parent)
            if _base_vals.extends_horizontal:
                self._parent.bus_frame.grid(row=0, column=2)
            else:
                self._parent.bus_frame.grid(row=2, column=0, sticky=(tk.W))
        else:
            [
                frame.destroy()
                for frame in self._parent.configframes
                if "!busconfig" in str(frame)
            ]
            self._parent.bus_frame.destroy()
            self._parent.bus_frame = None
            self.channel_button["state"] = "normal"

        if self._parent.submix_frame:
            self._parent.submix_frame.destroy()
            self.submix.set(False)
            if not _base_vals.using_theme:
                self.s.configure(
                    f"Submix.TButton",
                    background=f'{"purple" if self.submix.get() else "white"}',
                )

        self.extend_text.set("REDUCE" if self.extend.get() else "EXTEND")

    def col_row_configure(self):
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.N, tk.S, tk.W, tk.E))
            for child in self.winfo_children()
            if isinstance(child, ttk.Checkbutton)
        ]

        self.rowconfigure(1, minsize=self._parent.channel_frame.height - 18)
        self.grid(sticky=(tk.N))
