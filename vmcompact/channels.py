import logging
import tkinter as tk
from tkinter import ttk

from . import builders
from .data import _base_values, _configuration

logger = logging.getLogger(__name__)


class ChannelLabelFrame(ttk.LabelFrame):
    """Base class for a single channel"""

    def __init__(self, parent, index, id):
        super().__init__(parent)
        self.parent = parent
        self.index = index
        self.id = id
        self.logger = logger.getChild(self.__class__.__name__)
        self.styletable = self.parent.parent.styletable

        self.builder = builders.ChannelLabelFrameBuilder(self, index, id)
        self.builder.setup()
        self.builder.add_progressbar()
        self.builder.add_scale()
        self.builder.add_mute_button()
        self.builder.add_conf_button()
        self.builder.add_gain_label()
        self.sync_params()
        self.sync_labels()
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
        try:
            return getattr(self.target, param)
        except AttributeError as e:
            self.logger(f'{type(e).__name__}: {e}')

    def setter(self, param, value):
        if param in dir(self.target):  # avoid calling getattr (with hasattr)
            setattr(self.target, param, value)

    def scale_callback(self, *args):
        """callback function for scale widget"""

        val = round(self.gain.get(), 1)
        self.setter('gain', val)
        self.gainlabel.set(val)

    def toggle_mute(self, *args):
        self.target.mute = self.mute.get()
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f'{self.identifier}Mute{self.index}.TButton',
                background=f'{"red" if self.mute.get() else "white"}',
            )

    def reset_gain(self, *args):
        self.setter('gain', 0)
        self.gain.set(0)
        self.gainlabel.set(self.gain.get())

    def scale_press(self, *args):
        self.after(1, self.remove_events)

    def remove_events(self):
        self.parent.target.event.remove('pdirty')
        self.parent.target.event.remove('ldirty')

    def scale_release(self, *args):
        _base_values.run_update = False
        self.after(1, self.add_events)

    def add_events(self):
        self.parent.target.event.add('pdirty')
        self.parent.target.event.add('ldirty')
        self.after(500, self.resume_updates)

    def pause_updates(self, func, *args):
        """function wrapper, adds a 50ms delay on updates"""
        _base_values.run_update = False

        func(*args)

        self.after(50, self.resume_updates)

    def resume_updates(self):
        _base_values.run_update = True

    def _on_mousewheel(self, event):
        self.gain.set(
            round(
                self.gain.get()
                + (
                    _configuration.mwscroll_step
                    if event.delta > 0
                    else -_configuration.mwscroll_step
                ),
                1,
            )
        )
        if self.gain.get() > 12:
            self.gain.set(12)
        elif self.gain.get() < -60:
            self.gain.set(-60)
        self.setter('gain', self.gain.get())
        self.gainlabel.set(round(self.gain.get(), 1))

    def open_config(self):
        if self.conf.get():
            self.configbuilder.create_configframe(self.identifier, self.index, self.id)
        else:
            self.parent.parent.config_frame.teardown()
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f'{self.identifier}Conf{self.index}.TButton',
                background=f'{"yellow" if self.conf.get() else "white"}',
            )

    def on_update(self, subject):
        if subject == 'ldirty':
            self.upd_levels()
        elif subject == 'pdirty':
            self.sync_params()
        elif subject == 'labelframe':
            self.after(5, self.sync_labels)

    def sync_params(self):
        """sync parameter states, update button colours"""
        self.gain.set(self.getter('gain'))
        self.gainlabel.set(round(self.gain.get(), 1))
        self.mute.set(self.getter('mute'))
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f'{self.identifier}Mute{self.index}.TButton',
                background=f'{"red" if self.mute.get() else "white"}',
            )

    def sync_labels(self):
        """sync labelframes according to label text"""
        retval = self.getter('label')
        if self.parent.label_cache[self.id][self.index] != retval:
            self.parent.label_cache[self.id][self.index] = retval
            if len(retval) > 10:
                retval = f'{retval[:8]}..'
            if not retval:
                self.parent.columnconfigure(self.index, minsize=0)
                self.parent.parent.subject.remove(self)
                self.grid_remove()
            else:
                self.parent.parent.subject.add(self)
                self.grid()
            self.configure(text=retval)

    def grid_configure(self):
        self.grid(padx=_configuration.channel_xpadding, sticky=(tk.N, tk.S))
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
        """
        if self.index < self.parent.parent.kind.num_strip:
            if self.target.levels.is_updated:
                val = max(self.target.levels.prefader)
                self.level.set(
                    (0 if self.mute.get() else 72 + val - 12 + self.gain.get())
                )


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
        if self.index < self.parent.parent.kind.num_bus:
            if self.target.levels.is_updated or self.level.get() != -118:
                val = max(self.target.levels.all)
                self.level.set((0 if self.mute.get() else 72 + val - 12))


class ChannelFrame(ttk.Frame):
    def init(self, parent, id):
        super().__init__(parent)
        self.parent = parent
        self.id = id
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs
        self.label_cache = {
            'strip': [''] * (self.phys_in + self.virt_in),
            'bus': [''] * (self.phys_out + self.virt_out),
        }
        self.parent.subject.add(self)
        self.update_labels()

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

    def update_labels(self):
        for labelframe in self.labelframes:
            labelframe.on_update('labelframe')

    def on_update(self, subject):
        if subject == 'pdirty':
            self.update_labels()

    def grid_configure(self):
        [
            self.columnconfigure(i, minsize=_configuration.channel_width)
            for i, _ in enumerate(self.labelframes)
        ]
        [self.rowconfigure(0, minsize=100) for i, _ in enumerate(self.labelframes)]

    def teardown(self):
        [self.parent.subject.remove(frame) for frame in self.labelframes]
        self.parent.subject.remove(self)
        self.destroy()
        setattr(self.parent, f'{self.identifier}_frame', None)


def _make_channelframe(parent, identifier):
    """
    Creates a Channel Frame class of type strip or bus
    """

    phys_in, virt_in = parent.kind.ins
    phys_out, virt_out = parent.kind.outs

    def init_labels(self):
        """
        Grids each labelframe, grid_removes any without a label
        """

        for i, labelframe in enumerate(
            getattr(self, 'strips' if identifier == 'strip' else 'buses')
        ):
            labelframe.grid(row=0, column=i)
            label = labelframe.target.label
            if not label:
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()
            self.label_cache[identifier][i] = label

    def init_strip(self, *args, **kwargs):
        self.init(parent, identifier)
        self.strips = tuple(
            Strip(self, i, identifier) for i in range(phys_in + virt_in)
        )
        self.grid(row=0, column=0, sticky=(tk.W))
        self.grid_configure()
        init_labels(self)

    def init_bus(self, *args, **kwargs):
        self.init(parent, identifier)
        self.buses = tuple(Bus(self, i, identifier) for i in range(phys_out + virt_out))
        if _configuration.extended:
            if _configuration.extends_horizontal:
                self.grid(row=0, column=2, sticky=(tk.W))
            else:
                self.grid(row=2, column=0, sticky=(tk.W))
        else:
            self.grid(row=0, column=0)
        self.grid_configure()
        init_labels(self)

    if identifier == 'strip':
        CHANNELFRAME_cls = type(
            f'ChannelFrame{identifier.capitalize()}',
            (ChannelFrame,),
            {
                '__init__': init_strip,
            },
        )
    else:
        CHANNELFRAME_cls = type(
            f'ChannelFrame{identifier.capitalize()}',
            (ChannelFrame,),
            {
                '__init__': init_bus,
            },
        )
    return CHANNELFRAME_cls(parent)
