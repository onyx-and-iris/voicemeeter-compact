import tkinter as tk
from tkinter import ttk
from functools import partial

from .data import _base_vals


class Config(ttk.Frame):
    def __init__(self, parent, index, _id):
        super().__init__(parent)
        self._parent = parent
        self.index = index
        self.id = _id
        self.s = parent.styletable

        self.phys_in, self.virt_in = parent.kind.ins
        self.phys_out, self.virt_out = parent.kind.outs

        self.watch_pdirty()

    @property
    def identifier(self):
        return self.id

    @property
    def target(self):
        """returns the current interface"""
        return self._parent.target

    def getter(self, param):
        if param in dir(self.target):
            return getattr(self.target, param)

    def setter(self, param, value):
        if param in dir(self.target):
            setattr(self.target, param, value)

    def scale_enter(self, *args):
        _base_vals.in_scale_button_1 = True

    def scale_leave(self, *args):
        _base_vals.in_scale_button_1 = False
        self._parent.nav_frame.info_text.set("")

    def scale_callback(self, param, *args):
        """callback function for scale widget"""
        val = self.slider_vars[self.slider_params.index(param)].get()
        self.setter(param, val)
        self._parent.nav_frame.info_text.set(round(val, 1))

    def reset_scale(self, param, val, *args):
        self.setter(param, val)
        self.slider_vars[self.slider_params.index(param)].set(val)

    def col_row_configure(self):
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.W, tk.E))
            for child in self.winfo_children()
            if isinstance(child, ttk.Checkbutton)
        ]
        self.grid(sticky=(tk.W))

    def watch_pdirty(self):
        self.after(1, self.watch_pdirty_step)

    def watch_pdirty_step(self):
        """keeps params synced but ensures sliders are responsive"""
        if self._parent.pdirty and not _base_vals.in_scale_button_1:
            self.sync()
        self.after(_base_vals.pdelay, self.watch_pdirty_step)


