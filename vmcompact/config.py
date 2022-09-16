import tkinter as tk
from functools import partial
from tkinter import ttk

from . import builders
from .data import _base_values, _configuration


class Config(ttk.Frame):
    def __init__(self, parent, index, _id):
        super().__init__(parent)
        self.parent = parent
        self.index = index
        self.id = _id
        self.styletable = parent.styletable
        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs

        self.parent.subject.add(self)

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

    def scale_press(self, *args):
        self.after(1, self.remove_events)

    def remove_events(self):
        self.parent.target.event.remove("pdirty")
        self.parent.target.event.remove("ldirty")

    def scale_release(self, *args):
        _base_values.run_update = False
        self.after(1, self.add_events)

    def add_events(self):
        self.parent.target.event.add("pdirty")
        self.parent.target.event.add("ldirty")
        self.after(350, self.resume_updates)

    def resume_updates(self):
        _base_values.run_update = True

    def scale_enter(self, param, *args):
        val = self.slider_vars[self.slider_params.index(param)].get()
        self.parent.nav_frame.info_text.set(round(val, 1))

    def scale_leave(self, *args):
        self.parent.nav_frame.info_text.set("")

    def scale_callback(self, param, *args):
        """callback function for scale widget"""

        val = self.slider_vars[self.slider_params.index(param)].get()
        self.setter(param, val)
        self.parent.nav_frame.info_text.set(round(val, 1))

    def reset_scale(self, param, val, *args):
        self.setter(param, val)
        self.slider_vars[self.slider_params.index(param)].set(val)

    def toggle_p(self, param):
        val = self.param_vars[self.params.index(param)].get()
        self.setter(param, val)
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def on_update(self, subject):
        """update parameters"""
        if subject == "pdirty":
            self.sync()


class StripConfig(Config):
    def __init__(self, parent, index, _id):
        super().__init__(parent, index, _id)
        self.grid(column=0, row=1, columnspan=4, padx=(2,))
        self.builder = builders.StripConfigFrameBuilder(self)
        self.builder.setup()
        self.make_row_0()
        self.make_row_1()
        self.make_row_2()
        self.builder.grid_configure()

        self.sync()

    @property
    def target(self):
        """returns the strip class for this configframe in the current interface"""

        _target = super(StripConfig, self).target
        return getattr(_target, self.identifier)[self.index]

    def make_row_0(self):
        if self.index < self.phys_in:
            if self.parent.kind.name == "basic":
                self.builder.create_audibility_slider()
            else:
                self.builder.create_comp_slider()
                self.builder.create_gate_slider()
                self.builder.create_limit_slider()

    def make_row_1(self):
        self.builder.create_a_buttons()
        self.builder.create_b_buttons()

    def make_row_2(self):
        self.builder.create_param_buttons()

    def toggle_a(self, param):
        val = self.phys_out_params_vars[self.phys_out_params.index(param)].get()
        self.setter(param, val)
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def toggle_b(self, param):
        val = self.virt_out_params_vars[self.virt_out_params.index(param)].get()
        self.setter(param, val)
        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def teardown(self):
        self.builder.teardown()

    def sync(self):
        [
            self.phys_out_params_vars[i].set(self.getter(param))
            for i, param in enumerate(self.phys_out_params)
        ]
        [
            self.virt_out_params_vars[i].set(self.getter(param))
            for i, param in enumerate(self.virt_out_params)
        ]
        [
            self.param_vars[i].set(self.getter(param))
            for i, param in enumerate(self.params)
        ]

        if not _configuration.themes_enabled:
            [
                self.styletable.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.phys_out_params_vars[i].get() else "white"}',
                )
                for i, param in enumerate(self.phys_out_params)
            ]
            [
                self.styletable.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.virt_out_params_vars[i].get() else "white"}',
                )
                for i, param in enumerate(self.virt_out_params)
            ]
            [
                self.styletable.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.param_vars[i].get() else "white"}',
                )
                for i, param in enumerate(self.params)
            ]


class BusConfig(Config):
    def __init__(self, parent, index, _id):
        super().__init__(parent, index, _id)
        if _configuration.extends_horizontal:
            self.grid(column=0, row=1, columnspan=4, padx=(2,))
        else:
            self.grid(column=0, row=3, columnspan=4, padx=(2,))
        self.builder = builders.BusConfigFrameBuilder(self)
        self.builder.setup()
        self.make_row_0()
        self.make_row_1()
        self.builder.grid_configure()

        self.sync()

    @property
    def target(self):
        """returns the bus class for this configframe in the current interface"""

        _target = super(BusConfig, self).target
        return getattr(_target, self.identifier)[self.index]

    def make_row_0(self):
        self.builder.create_bus_mode_button()

    def make_row_1(self):
        self.builder.create_param_buttons()

    def current_bus_mode(self):
        for mode in self.bus_modes:
            if getattr(self.target.mode, mode):
                return mode

    def rotate_bus_modes_right(self, *args):
        current_mode = self.current_bus_mode()
        next = self.bus_modes.index(current_mode) + 1
        if next < len(self.bus_modes):
            setattr(
                self.target.mode,
                self.bus_modes[next],
                True,
            )
            self.bus_mode_label_text.set(self.bus_mode_map[self.bus_modes[next]])
        else:
            self.target.mode.normal = True
            self.bus_mode_label_text.set("Normal")

    def rotate_bus_modes_left(self, *args):
        current_mode = self.current_bus_mode()
        prev = self.bus_modes.index(current_mode) - 1
        if prev < 0:
            self.target.mode.rearonly = True
            self.bus_mode_label_text.set("Rear Only")
        else:
            setattr(
                self.target.mode,
                self.bus_modes[prev],
                True,
            )
            self.bus_mode_label_text.set(self.bus_mode_map[self.bus_modes[prev]])

    def teardown(self):
        self.builder.teardown()

    def sync(self):
        [
            self.param_vars[i].set(self.getter(param))
            for i, param in enumerate(self.params)
        ]
        self.bus_mode_label_text.set(self.bus_mode_map[self.current_bus_mode()])
        if not _configuration.themes_enabled:
            [
                self.styletable.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.param_vars[i].get() else "white"}',
                )
                for i, param in enumerate(self.params)
            ]
