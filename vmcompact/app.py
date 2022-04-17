import tkinter as tk
from tkinter import ttk
from typing import NamedTuple
from functools import partial
from pathlib import Path

from .errors import VMCompactErrors
from .data import _base_vals, _kinds_all
from .channels import ChannelFrame
from .navigation import Navigation
from .menu import Menus
from .banner import Banner
from .configurations import configuration


class App(tk.Tk):
    """Topmost Level of App"""

    @classmethod
    def make(cls, kind: NamedTuple):
        """
        Factory function for App

        Returns an App class of a kind
        """
        APP_cls = type(
            f"Voicemeeter{kind.name}.Compact",
            (cls,),
            {
                "kind": kind,
            },
        )
        return APP_cls

    def __init__(self, vmr):
        super().__init__()
        defaults = {
            "theme": {
                "enabled": True,
                "mode": "light",
            },
            "extends": {
                "extended": True,
                "extends_horizontal": True,
            },
            "channel": {
                "width": 80,
                "height": 130,
            },
            "submixes": {
                "default": 0,
            },
        }
        if configuration:
            self.configuration = defaults | self.configuration
        else:
            configuration["app"] = defaults
        _base_vals.themes_enabled = self.configuration["theme"]["enabled"]
        _base_vals.extends_horizontal = self.configuration["extends"][
            "extends_horizontal"
        ]
        _base_vals.submixes = self.configuration["submixes"]["default"]
        # create menus
        self.menus = Menus(self, vmr)
        self.styletable = ttk.Style()
        self._vmr = vmr

        # start watchers, initialize level arrays
        self.upd_pdirty()
        self.strip_levels = self.target.strip_levels
        self.bus_levels = self.target.bus_levels
        self.watch_levels()

        self.resizable(False, False)
        if _base_vals.themes_enabled:
            self.apply_theme()
        self._make_app(self.kind)

        self.drag_id = ""
        self.bind("<Configure>", self.dragging)

        self.iconbitmap(Path(__file__).parent.resolve() / "img" / "cat.ico")

    @property
    def target(self):
        """returns the current interface"""
        return self._vban if _base_vals.vban_connected else self._vmr

    @property
    def pdirty(self):
        return self._pdirty

    @pdirty.setter
    def pdirty(self, val):
        self._pdirty = val

    @property
    def ldirty(self):
        return self._ldirty

    @ldirty.setter
    def ldirty(self, val):
        self._ldirty = val

    @property
    def configuration(self):
        return configuration["app"]

    @configuration.setter
    def configuration(self, val):
        self.configuration["app"] = val

    @property
    def configframes(self):
        """returns a tuple of current config frame addresses"""
        return tuple(
            frame
            for frame in self.winfo_children()
            if isinstance(frame, ttk.Frame)
            and "!stripconfig" in str(frame)
            or "!busconfig" in str(frame)
        )

    def apply_theme(self):
        _base_vals.using_theme = True
        self.tk.call(
            "source",
            Path(__file__).parent.resolve() / "sun-valley-theme/sun-valley.tcl",
        )
        self.tk.call("set_theme", self.configuration["theme"]["mode"])

    def _make_app(self, kind, vban=None):
        self.title(
            f'Voicemeeter{kind.name}.Compact [{"Local" if not vban else "Network"} Connection]'
        )
        self._vban = vban
        self.kind = kind
        self.strip_levels = self.target.strip_levels
        self.bus_levels = self.target.bus_levels

        self._make_top_level_frames()

    def _make_top_level_frames(self):
        # initialize bus frame variable
        self.bus_frame = None
        # channel_frame, left aligned
        self.channel_frame = ChannelFrame.make_strips(self)
        self.channel_frame.grid(row=0, column=0, sticky=(tk.W))
        # separator
        self.sep = ttk.Separator(self, orient="vertical")
        self.sep.grid(row=0, column=1, sticky=(tk.S, tk.N))
        self.columnconfigure(1, minsize=15)

        # navigation frame
        self.nav_frame = Navigation(self)
        self.nav_frame.grid(row=0, column=3)

        if self.configuration["extends"]["extended"]:
            self.nav_frame.extend.set(True)
            self.nav_frame.extend_frame()

        self.banner = Banner(self)
        self.banner.grid(row=4, column=0, columnspan=3)

    def _destroy_top_level_frames(self):
        [
            frame.destroy()
            for frame in self.winfo_children()
            if isinstance(frame, ttk.Frame)
        ]

    def upd_pdirty(self):
        self.after(1, self.upd_pdirty_step)

    def upd_pdirty_step(self):
        self.pdirty = self.target.pdirty
        self.after(_base_vals.pdelay, self.upd_pdirty_step)

    def watch_levels(self):
        self.after(1, self.watch_levels_step)

    def watch_levels_step(self):
        """Continuously fetch level arrays, only update if ldirty"""
        _strip_levels = self.target.strip_levels
        _bus_levels = self.target.bus_levels
        self.comp_strip = [not a == b for a, b in zip(self.strip_levels, _strip_levels)]
        self.comp_bus = [not a == b for a, b in zip(self.bus_levels, _bus_levels)]

        self.ldirty = any(any(l) for l in (self.comp_strip, self.comp_bus))
        if self.ldirty:
            self.strip_levels = _strip_levels
            self.bus_levels = _bus_levels
        self.after(_base_vals.ldelay, self.watch_levels_step)

    def dragging(self, event, *args):
        if event.widget is self:
            if self.drag_id == "":
                _base_vals.in_scale_button_1 = True
                _base_vals.dragging = True
            else:
                self.after_cancel(self.drag_id)
            self.drag_id = self.after(100, self.stop_drag)

    def stop_drag(self):
        _base_vals.dragging = False
        _base_vals.in_scale_button_1 = False
        self.drag_id = ""


_apps = {kind.id: App.make(kind) for kind in _kinds_all}


def connect(kind_id: str, vmr) -> App:
    """return App of the kind requested"""
    try:
        VMMIN_cls = _apps[kind_id]
        return VMMIN_cls(vmr)
    except KeyError:
        raise VMCompactErrors(f"Invalid kind: {kind_id}")
