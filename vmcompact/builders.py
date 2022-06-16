import abc
import tkinter as tk
from functools import partial
from tkinter import ttk

import sv_ttk

from .banner import Banner
from .channels import _make_channelframe
from .config import BusConfig, StripConfig
from .data import _base_values, _configuration
from .navigation import Navigation


class AbstractBuilder(abc.ABC):
    @abc.abstractmethod
    def setup(self):
        """register as observable"""
        pass

    @abc.abstractmethod
    def teardown(self):
        """deregister as observable"""
        pass


class MainFrameBuilder(AbstractBuilder):
    """Responsible for building the frames that sit directly on the mainframe"""

    def __init__(self, app):
        self.kind = app.kind
        self.app = app

    def setup(self):
        self.app.title(
            f'Voicemeeter{self.kind.name}.Compact [{"Local" if not _base_values.vban_connected else "Network"} Connection]'
        )
        self.app.resizable(False, False)
        if _configuration.themes_enabled:
            print("Applying Sunvalley Theme")
            sv_ttk.set_theme(_configuration.theme_mode)

    def create_channelframe(self, type_):
        if type_ == "strip":
            self.app.strip_frame = _make_channelframe(self.app, type_)
        else:
            self.app.bus_frame = _make_channelframe(self.app, type_)

    def create_separator(self):
        self.app.sep = ttk.Separator(self.app, orient="vertical")
        self.app.sep.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.app.columnconfigure(1, minsize=15)

    def create_navframe(self):
        self.app.nav_frame = Navigation(self.app)

    def create_configframe(self, type_, index, id):
        if type_ == "strip":
            self.app.config_frame = StripConfig(self.app, index, id)
            if self.app.strip_frame:
                [
                    frame.conf.set(False)
                    for i, frame in enumerate(self.app.strip_frame.labelframes)
                    if i != index
                ]
            if self.app.bus_frame:
                [
                    frame.conf.set(False)
                    for _, frame in enumerate(self.app.bus_frame.labelframes)
                ]
        else:
            self.app.config_frame = BusConfig(self.app, index, id)
            if self.app.bus_frame:
                [
                    frame.conf.set(False)
                    for i, frame in enumerate(self.app.bus_frame.labelframes)
                    if i != index
                ]
            if self.app.strip_frame:
                [
                    frame.conf.set(False)
                    for _, frame in enumerate(self.app.strip_frame.labelframes)
                ]
        if not _configuration.themes_enabled:
            if self.app.strip_frame:
                [
                    frame.styletable.configure(
                        f"{frame.identifier}Conf{frame.index}.TButton",
                        background=f"{'white' if not frame.conf.get() else 'yellow'}",
                    )
                    for _, frame in enumerate(self.app.strip_frame.labelframes)
                ]
            if self.app.bus_frame:
                [
                    frame.styletable.configure(
                        f"{frame.identifier}Conf{frame.index}.TButton",
                        background=f"{'white' if not frame.conf.get() else 'yellow'}",
                    )
                    for _, frame in enumerate(self.app.bus_frame.labelframes)
                ]
        self.app.after(5, self.reset_config_frames)

    def reset_config_frames(self):
        [
            frame.teardown()
            for frame in self.app.configframes
            if frame != self.app.config_frame
        ]

    def create_banner(self):
        self.app.banner = Banner(self.app)
        self.app.banner.grid(row=4, column=0, columnspan=3)

    def teardown(self):
        pass


