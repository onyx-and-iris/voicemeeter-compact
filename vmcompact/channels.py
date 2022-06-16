import tkinter as tk
from math import log
from tkinter import ttk

from . import builders
from .data import _base_values, _configuration


class ChannelLabelFrame(ttk.LabelFrame):
    """Base class for a single channel"""

    def __init__(self, parent, index, id):
        super().__init__(parent)
        self.parent = parent
        self.index = index
        self.id = id
        self.styletable = self.parent.parent.styletable

        self.builder = builders.ChannelLabelFrameBuilder(self, index, id)
        self.builder.setup()
        self.builder.add_progressbar()
        self.builder.add_scale()
        self.builder.add_mute_button()
        self.builder.add_conf_button()
        self.builder.add_gain_label()
        self.sync()
        self.grid_configure()

        self.configbuilder = builders.MainFrameBuilder(self.parent.parent)

    @property
    def identifier(self):
        return self.id

    @property
    def target(self):
        """returns the current interface"""

        return self.parent.target

    def getter(self, param):
        if hasattr(self.target, param):
            return getattr(self.target, param)

    def setter(self, param, value):
        if hasattr(self.target, param):
            setattr(self.target, param, value)

    def scale_callback(self, *args):
        """callback function for scale widget"""

        self.setter("gain", self.gain.get())
        self.gainlabel.set(round(self.gain.get(), 1))

    def toggle_mute(self, *args):
        self.target.mute = self.mute.get()
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{self.identifier}Mute{self.index}.TButton",
                background=f'{"red" if self.mute.get() else "white"}',
            )

    def reset_gain(self, *args):
        self.setter("gain", 0)
        self.gain.set(0)

    def scale_press(self, *args):
        _base_values.in_scale_button_1 = True

    def scale_release(self, *args):
        _base_values.in_scale_button_1 = False

    def _on_mousewheel(self, event):
        self.gain.set(
            self.gain.get()
            + (
                _configuration.mwscroll_step
                if event.delta > 0
                else -_configuration.mwscroll_step
            )
        )
        if self.gain.get() > 12:
            self.gain.set(12)
        elif self.gain.get() < -60:
            self.gain.set(-60)
        self.setter("gain", self.gain.get())

    def open_config(self):
        if self.conf.get():
            self.configbuilder.create_configframe(self.identifier, self.index, self.id)
        else:
            self.parent.parent.config_frame.teardown()
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{self.identifier}Conf{self.index}.TButton",
                background=f'{"yellow" if self.conf.get() else "white"}',
            )

    def sync(self):
        self.after(_base_values.pdelay, self.sync_params)
        self.after(100, self.sync_labels)

    def sync_params(self):
        """sync parameter states, update button colours"""
        self.gain.set(self.getter("gain"))
        self.gainlabel.set(round(self.gain.get(), 1))
        self.mute.set(self.getter("mute"))
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{self.identifier}Mute{self.index}.TButton",
                background=f'{"red" if  self.mute.get() else "white"}',
            )

    def sync_labels(self):
        """sync labelframes according to label text"""
        retval = self.getter("label")
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

    def grid_configure(self):
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


class Strip(ChannelLabelFrame):
    """Concrete class representing a single strip"""

    def __init__(self, parent, index, id):
        super().__init__(parent, index, id)
        if index <= parent.phys_in:
            self.level_offset = index * 2
        else:
            self.level_offset = parent.phys_in * 2 + (index - parent.phys_in) * 8

    @property
    def target(self):
        """returns the strip class for this labelframe in the current interface"""

        _target = super(Strip, self).target
        return getattr(_target, self.identifier)[self.index]

    def upd_levels(self):
        """
        Updates level values.

        Checks offset against expected level array size to avoid a race condition
        """
        if self.level_offset + 1 < len(self.parent.parent.strip_levels):
            if (
                any(
                    self.parent.parent.strip_comp[
                        self.level_offset : self.level_offset + 1
                    ]
                )
                or self.level.get() > 0
            ):
                val = self.convert_level(
                    max(
                        self.parent.parent.strip_levels[
                            self.level_offset : self.level_offset + 1
                        ]
                    )
                )
                self.level.set(
                    (0 if self.mute.get() else 100 + val - 18 + self.gain.get())
                )

    def on_update(self):
        """update levels"""

        self.after(_base_values.ldelay, self.upd_levels)


