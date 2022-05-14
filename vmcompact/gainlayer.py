import tkinter as tk
from tkinter import ttk
from math import log

from . import builders
from .data import _base_values, _configuration


class GainLayer(ttk.LabelFrame):
    """Concrete class representing a single gainlayer"""

    def __init__(self, parent, index, j):
        super().__init__(parent)
        self.parent = parent
        self.index = index
        self.j = j
        self.styletable = self.parent.parent.styletable
        if index <= parent.phys_in:
            self.level_offset = index * 2
        else:
            self.level_offset = parent.phys_in * 2 + (index - parent.phys_in) * 8

        self.builder = builders.ChannelLabelFrameBuilder(self, index, id="gainlayer")
        self.builder.setup()
        self.builder.add_progressbar()
        self.builder.add_scale()
        self.builder.add_on_button()
        self.sync()
        self.grid_configure()

    @property
    def target(self):
        """returns the strip[i].gainlayer class in the current interface"""

        _target = self.parent.target
        return _target.strip[self.index].gainlayer[self.j]

    @property
    def identifier(self):
        return "gainlayer"

    def getter(self, param):
        if param in dir(self.target):
            return getattr(self.target, param)

    def setter(self, param, value):
        if param in dir(self.target):
            setattr(self.target, param, value)

    def reset_gain(self, *args):
        self.setter("gain", 0)
        self.gain.set(0)
        self.parent.parent.nav_frame.info_text.set(0)

    def scale_callback(self, *args):
        """callback function for scale widget"""

        self.setter("gain", self.gain.get())
        self.parent.parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def scale_press(self, *args):
        _base_values.in_scale_button_1 = True

    def scale_release(self, *args):
        _base_values.in_scale_button_1 = False

    def scale_enter(self, *args):
        self.parent.parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def scale_leave(self, *args):
        self.parent.parent.nav_frame.info_text.set("")

    def _on_mousewheel(self, event):
        self.gain.set(
            self.gain.get()
            + (
                _base_values.mwscroll_step
                if event.delta > 0
                else -_base_values.mwscroll_step
            )
        )
        if self.gain.get() > 12:
            self.gain.set(12)
        elif self.gain.get() < -60:
            self.gain.set(-60)
        self.setter("gain", self.gain.get())
        self.parent.parent.nav_frame.info_text.set(round(self.gain.get(), 1))

    def set_on(self):
        """enables a gainlayer. sets its button colour"""

        setattr(
            self.parent.target.strip[self.index],
            self.parent.buses[self.j],
            self.on.get(),
        )
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{self.identifier}On{self.index}.TButton",
                background=f'{"green" if self.on.get() else "white"}',
            )

    def sync(self):
        self.after(_base_values.pdelay, self.sync_params)
        self.after(100, self.sync_labels)

    def sync_params(self):
        self.gain.set(self.getter("gain"))
        self.on.set(
            getattr(
                self.parent.target.strip[self.index],
                self.parent.buses[self.j],
            )
        )
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{self.identifier}On{self.index}.TButton",
                background=f'{"green" if self.on.get() else "white"}',
            )

    def sync_labels(self):
        """sync params with voicemeeter"""
        retval = self.parent.target.strip[self.index].label
        if len(retval) > 10:
            retval = f"{retval[:8]}.."
        if not retval:
            self.parent.columnconfigure(self.index, minsize=0)
            self.parent.parent.subject_ldirty.remove(self)
            self.grid_remove()
        else:
            self.parent.parent.subject_ldirty.add(self)
            self.grid()
        self.configure(text=retval)

    def convert_level(self, val):
        if _base_values.vban_connected:
            return round(-val * 0.01, 1)
        return round(20 * log(val, 10), 1) if val > 0 else -200.0

    def upd_levels(self):
        """
        Updates level values.

        Checks offset against expected level array size to avoid a race condition
        """
        if self.level_offset + 1 < len(self.parent.parent.strip_levels):
            if any(
                self.parent.parent.strip_comp[self.level_offset : self.level_offset + 1]
            ):
                val = self.convert_level(
                    max(
                        self.parent.parent.strip_levels[
                            self.level_offset : self.level_offset + 1
                        ]
                    )
                )
                self.level.set(
                    (
                        0
                        if self.parent.target.strip[self.index].mute
                        or not self.on.get()
                        else 100 + val - 18 + self.gain.get()
                    )
                )

    def on_update(self):
        """update levels"""

        self.after(_base_values.ldelay, self.upd_levels)

    def grid_configure(self):
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
        # pb and scale
        self.columnconfigure(0, minsize=36)
        self.columnconfigure(1, minsize=36)
        # on button
        if _configuration.themes_enabled:
            self.rowconfigure(1, minsize=70)
        else:
            self.rowconfigure(1, minsize=55)


class SubMixFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs
        self.buses = tuple(f"A{i+1}" for i in range(self.phys_out)) + tuple(
            f"B{i+1}" for i in range(self.virt_out)
        )

        self.gainlayers = [
            GainLayer(self, index, _base_values.submixes) for index in range(8)
        ]
        for i, labelframe in enumerate(self.labelframes):
            labelframe.grid(row=0, column=i)
            if not self.target.strip[i].label:
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()

        if _configuration.extends_horizontal:
            self.grid(row=0, column=2)
            if parent.bus_frame:
                parent.bus_frame.grid_remove()
        else:
            if parent.bus_frame:
                self.grid(
                    row=parent.bus_frame.grid_info()["row"], column=0, sticky=(tk.W)
                )
                parent.bus_frame.grid_remove()
            else:
                self.grid(row=2, column=0, sticky=(tk.W))

        # registers submixframe as pdirty observer
        self.parent.subject_pdirty.add(self)

        self.grid_configure()
        """
        Grids each labelframe, grid_removes any without a label
        """
        for i, labelframe in enumerate(self.labelframes):
            labelframe.grid(row=0, column=i)
            if not self.target.strip[i].label:
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()

    @property
    def target(self):
        """returns the current interface"""

        return self.parent.target

    @property
    def labelframes(self):
        """returns a tuple of current gainlayer labelframe addresses"""

        return tuple(
            frame
            for frame in self.winfo_children()
            if isinstance(frame, ttk.LabelFrame)
        )

    def grid_configure(self):
        [
            self.columnconfigure(i, minsize=_configuration.level_width)
            for i, _ in enumerate(self.labelframes)
        ]
        [
            self.rowconfigure(0, minsize=_configuration.level_height)
            for i, _ in enumerate(self.labelframes)
        ]

    def upd_labelframe(self, labelframe):
        labelframe.sync()

    def on_update(self):
        for labelframe in self.labelframes:
            self.after(1, self.upd_labelframe, labelframe)

    def teardown(self):
        # deregisters submixframe as pdirty observer
        self.parent.subject_pdirty.remove(self)
        self.destroy()