class NavigationFrameBuilder(AbstractBuilder):
    """Responsible for building navigation frame widgets"""

    def __init__(self, navframe):
        self.navframe = navframe

    def setup(self):
        self.navframe.submix = tk.BooleanVar()
        self.navframe.channel = tk.BooleanVar()
        self.navframe.extend = tk.BooleanVar(value=_configuration.extended)
        self.navframe.info = tk.BooleanVar()

        self.navframe.channel_text = tk.StringVar(
            value=f"{self.navframe.parent.strip_frame.identifier.upper()}"
        )
        self.navframe.extend_text = tk.StringVar(
            value=f"{'REDUCE' if self.navframe.extend.get() else 'EXTEND'}"
        )
        self.navframe.info_text = tk.StringVar()

    def create_submix_button(self):
        self.navframe.submix_button = ttk.Checkbutton(
            self.navframe,
            text="SUBMIX",
            command=self.navframe.show_submix,
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'Submix.TButton'}",
            variable=self.navframe.submix,
        )
        self.navframe.submix_button.grid(column=0, row=0)
        if self.navframe.parent.kind.name != "potato":
            self.navframe.submix_button["state"] = "disabled"

    def create_channel_button(self):
        self.navframe.channel_button = ttk.Checkbutton(
            self.navframe,
            textvariable=self.navframe.channel_text,
            command=self.navframe.switch_channel,
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'Channel.TButton'}",
            variable=self.navframe.channel,
        )
        self.navframe.channel_button.grid(column=0, row=1, rowspan=1)

    def create_extend_button(self):
        self.navframe.extend_button = ttk.Checkbutton(
            self.navframe,
            textvariable=self.navframe.extend_text,
            command=self.navframe.extend_frame,
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'Extend.TButton'}",
            variable=self.navframe.extend,
        )
        self.navframe.extend_button.grid(column=0, row=2)

    def create_info_button(self):
        self.navframe.info_button = ttk.Checkbutton(
            self.navframe,
            textvariable=self.navframe.info_text,
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'Rec.TButton'}",
            variable=self.navframe.info,
        )
        self.navframe.info_button.grid(column=0, row=3)

    def grid_configure(self):
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.N, tk.S, tk.W, tk.E))
            for child in self.navframe.winfo_children()
            if isinstance(child, ttk.Checkbutton)
        ]
        if _configuration.themes_enabled:
            self.navframe.rowconfigure(1, minsize=_configuration.level_height)
        else:
            self.navframe.rowconfigure(1, minsize=_configuration.level_height + 10)

    def teardown(self):
        pass


class ChannelLabelFrameBuilder(AbstractBuilder):
    """Responsible for building channel labelframe widgets"""

    def __init__(self, labelframe, index, id):
        self.labelframe = labelframe
        self.index = index
        self.identifier = id
        self.using_theme = False

    def setup(self):
        """Create class variables for widgets"""
        self.labelframe.gain = tk.DoubleVar()
        self.labelframe.level = tk.DoubleVar(value=0)
        self.labelframe.mute = tk.BooleanVar()
        self.labelframe.conf = tk.BooleanVar()
        self.labelframe.gainlabel = tk.StringVar()

        """for gainlayers"""
        self.labelframe.on = tk.BooleanVar()

    def add_progressbar(self):
        """Adds a progress bar widget to a single label frame"""
        self.labelframe.pb = ttk.Progressbar(
            self.labelframe,
            maximum=100,
            orient="vertical",
            mode="determinate",
            variable=self.labelframe.level,
        )
        self.labelframe.pb.grid(column=0, row=0)

    def add_scale(self):
        """Adds a scale widget to a single label frame"""
        self.scale = ttk.Scale(
            self.labelframe,
            from_=12.0,
            to=-60.0,
            orient="vertical",
            variable=self.labelframe.gain,
            command=self.labelframe.scale_callback,
            length=_configuration.level_height,
        )
        self.scale.grid(column=1, row=0)
        self.scale.bind("<Double-Button-1>", self.labelframe.reset_gain)
        self.scale.bind("<Button-1>", self.labelframe.scale_press)
        self.scale.bind("<ButtonRelease-1>", self.labelframe.scale_release)
        self.scale.bind("<MouseWheel>", self.labelframe._on_mousewheel)

    def add_gain_label(self):
        self.labelframe.gain_label = ttk.Label(
            self.labelframe,
            textvariable=self.labelframe.gainlabel,
        )
        self.labelframe.gain_label.grid(column=0, row=1, columnspan=2)

    def add_mute_button(self):
        """Adds a mute button widget to a single label frame"""
        self.button_mute = ttk.Checkbutton(
            self.labelframe,
            text="MUTE",
            command=partial(self.labelframe.toggle_mute, "mute"),
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{self.identifier}Mute{self.index}.TButton'}",
            variable=self.labelframe.mute,
        )
        self.button_mute.grid(column=0, row=2, columnspan=2)

    def add_conf_button(self):
        self.button_conf = ttk.Checkbutton(
            self.labelframe,
            text="CONFIG",
            command=self.labelframe.open_config,
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{self.identifier}Conf{self.index}.TButton'}",
            variable=self.labelframe.conf,
        )
        self.button_conf.grid(column=0, row=3, columnspan=2)

    def add_on_button(self):
        self.button_on = ttk.Checkbutton(
            self.labelframe,
            text="ON",
            command=self.labelframe.set_on,
            style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{self.identifier}On{self.index}.TButton'}",
            variable=self.labelframe.on,
        )
        self.button_on.grid(column=0, row=2, columnspan=2)

    def teardown(self):
        self.labelframe.grid_remove()