class StripConfig(Config):
    def __init__(self, parent, index, _id):
        super().__init__(parent, index, _id)

        # create parameter variables
        if self._parent.kind.name == "Basic":
            self.slider_params = ("audibility",)
            self.slider_vars = (tk.DoubleVar(),)
        else:
            self.slider_params = ("comp", "gate", "limit")
            self.slider_vars = [
                tk.DoubleVar() for i, _ in enumerate(self.slider_params)
            ]

        self.phys_out_params = [f"A{i+1}" for i in range(self.phys_out)]
        self.phys_out_params_vars = [
            tk.BooleanVar() for i, _ in enumerate(self.phys_out_params)
        ]

        self.virt_out_params = [f"B{i+1}" for i in range(self.virt_out)]
        self.virt_out_params_vars = [
            tk.BooleanVar() for i, _ in enumerate(self.virt_out_params)
        ]

        self.params = ("mono", "solo")
        self.param_vars = list(tk.BooleanVar() for i, _ in enumerate(self.params))

        self.make_row0()
        self.make_row1()
        self.make_row2()

        # sync all parameters
        self.sync()
        self.sync_sliders()

        self.col_row_configure()

    @property
    def target(self):
        """use the correct interface"""
        _target = super(StripConfig, self).target
        return getattr(_target, self.identifier)[self.index]

    def make_row0(self):
        # Create sliders
        if self.index < self.phys_in:
            if self._parent.kind.name == "Basic":
                # audibility
                aud_label = ttk.Label(self, text="Audibility")
                aud_scale = ttk.Scale(
                    self,
                    from_=0.0,
                    to=10.0,
                    orient="horizontal",
                    length=_base_vals.level_width,
                    variable=self.slider_vars[self.slider_params.index("audibility")],
                    command=partial(self.scale_callback, "audibility"),
                )
                aud_scale.bind(
                    "<Double-Button-1>", partial(self.reset_scale, "audibility", 0)
                )
                aud_scale.bind("<Button-1>", self.scale_enter)
                aud_scale.bind("<ButtonRelease-1>", self.scale_leave)

                aud_label.grid(column=0, row=0)
                aud_scale.grid(column=1, row=0)
            else:
                # comp
                comp_label = ttk.Label(self, text="Comp")
                comp_scale = ttk.Scale(
                    self,
                    from_=0.0,
                    to=10.0,
                    orient="horizontal",
                    length=_base_vals.level_width,
                    variable=self.slider_vars[self.slider_params.index("comp")],
                    command=partial(self.scale_callback, "comp"),
                )
                comp_scale.bind(
                    "<Double-Button-1>", partial(self.reset_scale, "comp", 0)
                )
                comp_scale.bind("<Button-1>", self.scale_enter)
                comp_scale.bind("<ButtonRelease-1>", self.scale_leave)

                # gate
                gate_label = ttk.Label(self, text="Gate")
                gate_scale = ttk.Scale(
                    self,
                    from_=0.0,
                    to=10.0,
                    orient="horizontal",
                    length=_base_vals.level_width,
                    variable=self.slider_vars[self.slider_params.index("gate")],
                    command=partial(self.scale_callback, "gate"),
                )
                gate_scale.bind(
                    "<Double-Button-1>", partial(self.reset_scale, "gate", 0)
                )
                gate_scale.bind("<Button-1>", self.scale_enter)
                gate_scale.bind("<ButtonRelease-1>", self.scale_leave)

                # limit
                limit_label = ttk.Label(self, text="Limit")
                limit_scale = ttk.Scale(
                    self,
                    from_=-40,
                    to=12,
                    orient="horizontal",
                    length=_base_vals.level_width,
                    variable=self.slider_vars[self.slider_params.index("limit")],
                    command=partial(self.scale_callback, "limit"),
                )
                limit_scale.bind(
                    "<Double-Button-1>", partial(self.reset_scale, "limit", 12)
                )
                limit_scale.bind("<Button-1>", self.scale_enter)
                limit_scale.bind("<ButtonRelease-1>", self.scale_leave)

                # Position sliders
                comp_label.grid(column=0, row=0)
                comp_scale.grid(column=1, row=0)
                gate_label.grid(column=2, row=0)
                gate_scale.grid(column=3, row=0)
                limit_label.grid(column=4, row=0)
                limit_scale.grid(column=5, row=0)

    def make_row1(self):
        # create buttons
        self.a_buttons = [
            ttk.Checkbutton(
                self,
                text=param,
                command=partial(self.toggle_a, param),
                style=f"{'Toggle.TButton' if _base_vals.using_theme else f'{param}.TButton'}",
                variable=self.phys_out_params_vars[self.phys_out_params.index(param)],
            )
            for param in self.phys_out_params
        ]
        self.b_buttons = [
            ttk.Checkbutton(
                self,
                text=param,
                command=partial(self.toggle_b, param),
                style=f"{'Toggle.TButton' if _base_vals.using_theme else f'{param}.TButton'}",
                variable=self.virt_out_params_vars[self.virt_out_params.index(param)],
            )
            for param in self.virt_out_params
        ]

        # set button positions
        [
            button.grid(
                column=self.a_buttons.index(button),
                row=1,
            )
            for button in self.a_buttons
        ]
        [
            button.grid(
                column=len(self.a_buttons) + self.b_buttons.index(button),
                row=1,
            )
            for button in self.b_buttons
        ]

    def toggle_a(self, param):
        val = self.phys_out_params_vars[self.phys_out_params.index(param)].get()
        self.setter(param, val)
        if not _base_vals.using_theme:
            self.s.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def toggle_b(self, param):
        val = self.virt_out_params_vars[self.virt_out_params.index(param)].get()
        self.setter(param, val)
        if not _base_vals.using_theme:
            self.s.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def make_row2(self):
        if self._parent.kind.name in ("Banana", "Potato"):
            if self.index == self.phys_in:
                self.params = list(map(lambda x: x.replace("mono", "mc"), self.params))
            if self._parent.kind.name == "Banana":
                pass
                # karaoke modes not in RT Packet yet. May implement in future
                """
                if self.index == self.phys_in + 1:
                    self.params = list(
                        map(lambda x: x.replace("mono", "k"), self.params)
                    )
                    self.param_vars[self.params.index("k")] = tk.IntVar
                """
            else:
                if self.index == self.phys_in + self.virt_in - 1:
                    self.params = list(
                        map(lambda x: x.replace("mono", "mc"), self.params)
                    )

        param_buttons = [
            ttk.Checkbutton(
                self,
                text=param,
                command=partial(self.toggle_p, param),
                style=f"{'Toggle.TButton' if _base_vals.using_theme else f'{param}.TButton'}",
                variable=self.param_vars[self.params.index(param)],
            )
            for param in self.params
        ]
        [
            button.grid(
                column=param_buttons.index(button),
                row=2,
            )
            for button in param_buttons
        ]

    def toggle_p(self, param):
        val = self.param_vars[self.params.index(param)].get()
        self.setter(param, val)
        if not _base_vals.using_theme:
            self.s.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def sync(self):
        [
            self.phys_out_params_vars[self.phys_out_params.index(param)].set(
                self.getter(param)
            )
            for param in self.phys_out_params
        ]
        [
            self.virt_out_params_vars[self.virt_out_params.index(param)].set(
                self.getter(param)
            )
            for param in self.virt_out_params
        ]
        [
            self.param_vars[self.params.index(param)].set(self.getter(param))
            for param in self.params
        ]
        if not _base_vals.using_theme:
            [
                self.s.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.phys_out_params_vars[self.phys_out_params.index(param)].get() else "white"}',
                )
                for param in self.phys_out_params
            ]
            [
                self.s.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.virt_out_params_vars[self.virt_out_params.index(param)].get() else "white"}',
                )
                for param in self.virt_out_params
            ]
            [
                self.s.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.param_vars[self.params.index(param)].get() else "white"}',
                )
                for param in self.params
            ]

    def sync_sliders(self):
        [
            self.slider_vars[self.slider_params.index(param)].set(self.getter(param))
            for param in self.slider_params
        ]

    def col_row_configure(self):
        super(StripConfig, self).col_row_configure()
        [
            self.columnconfigure(i, minsize=80)
            for i in range(self.phys_out + self.virt_out)
        ]


