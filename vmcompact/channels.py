import tkinter as tk
from tkinter import ttk
from functools import partial
from math import log

from .data import _base_vals
from .config import StripConfig, BusConfig


class Channel(ttk.LabelFrame):
    """Base class for a single channel"""

    def __init__(self, parent, index, id):
        super().__init__(parent)
        self._parent = parent
        self.index = index
        self.id = id
        self.s = self._parent._parent.styletable
        self.config_frame = None

        self.gain = tk.DoubleVar()
        self.level = tk.DoubleVar()
        self.mute = tk.BooleanVar()
        self.conf = tk.BooleanVar()

        self.sync()
        self._make_widgets()

        self.col_row_configure()
        self.watch_pdirty()
        self.watch_levels()

    @property
    def identifier(self):
        return self.id

    @property
    def target(self):
        """use the correct interface"""
        return self._parent.target

    def getter(self, param):
        if param in dir(self.target):
            return getattr(self.target, param)

    def setter(self, param, value):
        if param in dir(self.target):
            setattr(self.target, param, value)

    def toggle_mute(self, *args):
        self.target.mute = self.mute.get()
        if not _base_vals.using_theme:
            self.s.configure(
                f"{self.identifier}Mute{self.index}.TButton",
                background=f'{"red" if self.mute.get() else "white"}',
            )

    def reset_gain(self, *args):
        self.setter("gain", 0)
        self.gain.set(0)
        self._parent._parent.nav_frame.info_text.set(0)

    def scale_enter(self, *args):
        self._parent._parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def scale_leave(self, *args):
        self._parent._parent.nav_frame.info_text.set("")

    def scale_press(self, *args):
        _base_vals.in_scale_button_1 = True

    def scale_release(self, *args):
        _base_vals.in_scale_button_1 = False

    def scale_callback(self, *args):
        """callback function for scale widget"""
        self.setter("gain", self.gain.get())
        self._parent._parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def convert_level(self, val):
        if _base_vals.vban_connected:
            return round(-val * 0.01, 1)
        return round(20 * log(val, 10), 1) if val > 0 else -200.0

    def _make_widgets(self):
        """Creates a progressbar, scale, mute button and config button for a single channel"""
        # Progress bar
        self.pb = ttk.Progressbar(
            self,
            maximum=100,
            orient="vertical",
            mode="determinate",
            variable=self.level,
        )
        self.pb.grid(column=0, row=0)

        # Scale
        self.scale = ttk.Scale(
            self,
            from_=12.0,
            to=-60.0,
            orient="vertical",
            variable=self.gain,
            command=self.scale_callback,
            length=self._parent.height,
        )
        self.scale.grid(column=1, row=0)
        self.scale.bind("<Double-Button-1>", self.reset_gain)
        self.scale.bind("<Button-1>", self.scale_press)
        self.scale.bind("<Enter>", self.scale_enter)
        self.scale.bind("<ButtonRelease-1>", self.scale_release)
        self.scale.bind("<Leave>", self.scale_leave)

        # Mute button
        self.button_mute = ttk.Checkbutton(
            self,
            text="MUTE",
            command=partial(self.toggle_mute, "mute"),
            style=f"{'Toggle.TButton' if _base_vals.using_theme else f'{self.identifier}Mute{self.index}.TButton'}",
            variable=self.mute,
        )
        self.button_mute.grid(column=0, row=1, columnspan=2)

        self.button_conf = ttk.Checkbutton(
            self,
            text="CONFIG",
            command=self.open_config,
            style=f"{'Toggle.TButton' if _base_vals.using_theme else f'{self.identifier}Conf{self.index}.TButton'}",
            variable=self.conf,
        )
        self.button_conf.grid(column=0, row=2, columnspan=2)

    def watch_pdirty(self):
        self.after(1, self.watch_pdirty_step)

    def watch_pdirty_step(self):
        """keeps params synced but ensures sliders are responsive"""
        if self._parent._parent.pdirty and not _base_vals.in_scale_button_1:
            self.sync()
        self.after(_base_vals.pdelay, self.watch_pdirty_step)

    def sync(self):
        """sync params with voicemeeter"""
        retval = self.getter("label")
        if len(retval) > 10:
            retval = f"{retval[:8]}.."
        self.configure(text=retval)
        self.gain.set(self.getter("gain"))
        self.mute.set(self.getter("mute"))
        if not _base_vals.using_theme:
            self.s.configure(
                f"{self.identifier}Mute{self.index}.TButton",
                background=f'{"red" if  self.mute.get() else "white"}',
            )
            self.s.configure(
                f"{self.identifier}Conf{self.index}.TButton", background="white"
            )

    def col_row_configure(self):
        self.grid(sticky=(tk.N, tk.S))
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.W, tk.E))
            for child in self.winfo_children()
            if isinstance(child, ttk.Checkbutton)
        ]
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.N, tk.S))
            for child in self.winfo_children()
            if isinstance(child, ttk.Progressbar) or isinstance(child, ttk.Scale)
        ]


