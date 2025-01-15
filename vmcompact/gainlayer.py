import tkinter as tk
from tkinter import ttk

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

        self.builder = builders.ChannelLabelFrameBuilder(self, index, id='gainlayer')
        self.builder.setup()
        self.builder.add_progressbar()
        self.builder.add_scale()
        self.builder.add_gain_label()
        self.builder.add_on_button()
        self.sync_params()
        self.sync_labels()
        self.grid_configure()

    @property
    def target(self):
        """returns the strip[i].gainlayer class in the current interface"""

        _target = self.parent.target
        return _target.strip[self.index].gainlayer[self.j]

    @property
    def identifier(self):
        return 'gainlayer'

    def getter(self, param):
        try:
            return getattr(self.target, param)
        except AttributeError as e:
            self.logger(f'{type(e).__name__}: {e}')

    def setter(self, param, value):
        if param in dir(self.target):  # avoid calling getattr (with hasattr)
            setattr(self.target, param, value)

    def reset_gain(self, *args):
        self.setter('gain', 0)
        self.gain.set(0)
        self.gainlabel.set(self.gain.get())

    def scale_callback(self, *args):
        """callback function for scale widget"""

        val = round(self.gain.get(), 1)
        self.setter('gain', val)
        self.gainlabel.set(val)

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
        _base_values.run_update = False
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
        self.setter('gain', self.gain.get())
        self.after(1, self.resume_updates)

    def set_on(self):
        """enables a gainlayer. sets its button colour"""

        setattr(
            self.parent.target.strip[self.index],
            self.parent.buses[self.j],
            self.on.get(),
        )
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f'{self.identifier}On{self.index}.TButton',
                background=f'{"green" if self.on.get() else "white"}',
            )

    def on_update(self, subject):
        if subject == 'ldirty':
            self.upd_levels()
        elif subject == 'pdirty':
            self.sync_params()
        elif subject == 'labelframe':
            self.after(5, self.sync_labels)

    def sync_params(self):
        self.gain.set(self.getter('gain'))
        self.gainlabel.set(round(self.gain.get(), 1))
        self.on.set(
            getattr(
                self.parent.target.strip[self.index],
                self.parent.buses[self.j],
            )
        )
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f'{self.identifier}On{self.index}.TButton',
                background=f'{"green" if self.on.get() else "white"}',
            )

    def sync_labels(self):
        """sync params with voicemeeter"""
        retval = self.parent.target.strip[self.index].label
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

    def upd_levels(self):
        """
        Updates level values.
        """

        if self.parent.target.strip[self.index].levels.is_updated:
            val = max(self.parent.target.strip[self.index].levels.prefader)
            self.level.set(
                (
                    0
                    if self.parent.parent.strip_frame.strips[self.index].mute.get()
                    or not self.on.get()
                    else 72 + val - 12 + self.gain.get()
                )
            )

    def grid_configure(self):
        self.grid(padx=_configuration.channel_xpadding, sticky=(tk.N, tk.S))
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
            self.rowconfigure(2, minsize=70)
        else:
            self.rowconfigure(2, minsize=55)


class SubMixFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs
        self.buses = tuple(f'A{i + 1}' for i in range(self.phys_out)) + tuple(
            f'B{i + 1}' for i in range(self.virt_out)
        )

        self.gainlayers = [
            GainLayer(self, index, _configuration.submixes) for index in range(8)
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
            if parent.bus_frame and parent.bus_frame.grid_info():
                self.grid(
                    row=parent.bus_frame.grid_info()['row'], column=0, sticky=(tk.W)
                )
                parent.bus_frame.grid_remove()
            else:
                self.grid(row=2, column=0, sticky=(tk.W))

        self.grid_configure()
        """
        Grids each labelframe, grid_removes any without a label
        """
        for i, labelframe in enumerate(self.labelframes):
            labelframe.grid(row=0, column=i)
            if not self.target.strip[i].label:
                self.columnconfigure(i, minsize=0)
                labelframe.grid_remove()

        self.parent.subject.add(self)

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

    def on_update(self, subject):
        if subject == 'pdirty':
            for labelframe in self.labelframes:
                labelframe.on_update('labelframe')

    def grid_configure(self):
        [
            self.columnconfigure(i, minsize=_configuration.channel_width)
            for i, _ in enumerate(self.labelframes)
        ]
        [
            self.rowconfigure(0, minsize=_configuration.channel_height)
            for i, _ in enumerate(self.labelframes)
        ]

    def teardown(self):
        # deregisters submixframe as pdirty observer
        [self.parent.subject.remove(frame) for frame in self.gainlayers]
        self.parent.subject.remove(self)
        self.destroy()
