from dataclasses import dataclass
from voicemeeter import kinds


@dataclass
class BaseValues:
    level_height: int = 100
    level_width: int = 80

    # are we dragging a scale with mouse 1
    in_scale_button_1: bool = False
    # are we dragging main window with mouse 1
    dragging: bool = False
    # direction the gui extends
    extends_horizontal: bool = True
    # a vban connection established
    vban_connected: bool = False
    # are themes enabled
    themes_enabled: bool = True
    # are we using a theme
    using_theme: bool = False
    # bus assigned as current submix
    submixes: int = 0


_base_vals = BaseValues()


_kinds = {kind.id: kind for kind in kinds.all}

_kinds_all = _kinds.values()


def kind_get(kind_id):
    return _kinds[kind_id]
