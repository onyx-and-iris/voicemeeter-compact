import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
import webbrowser
import sv_ttk

import vbancmd

from .configurations import configuration
from .data import _base_vals, kind_get


class Menus(tk.Menu):
    def __init__(self, parent, vmr):
        super().__init__()
        self._parent = parent
        self._vmr = vmr
        if self.configuration_vban is not None:
            self.vban_conns = [None for i, _ in enumerate(self.configuration_vban)]
        self._is_topmost = tk.BooleanVar()
        self._selected_bus = list(tk.BooleanVar() for _ in range(8))

        # voicemeeter menu
        self.menu_voicemeeter = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.menu_voicemeeter, label="Voicemeeter")
        self.menu_voicemeeter.add_checkbutton(
            label="Always On Top",
            onvalue=1,
            offvalue=0,
            variable=self._is_topmost,
            command=self.always_on_top,
        )
        self.menu_voicemeeter.add_separator()
        self.menu_voicemeeter.add_command(
            label="Show",
            underline=0,
            command=partial(self.action_invoke_voicemeeter, "show"),
        )
        self.menu_voicemeeter.add_command(
            label="Hide",
            underline=0,
            command=partial(self.action_invoke_voicemeeter, "hide"),
        )
        self.menu_voicemeeter.add_command(
            label="Restart",
            underline=0,
            command=partial(self.action_invoke_voicemeeter, "restart"),
        )
        self.menu_voicemeeter.add_command(
            label="Shutdown",
            underline=0,
            command=partial(self.action_invoke_voicemeeter, "shutdown"),
        )
        self.menu_voicemeeter.add_separator()
        self.menu_lock = tk.Menu(self.menu_voicemeeter, tearoff=0)
        self.menu_voicemeeter.add_cascade(
            menu=self.menu_lock, label="GUI Lock", underline=0
        )
        self.menu_lock.add_command(
            label="Lock", command=partial(self.action_set_voicemeeter, "lock")
        )
        self.menu_lock.add_command(
            label="Unlock", command=partial(self.action_set_voicemeeter, "lock", False)
        )

        # profiles menu
        menu_profiles = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=menu_profiles, label="Profiles")
        self.menu_profiles_load = tk.Menu(menu_profiles, tearoff=0)
        menu_profiles.add_cascade(menu=self.menu_profiles_load, label="Load profile")
        defaults = {"base", "blank"}
        if len(vmr.profiles) > len(defaults) and all(
            key in vmr.profiles for key in defaults
        ):
            [
                self.menu_profiles_load.add_command(
                    label=profile, command=partial(self.load_profile, profile)
                )
                for profile in vmr.profiles.keys()
                if profile not in defaults
            ]
        else:
            menu_profiles.entryconfig(0, state="disabled")
        menu_profiles.add_separator()
        menu_profiles.add_command(label="Reset to defaults", command=self.load_defaults)

        # vban connect menu
        self.menu_vban = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.menu_vban, label="VBAN")
        if self.configuration_vban:
            for i, _ in enumerate(self.configuration_vban):
                setattr(self, f"menu_vban_{i+1}", tk.Menu(self.menu_vban, tearoff=0))
                target_menu = getattr(self, f"menu_vban_{i+1}")
                self.menu_vban.add_cascade(
                    menu=target_menu, label=f"VBAN Connect #{i+1}", underline=0
                )
                target_menu.add_command(
                    label="Connect", command=partial(self.vban_connect, i)
                )
                target_menu.add_command(
                    label="Disconnect", command=partial(self.vban_disconnect, i)
                )
                target_menu.entryconfig(1, state="disabled")
        else:
            self.entryconfig(3, state="disabled")

        # extends menu
        self.menu_extends = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.menu_extends, label="Extends")
        self.menu_extends.add_command(
            label="horizontal",
            underline=0,
            command=partial(self.switch_orientation, extends_horizontal=True),
        )
        self.menu_extends.add_command(
            label="vertical",
            underline=0,
            command=partial(self.switch_orientation, extends_horizontal=False),
        )
        self.menu_extends.entryconfig(
            0 if _base_vals.extends_horizontal else 1, state="disabled"
        )

        # submixes menu
        # here we build menu regardless of kind but disable if not Potato
        buses = tuple(f"A{i+1}" for i in range(5)) + tuple(f"B{i+1}" for i in range(3))
        self.menu_submixes = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.menu_submixes, label="Submixes")
        [
            self.menu_submixes.add_checkbutton(
                label=f"Bus {buses[i]}",
                underline=0,
                onvalue=1,
                offvalue=0,
                variable=self._selected_bus[i],
                command=partial(self.set_submix, i),
            )
            for i in range(8)
        ]
        self._selected_bus[_base_vals.submixes].set(True)
        if self._parent.kind.name != "Potato":
            self.entryconfig(5, state="disabled")

        # themes menu
        self.menu_themes = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.menu_themes, label="Themes")
        self.menu_themes.add_command(
            label="light", command=partial(self.load_theme, "light")
        )
        self.menu_themes.add_command(
            label="dark", command=partial(self.load_theme, "dark")
        )
        self.menu_themes.entryconfig(
            0 if self.configuration_app["theme"]["mode"] == "light" else 1,
            state="disabled",
        )
        if not _base_vals.themes_enabled:
            self.entryconfig(6, state="disabled")

        # Help menu
        self.menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.menu_help, label="Help")
        self.menu_help.add_command(
            label="Voicemeeter Site",
            command=self.documentation,
        )
        self.menu_help.add_command(
            label="Source Code",
            command=self.github,
        )
        self.menu_help.add_command(
            label="App Creator",
            command=self.onyxandiris,
        )

    @property
    def target(self):
        """use the correct interface"""
        return self._parent.target

    @property
    def configuration_app(self):
        return configuration["app"]

    @configuration_app.setter
    def configuration_app(self, val):
        self.configuration_app = val

    @property
    def configuration_vban(self):
        if "vban" in configuration:
            return configuration["vban"]

    def action_invoke_voicemeeter(self, cmd):
        getattr(self.target.command, cmd)()

    def action_set_voicemeeter(self, cmd, val=True):
        setattr(self.target.command, cmd, val)

    def load_profile(self, profile):
        self.target.apply_profile(profile)

    def load_defaults(self):
        resp = messagebox.askyesno(
            message="Are you sure you want to Reset values to defaults?\nPhysical strips B1, Virtual strips A1\nMono, Solo, Mute, EQ all OFF"
        )
        if resp:
            self.target.apply_profile("base")

    def always_on_top(self):
        self._parent.attributes("-topmost", self._is_topmost.get())
        self._parent.update()

    def switch_orientation(self, extends_horizontal: bool = True, *args):
        _base_vals.extends_horizontal = extends_horizontal
        if extends_horizontal:
            self.menu_extends.entryconfig(0, state="disabled")
            self.menu_extends.entryconfig(1, state="normal")
        else:
            self.menu_extends.entryconfig(1, state="disabled")
            self.menu_extends.entryconfig(0, state="normal")

    def set_submix(self, i):
        if _base_vals.submixes != i:
            _base_vals.submixes = i
            if self._parent.submix_frame is not None:
                self._parent.submix_frame.destroy()
                self._parent.nav_frame.show_submix()
            for j, var in enumerate(self._selected_bus):
                var.set(True if i == j else False)

    def load_theme(self, theme):
        sv_ttk.set_theme(theme)
        self.configuration_app["theme"]["mode"] = theme
        self.menu_themes.entryconfig(
            0,
            state=f"{'disabled' if theme == 'light' else 'normal'}",
        )
        self.menu_themes.entryconfig(
            1,
            state=f"{'disabled' if theme == 'dark' else 'normal'}",
        )
        [
            menu.config(bg=f"{'black' if theme == 'dark' else 'white'}")
            for menu in self.winfo_children()
            if isinstance(menu, tk.Menu)
        ]
        self.menu_lock.config(bg=f"{'black' if theme == 'dark' else 'white'}")
        self.menu_profiles_load.config(bg=f"{'black' if theme == 'dark' else 'white'}")
        [
            menu.config(bg=f"{'black' if theme == 'dark' else 'white'}")
            for menu in self.menu_vban.winfo_children()
            if isinstance(menu, tk.Menu)
        ]

    def vban_connect(self, i):
        [
            self.menu_vban.entryconfig(j, state="disabled")
            for j, _ in enumerate(self.menu_vban.winfo_children())
            if j != i
        ]

        opts = {}
        opts |= self.configuration_vban[f"connection-{i+1}"]
        kind_id = opts.pop("kind")
        self.vban_conns[i] = vbancmd.connect(kind_id, **opts)
        # login to vban interface
        self.vban_conns[i].login()
        # destroy the current App frames
        self._parent._destroy_top_level_frames()
        _base_vals.vban_connected = True
        # build new app frames according to a kind
        kind = kind_get(kind_id)
        self._parent._make_app(kind, self.vban_conns[i])
        target_menu = getattr(self, f"menu_vban_{i+1}")
        target_menu.entryconfig(0, state="disabled")
        target_menu.entryconfig(1, state="normal")
        self.entryconfig(
            5, state=f"{'normal' if kind.name == 'Potato' else 'disabled'}"
        )

    def vban_disconnect(self, i):
        # destroy the current App frames
        self._parent._destroy_top_level_frames()
        _base_vals.vban_connected = False
        # logout of vban interface
        i_to_close = self.vban_conns[i]
        self.vban_conns[i] = None
        i_to_close.logout()
        # build new app frames according to a kind
        kind = kind_get(self._vmr.type)
        self._parent._make_app(kind, None)
        target_menu = getattr(self, f"menu_vban_{i+1}")
        target_menu.entryconfig(0, state="normal")
        target_menu.entryconfig(1, state="disabled")
        self.entryconfig(
            5, state=f"{'normal' if kind.name == 'Potato' else 'disabled'}"
        )

        self.after(15000, self.enable_vban_menus)

    def enable_vban_menus(self):
        [
            self.menu_vban.entryconfig(j, state="normal")
            for j, _ in enumerate(self.menu_vban.winfo_children())
        ]

    def documentation(self):
        webbrowser.open_new(r"https://voicemeeter.com/")

    def github(self):
        webbrowser.open_new(r"https://github.com/onyx-and-iris/voicemeeter-compact")

    def onyxandiris(self):
        webbrowser.open_new(r"https://onyxandiris.online")