class Bus(ChannelLabelFrame):
    """Concrete bus class representing a single bus"""

    def __init__(self, parent, index, id):
        super().__init__(parent, index, id)
        self.level_offset = index * 8

    @property
    def target(self):
        """returns the bus class for this labelframe in the current interface"""

        _target = super(Bus, self).target
        return getattr(_target, self.identifier)[self.index]

    def upd_levels(self):
        if self.level_offset + 1 < len(self.parent.parent.bus_levels):
            if (
                any(
                    self.parent.parent.bus_comp[
                        self.level_offset : self.level_offset + 1
                    ]
                )
                or self.level.get() > 0
            ):
                val = self.convert_level(
                    max(
                        self.parent.parent.bus_levels[
                            self.level_offset : self.level_offset + 1
                        ]
                    )
                )
                self.level.set((0 if self.mute.get() else 100 + val - 18))

    def on_update(self):
        """update levels"""

        self.after(_base_values.ldelay, self.upd_levels)


class ChannelFrame(ttk.Frame):
    def init(self, parent, id):
        super().__init__(parent)
        self.parent = parent
        self.id = id
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs

        # registers channelframe as pdirty observer
        self.parent.subject_pdirty.add(self)

    @property
    def target(self):
        """returns the current interface"""

        return self.parent.target

    @property
    def identifier(self):
        return self.id

    @property
    def labelframes(self):
        """returns a tuple of current channel labelframe addresses"""

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
        [self.rowconfigure(0, minsize=100) for i, _ in enumerate(self.labelframes)]

    def upd_labelframe(self, labelframe):
        labelframe.sync()

    def on_update(self):
        """update parameters"""

        for labelframe in self.labelframes:
            self.after(1, self.upd_labelframe, labelframe)

    def teardown(self):
        # deregisters channelframe as pdirty observer

        self.parent.subject_pdirty.remove(self)
        self.destroy()
        setattr(self.parent, f"{self.identifier}_frame", None)


def _make_channelframe(parent, id):
    """
    Creates a Channel Frame class of type strip or bus
    """

    phys_in, virt_in = parent.kind.ins
    phys_out, virt_out = parent.kind.outs

    def init_labels(self, id):
        """
        Grids each labelframe, grid_removes any without a label
        """

        for i, labelframe in enumerate(
            getattr(self, "strips" if id == "strip" else "buses")
        ):
            labelframe.grid(row=0, column=i)
            if not labelframe.target.label:
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()

    def init_strip(self, *args, **kwargs):
        self.init(parent, id)
        self.strips = tuple(Strip(self, i, id) for i in range(phys_in + virt_in))
        self.grid(row=0, column=0, sticky=(tk.W))
        self.grid_configure()
        init_labels(self, id)

    def init_bus(self, *args, **kwargs):
        self.init(parent, id)
        self.buses = tuple(Bus(self, i, id) for i in range(phys_out + virt_out))
        if _configuration.extended:
            if _configuration.extends_horizontal:
                self.grid(row=0, column=2, sticky=(tk.W))
            else:
                self.grid(row=2, column=0, sticky=(tk.W))
        else:
            self.grid(row=0, column=0)
        self.grid_configure()
        init_labels(self, id)

    if id == "strip":
        CHANNELFRAME_cls = type(
            f"ChannelFrame{id.capitalize}",
            (ChannelFrame,),
            {
                "__init__": init_strip,
            },
        )
    else:
        CHANNELFRAME_cls = type(
            f"ChannelFrame{id.capitalize}",
            (ChannelFrame,),
            {
                "__init__": init_bus,
            },
        )
    return CHANNELFRAME_cls(parent)