class Strip(Channel):
    """Concrete class representing a single"""

    def __init__(self, parent, index, id):
        super().__init__(parent, index, id)
        if index <= parent.phys_in:
            self.level_offset = index * 2
        else:
            self.level_offset = parent.phys_in * 2 + (index - parent.phys_in) * 8

    @property
    def target(self):
        """use the correct interface"""
        _target = super(Strip, self).target
        return getattr(_target, self.identifier)[self.index]

    def open_config(self):
        if self.conf.get():
            self.config_frame = StripConfig(
                self._parent._parent,
                self.index,
                self.identifier,
            )
            self.config_frame.grid(column=0, row=1, columnspan=4)
            self._parent._parent.channel_frame.reset_config_buttons(self)
            if self._parent._parent.bus_frame is not None:
                self._parent._parent.bus_frame.reset_config_buttons(self)
        else:
            self.config_frame.destroy()

        if not _base_vals.using_theme:
            self.s.configure(
                f"{self.identifier}Conf{self.index}.TButton",
                background=f'{"yellow" if self.conf.get() else "white"}',
            )

    def watch_levels(self):
        self.after(1, self.watch_levels_step)

    def watch_levels_step(self):
        if not _base_vals.dragging:
            if (
                self._parent._parent.ldirty
                and any(
                    self._parent._parent.comp_strip[
                        self.level_offset : self.level_offset + 1
                    ]
                )
                and _base_vals.strip_level_array_size
                == len(self._parent._parent.comp_strip)
            ):
                vals = (
                    self.convert_level(
                        self._parent._parent.strip_levels[self.level_offset]
                    ),
                    self.convert_level(
                        self._parent._parent.strip_levels[self.level_offset + 1]
                    ),
                )
                self.level.set(
                    (0 if self.mute.get() else 100 + (max(vals) - 18) + self.gain.get())
                )
        self.after(
            _base_vals.ldelay if not _base_vals.in_scale_button_1 else 100,
            self.watch_levels_step,
        )


