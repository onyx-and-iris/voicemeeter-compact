from dataclasses import dataclass
from voicemeeter import kinds

from .configurations import get_configuration

configuration = get_configuration("app")


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass
class Configurations(metaclass=SingletonMeta):
    # width of a single labelframe
    level_width: int = 75
    # height of a single labelframe
    level_height: int = 100

    # is the gui extended
    extended: bool = configuration["extends"]["extended"]
    # direction the gui extends
    extends_horizontal: bool = configuration["extends"]["extends_horizontal"]
    # are themes enabled
    themes_enabled: bool = configuration["theme"]["enabled"]
    # light or dark
    theme_mode: str = configuration["theme"]["mode"]
    # size of mousewheel scroll step
    mwscroll_step: int = configuration["mwscroll_step"]["size"]

    @property
    def profile(self):
        if "profiles" in configuration:
            return configuration["profiles"]["profile"]


@dataclass
class BaseValues(metaclass=SingletonMeta):
    # are we dragging a scale with mouse 1
    in_scale_button_1: bool = False
    # are we dragging main window with mouse 1
    dragging: bool = False
    # a vban connection established
    vban_connected: bool = False
    # bus assigned as current submix
    submixes: int = 0
    # pdirty delay
    pdelay: int = 5
    # ldirty delay
    ldelay: int = 50
    # size of strip level array for a kind
    strip_level_array_size: int = None
    # size of bus level array for a kind
    bus_level_array_size: int = None


_base_values = BaseValues()
_configuration = Configurations()

_kinds = {kind.id: kind for kind in kinds.all}

_kinds_all = _kinds.values()


def kind_get(kind_id):
    return _kinds[kind_id]
