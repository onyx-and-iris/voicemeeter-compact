from dataclasses import dataclass

from voicemeeterlib import kinds

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
    # bus assigned as current submix
    submixes: int = configuration["submixes"]["default"]

    # width of a single channel labelframe
    channel_width: int = configuration["channel"]["width"]
    # height of a single channel labelframe
    channel_height: int = configuration["channel"]["height"]
    # xpadding for a single channel labelframe
    channel_xpadding: int = configuration["channel"]["xpadding"]

    # do we grid the navigation frame?
    navigation_show: bool = configuration["navigation"]["show"]

    @property
    def config(self):
        if "configs" in configuration:
            return configuration["configs"]["config"]


@dataclass
class BaseValues(metaclass=SingletonMeta):
    # pause updates after releasing scale
    run_update: bool = False
    # are we dragging main window with mouse 1
    dragging: bool = False
    # a vban connection established
    vban_connected: bool = False


_base_values = BaseValues()
_configuration = Configurations()

_kinds = {kind.name: kind for kind in kinds.kinds_all}

_kinds_all = _kinds.values()


def kind_get(kind_id):
    return _kinds[kind_id]
