import tkinter as tk
from tkinter import ttk
from typing import NamedTuple
from pathlib import Path

from .errors import VMCompactErrors
from .data import _kinds_all, _configuration, _base_values
from .subject import Subject
from .builders import MainFrameBuilder
from .menu import Menus


class App(tk.Tk):
    """App mainframe"""

    @classmethod
    def make(cls, kind: NamedTuple):
        """
        Factory function for App.

        Returns an App class of a kind.
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

        self._vmr = vmr
        icon_path = Path(__file__).parent.resolve() / "img" / "cat.ico"
        if icon_path.is_file():
            self.iconbitmap(str(icon_path))
        self.minsize(275, False)
        self.subject_pdirty = Subject()
        self.subject_ldirty = Subject()
        self.strip_levels = None
        self.bus_levels = None
        self["menu"] = Menus(self, vmr)
        self.styletable = ttk.Style()
        if _configuration.profile:
            vmr.apply_profile(_configuration.profile)

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
        if self.kind.name == "Potato":
            self.builder.create_banner()

    def on_update(self, subject, data):
        """called whenever notified of update"""

        if not _base_values.in_scale_button_1:
            if subject == "pdirty":
                self.after(1, self.notify_pdirty)
            elif subject == "ldirty" and not _base_values.dragging:
                (
                    self.strip_levels,
                    self.strip_comp,
                    self.bus_levels,
                    self.bus_comp,
                ) = data
                self.after(1, self.notify_ldirty)

    def notify_pdirty(self):
        self.subject_pdirty.notify()

    def notify_ldirty(self):
        self.subject_ldirty.notify()

    def _destroy_top_level_frames(self):
        """
        Clear observables.

        Deregister app as observer.

        Destroy all top level frames.
        """
        self.target.subject.remove(self)
        self.subject_pdirty.clear()
        self.subject_ldirty.clear()
        [
            frame.destroy()
            for frame in self.winfo_children()
            if isinstance(frame, ttk.Frame)
        ]

    def dragging(self, event, *args):
        if event.widget is self:
            if self.drag_id == "":
                _base_values.in_scale_button_1 = True
                _base_values.dragging = True
            else:
                self.after_cancel(self.drag_id)
            self.drag_id = self.after(100, self.stop_drag)

    def stop_drag(self):
        _base_values.dragging = False
        _base_values.in_scale_button_1 = False
        self.drag_id = ""


_apps = {kind.id: App.make(kind) for kind in _kinds_all}


def connect(kind_id: str, vmr) -> App:
    """return App of the kind requested"""

    try:
        VMMIN_cls = _apps[kind_id]
        return VMMIN_cls(vmr)
    except KeyError:
        raise VMCompactErrors(f"Invalid kind: {kind_id}")