class Bus(Channel):
    """Concrete bus class representing a single bus"""

    def __init__(self, parent, index, id):
        super().__init__(parent, index, id)
        self.level_offset = self.index * 8

    @property
    def target(self):
        """use the correct interface"""
        _target = super(Bus, self).target
        return getattr(_target, self.identifier)[self.index]

    def open_config(self):
        if self.conf.get():
            self.config_frame = BusConfig(
                self._parent._parent,
                self.index,
                self.identifier,
            )
            if _base_vals.extends_horizontal:
                self.config_frame.grid(column=0, row=1, columnspan=3)
            else:
                self.config_frame.grid(column=0, row=3, columnspan=3)
            self._parent._parent.channel_frame.reset_config_buttons(self)
            self._parent._parent.bus_frame.reset_config_buttons(self)
        else:
            self.config_frame.destroy()

        if not _base_vals.using_theme:
            self.s.configure(
                f"{self.identifier}Conf{self.index}.TButton",
                background=f'{"yellow" if self.conf.get() else "white"}',
            )

    def watch_levels(self):
        self.after(1, self.watch_levels_step)

    def watch_levels_step(self):
        if not _base_vals.dragging:
            if (
                self._parent._parent.ldirty
                and any(
                    self._parent._parent.comp_bus[
                        self.level_offset : self.level_offset + 1
                    ]
                )
                and _base_vals.bus_level_array_size
                == len(self._parent._parent.comp_bus)
            ):
                vals = (
                    self.convert_level(
                        self._parent._parent.bus_levels[self.level_offset]
                    ),
                    self.convert_level(
                        self._parent._parent.bus_levels[self.level_offset + 1]
                    ),
                )
                self.level.set((0 if self.mute.get() else 100 + (max(vals) - 18)))
        self.after(
            _base_vals.ldelay if not _base_vals.in_scale_button_1 else 100,
            self.watch_levels_step,
        )


class ChannelFrame(ttk.Frame):
    @classmethod
    def make_strips(cls, parent):
        return cls(parent, is_strip=True)

    @classmethod
    def make_buses(cls, parent):
        return cls(parent, is_strip=False)

    def __init__(self, parent, is_strip: bool = True):
        super().__init__(parent)
        self._parent = parent
        self._is_strip = is_strip
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs
        _base_vals.strip_level_array_size = 2 * self.phys_in + 8 * self.virt_in
        _base_vals.bus_level_array_size = 8 * (self.phys_out + self.virt_out)

        defaults = {
            "width": 80,
            "height": 150,
        }
        self.configuration = defaults | self.configuration
        self.width = self.configuration["width"]
        self.height = self.configuration["height"]

        self.watch_pdirty()

        # create labelframes
        if is_strip:
            self.strips = [
                Strip(self, i, self.identifier)
                for i in range(self.phys_in + self.virt_in)
            ]
        else:
            self.buses = [
                Bus(self, i, self.identifier)
                for i in range(self.phys_out + self.virt_out)
            ]

        # position label frames. destroy any without label text
        self.labelframes = self.strips if is_strip else self.buses

        self.col_row_configure()

        for i, labelframe in enumerate(self.labelframes):
            labelframe.grid(row=0, column=i)
            if not labelframe.cget("text"):
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()

    @property
    def target(self):
        """returns the current interface"""
        return self._parent.target

    @property
    def configuration(self):
        return self._parent.configuration["channel"]

    @configuration.setter
    def configuration(self, val):
        self._parent.configuration["channel"] = val

    @property
    def identifier(self):
        return "strip" if self._is_strip else "bus"

    def reset_config_buttons(self, current):
        if not _base_vals.using_theme:
            [
                labelframe.s.configure(
                    f"{labelframe.identifier}Conf{labelframe.index}.TButton",
                    background="white",
                )
                for labelframe in self.labelframes
                if labelframe is not None
            ]
        [
            labelframe.conf.set(False)
            for labelframe in self.labelframes
            if labelframe is not None and labelframe != current
        ]
        [
            labelframe.config_frame.destroy()
            for labelframe in self.labelframes
            if labelframe is not None
            and labelframe.config_frame
            and labelframe != current
        ]

    def col_row_configure(self):
        [
            self.columnconfigure(i, minsize=self.width)
            for i, _ in enumerate(self.labelframes)
        ]
        [self.rowconfigure(0, minsize=130) for i, _ in enumerate(self.labelframes)]

    def watch_pdirty(self):
        self.after(1, self.watch_pdirty_step)

    def watch_pdirty_step(self):
        if self._parent.pdirty:
            self.watch_labels()
        self.after(_base_vals.pdelay, self.watch_pdirty_step)

    def watch_labels(self):
        for i, labelframe in enumerate(self.labelframes):
            if not labelframe.getter("label"):
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()
            else:
                self.columnconfigure(i, minsize=self.width)
                labelframe.grid()
