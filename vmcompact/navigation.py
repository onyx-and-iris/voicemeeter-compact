import tkinter as tk
from tkinter import ttk

from . import builders
from .data import _configuration
from .gainlayer import SubMixFrame


class Navigation(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=3, padx=(0, 2), pady=(5, 5), sticky=(tk.W, tk.E))
        self.styletable = self.parent.styletable

        self.builder = builders.NavigationFrameBuilder(self)
        self.builder.setup()
        self.builder.create_submix_button()
        self.builder.create_channel_button()
        self.builder.create_extend_button()
        self.builder.create_info_button()
        self.builder.grid_configure()

        self.mainframebuilder = builders.MainFrameBuilder(self.parent)

    def show_submix(self):
        if self.submix.get():
            self.parent.submix_frame = SubMixFrame(self.parent)
        else:
            if _configuration.extends_horizontal:
                self.parent.submix_frame.teardown()
                if self.parent.bus_frame:
                    self.parent.bus_frame.grid()
                else:
                    self.parent.columnconfigure(1, weight=0)
            else:
                self.parent.submix_frame.teardown()
                if self.parent.bus_frame:
                    self.parent.bus_frame.grid()
                else:
                    self.parent.rowconfigure(2, weight=0, minsize=0)

        if not _configuration.themes_enabled:
            self.styletable.configure(
                f"Submix.TButton",
                background=f'{"purple" if self.submix.get() else "white"}',
            )

    def switch_channel(self):
        if self.channel_text.get() == "STRIP":
            self.mainframebuilder.create_channelframe("bus")
            self.parent.strip_frame.teardown()
        else:
            self.mainframebuilder.create_channelframe("strip")
            self.parent.bus_frame.teardown()

        self.extend_button["state"] = (
            "disabled" if self.channel_text.get() == "STRIP" else "normal"
        )
        [frame.teardown() for frame in self.parent.configframes]
        self.channel_text.set("BUS" if self.channel_text.get() == "STRIP" else "STRIP")

    def extend_frame(self):
        _configuration.extended = self.extend.get()
        if self.extend.get():
            self.channel_button["state"] = "disabled"
            self.mainframebuilder.create_channelframe("bus")
        else:
            [
                frame.teardown()
                for frame in self.parent.configframes
                if "!busconfig" in str(frame)
            ]
            self.parent.bus_frame.teardown()
            self.parent.bus_frame = None
            self.channel_button["state"] = "normal"

            if self.parent.submix_frame:
                self.parent.submix_frame.teardown()
                self.submix.set(False)
                if not _configuration.themes_enabled:
                    self.styletable.configure(
                        f"Submix.TButton",
                        background=f'{"purple" if self.submix.get() else "white"}',
                    )

            self.extend_text.set("REDUCE" if self.extend.get() else "EXTEND")
