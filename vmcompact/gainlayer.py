import tkinter as tk
from tkinter import ttk
from math import log

from .data import _base_vals


class GainLayer(ttk.LabelFrame):
    """Concrete class representing a single gainlayer"""

    def __init__(self, parent, index, j):
        super().__init__(parent)
        self._parent = parent
        self.index = index
        self.j = j
        self.gain = tk.DoubleVar()
        self.level = tk.DoubleVar()
        self.on = tk.BooleanVar()
        self.s = self._parent._parent.styletable
        if index <= parent.phys_in:
            self.level_offset = index * 2
        else:
            self.level_offset = parent.phys_in * 2 + (index - parent.phys_in) * 8

        self.sync()
        self._make_widgets()

        self.col_row_configure()
        self.watch_pdirty()
        self.watch_levels()

    @property
    def target(self):
        """returns the current interface"""
        _target = self._parent.target
        return _target.strip[self.index].gainlayer[self.j]

    def getter(self, param):
        if param in dir(self.target):
            return getattr(self.target, param)

    def setter(self, param, value):
        if param in dir(self.target):
            setattr(self.target, param, value)

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

    def _on_mousewheel(self, event):
        self.gain.set(
            self.gain.get()
            + (
                _base_vals.mwscroll_step
                if event.delta > 0
                else -_base_vals.mwscroll_step
            )
        )
        if self.gain.get() > 12:
            self.gain.set(12)
        elif self.gain.get() < -60:
            self.gain.set(-60)
        self.setter("gain", self.gain.get())
        self._parent._parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def scale_callback(self, *args):
        """callback function for scale widget"""
        self.setter("gain", self.gain.get())
        self._parent._parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def set_on(self):
        """enables a gainlayer. sets its button colour"""
        setattr(
            self._parent.target.strip[self.index],
            self._parent.buses[self.j],
            self.on.get(),
        )
        if not _base_vals.using_theme:
            self.s.configure(
                f"On.TButton",
                background=f'{"green" if self.on.get() else "white"}',
            )

    def convert_level(self, val):
        if _base_vals.vban_connected:
            return round(-val * 0.01, 1)
        return round(20 * log(val, 10), 1) if val > 0 else -200.0

    def _make_widgets(self):
        """Creates a progressbar, scale, on button and config button for a single channel"""
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
        self.scale.bind("<MouseWheel>", self._on_mousewheel)

        # On button
        self.button_on = ttk.Checkbutton(
            self,
            text="ON",
            command=self.set_on,
            style=f"{'Toggle.TButton' if _base_vals.using_theme else 'On.TButton'}",
            variable=self.on,
        )
        self.button_on.grid(column=0, row=1, columnspan=2)

    def col_row_configure(self):
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.N, tk.S, tk.W, tk.E))
            for child in self.winfo_children()
            if isinstance(child, ttk.Checkbutton)
        ]
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.N, tk.S))
            for child in self.winfo_children()
            if isinstance(child, ttk.Progressbar) or isinstance(child, ttk.Scale)
        ]
        self.columnconfigure(0, minsize=36)
        self.columnconfigure(1, minsize=36)
        self.rowconfigure(1, minsize=70)

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
        self.on.set(
            getattr(
                self._parent.target.strip[self.index],
                self._parent.buses[self.j],
            )
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
                    (
                        0
                        if self._parent._parent.channel_frame.strips[
                            self.index
                        ].mute.get()
                        or not self.on.get()
                        else 100 + (max(vals) - 18) + self.gain.get()
                    )
                )
        self.after(
            _base_vals.ldelay if not _base_vals.in_scale_button_1 else 100,
            self.watch_levels_step,
        )


class SubMixFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs
        self.buses = tuple(f"A{i+1}" for i in range(self.phys_out)) + tuple(
            f"B{i+1}" for i in range(self.virt_out)
        )
        defaults = {
            "width": 80,
            "height": 150,
        }
        self.configuration = defaults | self.configuration
        self.width = self.configuration["width"]
        self.height = self.configuration["height"]

        self.gainlayers = [
            GainLayer(self, index, _base_vals.submixes) for index in range(8)
        ]
        [
            gainlayer.grid(row=0, column=self.gainlayers.index(gainlayer))
            for gainlayer in self.gainlayers
        ]

        self.col_row_configure()

        # destroy any without label text
        for i, gainlayer in enumerate(self.gainlayers):
            gainlayer.grid(row=0, column=i)
            if not gainlayer.cget("text"):
                self.columnconfigure(i, minsize=0)
                gainlayer.grid_remove()

        self.watch_pdirty()

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

    def col_row_configure(self):
        [
            self.columnconfigure(i, minsize=self.width)
            for i, _ in enumerate(self.gainlayers)
        ]
        [self.rowconfigure(0, minsize=130) for i, _ in enumerate(self.gainlayers)]

    def watch_pdirty(self):
        self.after(1, self.watch_pdirty_step)

    def watch_pdirty_step(self):
        if self._parent.pdirty:
            self.watch_labels()
        self.after(_base_vals.pdelay, self.watch_pdirty_step)

    def watch_labels(self):
        for i, gainlayer in enumerate(self.gainlayers):
            if not self.target.strip[gainlayer.index].label:
                self.columnconfigure(i, minsize=0)
                gainlayer.grid_remove()
            else:
                self.columnconfigure(i, minsize=80)
                gainlayer.grid()
