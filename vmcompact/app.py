import logging
import tkinter as tk
from functools import cached_property
from pathlib import Path
from tkinter import ttk
from typing import NamedTuple

from .builders import MainFrameBuilder
from .configurations import loader
from .data import _base_values, _configuration, _kinds_all
from .errors import VMCompactError
from .menu import Menus
from .subject import Subject

logger = logging.getLogger(__name__)


class App(tk.Tk):
    """App mainframe"""

    @classmethod
    def make(cls, kind: NamedTuple):
        """
        Factory function for App.

        Returns an App class of a kind.
        """

        APP_cls = type(
            f"Voicemeeter{kind}.Compact",
            (cls,),
            {
                "kind": kind,
            },
        )
        return APP_cls

    def __init__(self, vmr):
        super().__init__()
        self.logger = logger.getChild(self.__class__.__name__)
        self._vmr = vmr
        self._vmr.event.add(["pdirty", "ldirty"])
        self.after(12000 if self._vmr.gui.launched_by_api else 1, self.start_updates)
        self._vmr.init_thread()
        icon_path = Path(__file__).parent.resolve() / "img" / "cat.ico"
        if icon_path.is_file():
            self.iconbitmap(str(icon_path))
        self.minsize(275, False)
        self.subject = Subject()
        self._configs = None
        self["menu"] = Menus(self, vmr)
        self.styletable = ttk.Style()
        if _configuration.config:
            vmr.apply_config(_configuration.config)

        self.build_app()

        self.drag_id = ""
        self.bind("<Configure>", self.dragging)

    def start_updates(self):
        self.logger.debug("updates started")
        _base_values.run_update = True
        if self._vmr.gui.launched_by_api:
            self.on_pdirty()

    def __str__(self):
        return f"{type(self).__name__}App"

    @property
    def target(self):
        """returns the current interface"""

        return self._vban if _base_values.vban_connected else self._vmr

    @property
    def configframes(self):
        """returns the current configframes"""

        return (
            frame
            for frame in self.winfo_children()
            if isinstance(frame, ttk.Frame)
            and "!stripconfig" in str(frame)
            or "!busconfig" in str(frame)
        )

    def build_app(self, kind=None, vban=None):
        """builds the app frames according to a kind"""
        self._vban = vban
        if kind:
            self.kind = kind

        # register event callbacks
        self.target.subject.add([self.on_pdirty, self.on_ldirty])

        self.bus_frame = None
        self.submix_frame = None
        self.builder = MainFrameBuilder(self)
        self.builder.setup()
        self.builder.create_channelframe("strip")
        self.builder.create_separator()
        self.builder.create_navframe()
        if _configuration.extended:
            self.nav_frame.extend.set(True)
            self.nav_frame.extend_frame()
        if self.kind.name == "potato":
            self.builder.create_banner()

    def on_pdirty(self):
        if _base_values.run_update:
            self.after(1, self.subject.notify, "pdirty")

    def on_ldirty(self):
        if not _base_values.dragging:
            self.after(1, self.subject.notify, "ldirty")

    def _destroy_top_level_frames(self):
        """
        Clear observables.

        Deregister app as observer.

        Destroy all top level frames.
        """
        self.target.subject.remove([self.on_pdirty, self.on_ldirty])
        self.subject.clear()
        [
            frame.destroy()
            for frame in self.winfo_children()
            if isinstance(frame, ttk.Frame)
        ]

    def dragging(self, event, *args):
        if event.widget is self:
            if self.drag_id == "":
                _base_values.dragging = True
            else:
                self.after_cancel(self.drag_id)
            self.drag_id = self.after(100, self.stop_drag)

    def stop_drag(self):
        self.drag_id = ""
        _base_values.dragging = False

    @cached_property
    def userconfigs(self):
        self._configs = loader(self.kind.name, self.target)
        return self._configs


_apps = {kind.name: App.make(kind) for kind in _kinds_all}


def connect(kind_id: str, vmr) -> App:
    """return App of the kind requested"""

    try:
        VMMIN_cls = _apps[kind_id]
    except KeyError:
        raise VMCompactError(f"Invalid kind: {kind_id}")
    return VMMIN_cls(vmr)