class ChannelConfigFrameBuilder(AbstractBuilder):
    """Responsible for building channel configframe widgets"""

    def __init__(self, configframe):
        self.configframe = configframe
        (
            self.configframe.phys_in,
            self.configframe.virt_in,
        ) = self.configframe.parent.kind.ins
        (
            self.configframe.phys_out,
            self.configframe.virt_out,
        ) = self.configframe.parent.kind.outs

    def setup(self):
        "register configframe as observable"
        pass

    def teardown(self):
        """Deregister as observable, then destroy frame"""
        self.configframe.parent.subject_pdirty.remove(self.configframe)
        self.configframe.destroy()

    def grid_configure(self):
        [
            child.grid_configure(padx=1, pady=1, sticky=(tk.W, tk.E))
            for child in self.configframe.winfo_children()
            if isinstance(child, ttk.Checkbutton)
        ]
        self.configframe.grid(sticky=(tk.W))
        [
            self.configframe.columnconfigure(i, minsize=_configuration.level_width)
            for i in range(self.configframe.phys_out + self.configframe.virt_out)
        ]


class StripConfigFrameBuilder(ChannelConfigFrameBuilder):
    """Responsible for building channel configframe widgets"""

    def setup(self):
        if self.configframe.parent.kind.name == "basic":
            self.configframe.slider_params = ("audibility",)
            self.configframe.slider_vars = (tk.DoubleVar(),)
        else:
            self.configframe.slider_params = ("comp", "gate", "limit")
            self.configframe.slider_vars = [
                tk.DoubleVar() for _ in self.configframe.slider_params
            ]

        self.configframe.phys_out_params = [
            f"A{i+1}" for i in range(self.configframe.phys_out)
        ]
        self.configframe.phys_out_params_vars = [
            tk.BooleanVar() for _ in self.configframe.phys_out_params
        ]

        self.configframe.virt_out_params = [
            f"B{i+1}" for i in range(self.configframe.virt_out)
        ]
        self.configframe.virt_out_params_vars = [
            tk.BooleanVar() for _ in self.configframe.virt_out_params
        ]

        self.configframe.params = ("mono", "solo")
        self.configframe.param_vars = list(
            tk.BooleanVar() for _ in self.configframe.params
        )

        if self.configframe.parent.kind.name in ("banana", "potato"):
            if self.configframe.index == self.configframe.phys_in:
                self.configframe.params = list(
                    map(lambda x: x.replace("mono", "mc"), self.configframe.params)
                )
            if self.configframe.parent.kind.name == "banana":
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
                if (
                    self.configframe.index
                    == self.configframe.phys_in + self.configframe.virt_in - 1
                ):
                    self.configframe.params = list(
                        map(lambda x: x.replace("mono", "mc"), self.configframe.params)
                    )

    def create_comp_slider(self):
        comp_label = ttk.Label(self.configframe, text="Comp")
        comp_scale = ttk.Scale(
            self.configframe,
            from_=0.0,
            to=10.0,
            orient="horizontal",
            length=_configuration.level_width,
            variable=self.configframe.slider_vars[
                self.configframe.slider_params.index("comp")
            ],
            command=partial(self.configframe.scale_callback, "comp"),
        )
        comp_scale.bind(
            "<Double-Button-1>", partial(self.configframe.reset_scale, "comp", 0)
        )
        comp_scale.bind("<Button-1>", self.configframe.scale_press)
        comp_scale.bind("<ButtonRelease-1>", self.configframe.scale_release)
        comp_scale.bind("<Enter>", partial(self.configframe.scale_enter, "comp"))
        comp_scale.bind("<Leave>", self.configframe.scale_leave)

        comp_label.grid(column=0, row=0)
        comp_scale.grid(column=1, row=0)

    def create_gate_slider(self):
        gate_label = ttk.Label(self.configframe, text="Gate")
        gate_scale = ttk.Scale(
            self.configframe,
            from_=0.0,
            to=10.0,
            orient="horizontal",
            length=_configuration.level_width,
            variable=self.configframe.slider_vars[
                self.configframe.slider_params.index("gate")
            ],
            command=partial(self.configframe.scale_callback, "gate"),
        )
        gate_scale.bind(
            "<Double-Button-1>", partial(self.configframe.reset_scale, "gate", 0)
        )
        gate_scale.bind("<Button-1>", self.configframe.scale_press)
        gate_scale.bind("<ButtonRelease-1>", self.configframe.scale_release)
        gate_scale.bind("<Enter>", partial(self.configframe.scale_enter, "gate"))
        gate_scale.bind("<Leave>", self.configframe.scale_leave)

        gate_label.grid(column=2, row=0)
        gate_scale.grid(column=3, row=0)

    def create_limit_slider(self):
        limit_label = ttk.Label(self.configframe, text="Limit")
        limit_scale = ttk.Scale(
            self.configframe,
            from_=-40,
            to=12,
            orient="horizontal",
            length=_configuration.level_width,
            variable=self.configframe.slider_vars[
                self.configframe.slider_params.index("limit")
            ],
            command=partial(self.configframe.scale_callback, "limit"),
        )
        limit_scale.bind(
            "<Double-Button-1>", partial(self.configframe.reset_scale, "limit", 12)
        )
        limit_scale.bind("<Button-1>", self.configframe.scale_press)
        limit_scale.bind("<ButtonRelease-1>", self.configframe.scale_release)
        limit_scale.bind("<Enter>", partial(self.configframe.scale_enter, "limit"))
        limit_scale.bind("<Leave>", self.configframe.scale_leave)

        limit_label.grid(column=4, row=0)
        limit_scale.grid(column=5, row=0)

    def create_audibility_slider(self):
        aud_label = ttk.Label(self.configframe, text="Audibility")
        aud_scale = ttk.Scale(
            self.configframe,
            from_=0.0,
            to=10.0,
            orient="horizontal",
            length=_configuration.level_width,
            variable=self.configframe.slider_vars[
                self.configframe.slider_params.index("audibility")
            ],
            command=partial(self.configframe.scale_callback, "audibility"),
        )
        aud_scale.bind(
            "<Double-Button-1>", partial(self.configframe.reset_scale, "audibility", 0)
        )
        aud_scale.bind("<Button-1>", self.configframe.scale_press)
        aud_scale.bind("<ButtonRelease-1>", self.configframe.scale_release)
        aud_scale.bind("<Enter>", partial(self.configframe.scale_enter, "audibility"))
        aud_scale.bind("<Leave>", self.configframe.scale_leave)

        aud_label.grid(column=0, row=0)
        aud_scale.grid(column=1, row=0)

    def create_a_buttons(self):
        self.configframe.a_buttons = [
            ttk.Checkbutton(
                self.configframe,
                text=param,
                command=partial(self.configframe.toggle_a, param),
                style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{param}.TButton'}",
                variable=self.configframe.phys_out_params_vars[
                    self.configframe.phys_out_params.index(param)
                ],
            )
            for param in self.configframe.phys_out_params
        ]
        [
            button.grid(
                column=i,
                row=1,
            )
            for i, button in enumerate(self.configframe.a_buttons)
        ]

    def create_b_buttons(self):
        self.configframe.b_buttons = [
            ttk.Checkbutton(
                self.configframe,
                text=param,
                command=partial(self.configframe.toggle_b, param),
                style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{param}.TButton'}",
                variable=self.configframe.virt_out_params_vars[
                    self.configframe.virt_out_params.index(param)
                ],
            )
            for param in self.configframe.virt_out_params
        ]
        [
            button.grid(
                column=len(self.configframe.a_buttons) + i,
                row=1,
            )
            for i, button in enumerate(self.configframe.b_buttons)
        ]

    def create_param_buttons(self):
        param_buttons = [
            ttk.Checkbutton(
                self.configframe,
                text=param,
                command=partial(self.configframe.toggle_p, param),
                style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{param}.TButton'}",
                variable=self.configframe.param_vars[i],
            )
            for i, param in enumerate(self.configframe.params)
        ]
        [
            button.grid(
                column=i,
                row=2,
            )
            for i, button in enumerate(param_buttons)
        ]