class BusConfig(Config):
    def __init__(self, parent, index, _id):
        super().__init__(parent, index, _id)
        # fmt: off
        # create parameter variables
        self.bus_modes = (
            "normal", "Amix", "Bmix", "Repeat", "Composite", "TVMix", "UpMix21",
            "UpMix41", "UpMix61", "CenterOnly", "LFEOnly", "RearOnly",
        )
        # fmt: on
        self.params = ("mono", "eq", "eq_ab")
        self.param_vars = [tk.BooleanVar() for i, _ in enumerate(self.params)]

        # sync all parameters
        self.sync()

        self.make_row0()
        self.make_row1()

        self.col_row_configure()

    @property
    def target(self):
        """returns the current interface"""
        _target = super(BusConfig, self).target
        return getattr(_target, self.identifier)[self.index]

    @property
    def bus_mode(self):
        return self._parent.bus_modes_cache[
            "vban" if _base_vals.vban_connected else "vmr"
        ][self.index].get()

    @bus_mode.setter
    def bus_mode(self, val):
        self._parent.bus_modes_cache["vban" if _base_vals.vban_connected else "vmr"][
            self.index
        ].set(val)

    def make_row0(self):
        self.bus_mode_label_text = tk.StringVar(value=f"Bus Mode: {self.bus_mode}")
        self.busmode_button = ttk.Button(self, textvariable=self.bus_mode_label_text)
        self.busmode_button.grid(column=0, row=0, columnspan=2, sticky=(tk.W))
        self.busmode_button.bind("<Button-1>", self.rotate_bus_modes_right)
        self.busmode_button.bind("<Button-3>", self.rotate_bus_modes_left)

    def rotate_bus_modes_right(self, *args):
        current_index = self.bus_modes.index(self.bus_mode)
        if current_index + 1 < len(self.bus_modes):
            self.bus_mode = self.bus_modes[current_index + 1]
        else:
            self.bus_mode = self.bus_modes[0]
        setattr(self.target.mode, self.bus_mode.lower(), True)
        self.bus_mode_label_text.set(f"Bus Mode: {self.bus_mode}")

    def rotate_bus_modes_left(self, *args):
        current_index = self.bus_modes.index(self.bus_mode)
        if current_index == 0:
            self.bus_mode = self.bus_modes[-1]
        else:
            self.bus_mode = self.bus_modes[current_index - 1]
        setattr(self.target.mode, self.bus_mode.lower(), True)
        self.bus_mode_label_text.set(f"Bus Mode: {self.bus_mode}")

    def make_row1(self):
        param_buttons = [
            ttk.Checkbutton(
                self,
                text=param,
                command=partial(self.toggle_p, param),
                style=f"{'Toggle.TButton' if _base_vals.using_theme else f'{param}.TButton'}",
                variable=self.param_vars[self.params.index(param)],
            )
            for param in self.params
        ]
        [
            button.grid(
                column=param_buttons.index(button),
                row=1,
            )
            for button in param_buttons
        ]

    def toggle_p(self, param):
        val = self.param_vars[self.params.index(param)].get()
        self.setter(param, val)
        if not _base_vals.using_theme:
            self.s.configure(
                f"{param}.TButton", background=f'{"green" if val else "white"}'
            )

    def col_row_configure(self):
        super(BusConfig, self).col_row_configure()
        [
            self.columnconfigure(i, minsize=80)
            for i in range(self.phys_out + self.virt_out)
        ]

    def sync(self):
        for i, mode in enumerate(self.bus_modes):
            if getattr(self.target.mode, mode.lower()):
                self.bus_mode = self.bus_modes[i]
        [
            self.param_vars[self.params.index(param)].set(self.getter(param))
            for param in self.params
        ]
        if not _base_vals.using_theme:
            [
                self.s.configure(
                    f"{param}.TButton",
                    background=f'{"green" if self.param_vars[self.params.index(param)].get() else "white"}',
                )
                for param in self.params
            ]
