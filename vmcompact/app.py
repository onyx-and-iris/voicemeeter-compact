import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import NamedTuple

from .builders import MainFrameBuilder
from .data import _base_values, _configuration, _kinds_all
from .errors import VMCompactErrors
from .menu import Menus
from .subject import Subject


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

        self._vmr = vmr
        self._vmr.event.add("ldirty")
        icon_path = Path(__file__).parent.resolve() / "img" / "cat.ico"
        if icon_path.is_file():
            self.iconbitmap(str(icon_path))
        self.minsize(275, False)
        self.subject = Subject()
        self["menu"] = Menus(self, vmr)
        self.styletable = ttk.Style()
        if _configuration.config:
            vmr.apply_config(_configuration.config)

        self.build_app()

        self.drag_id = ""
        self.bind("<Configure>", self.dragging)

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

        # register app as observer
        self.target.subject.add(self)

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

    def on_update(self, subject):
        """called whenever notified of update"""

        if subject == "pdirty" and _base_values.run_update:
            self.after(1, self.subject.notify, "pdirty")
        elif subject == "ldirty" and not _base_values.dragging:
            self.after(1, self.subject.notify, "ldirty")

    def _destroy_top_level_frames(self):
        """
        Clear observables.

        Deregister app as observer.

        Destroy all top level frames.
        """
        self.target.subject.remove(self)
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


_apps = {kind.name: App.make(kind) for kind in _kinds_all}


def connect(kind_id: str, vmr) -> App:
    """return App of the kind requested"""

    try:
        VMMIN_cls = _apps[kind_id]
    except KeyError:
        raise VMCompactErrors(f"Invalid kind: {kind_id}")
    return VMMIN_cls(vmr)