class BusConfigFrameBuilder(ChannelConfigFrameBuilder):
    """Responsible for building channel configframe widgets"""

    def setup(self):
        # fmt: off
        self.configframe.bus_mode_map = {
            "normal": "Normal",
            "amix": "Mix Down A",
            "bmix": "Mix Down B",
            "repeat": "Stereo Repeat",
            "composite": "Composite",
            "tvmix": "Up Mix TV",
            "upmix21": "Up Mix 2.1",
            "upmix41": "Up Mix 4.1",
            "upmix61": "Up Mix 6.1",
            "centeronly": "Center Only",
            "lfeonly": "LFE Only",
            "rearonly": "Rear Only",
        }
        self.configframe.bus_modes = list(self.configframe.bus_mode_map.keys())
        # fmt: on
        self.configframe.params = ("mono", "eq", "eq_ab")
        self.configframe.param_vars = [tk.BooleanVar() for _ in self.configframe.params]
        self.configframe.bus_mode_label_text = tk.StringVar(
            value=self.configframe.bus_mode_map[self.configframe.current_bus_mode()]
        )

    def create_bus_mode_button(self):
        self.configframe.busmode_button = ttk.Button(
            self.configframe, textvariable=self.configframe.bus_mode_label_text
        )
        self.configframe.busmode_button.grid(
            column=0, row=0, columnspan=2, sticky=(tk.W)
        )
        self.configframe.busmode_button.bind(
            "<Button-1>", self.configframe.rotate_bus_modes_right
        )
        self.configframe.busmode_button.bind(
            "<Button-3>", self.configframe.rotate_bus_modes_left
        )

    def create_param_buttons(self):
        param_buttons = [
            ttk.Checkbutton(
                self.configframe,
                text=param,
                command=partial(self.configframe.toggle_p, param),
                style=f"{'Toggle.TButton' if _configuration.themes_enabled else f'{param}.TButton'}",
                variable=self.configframe.param_vars[i],
            )
            for i, param in enumerate(self.configframe.params)
        ]
        [
            button.grid(
                column=i,
                row=1,
            )
            for i, button in enumerate(param_buttons)
        ]
