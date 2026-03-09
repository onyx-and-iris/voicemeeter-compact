def get_busmode_fullnames(kind) -> dict:
    if kind.name == 'basic':
        return {
            'normal': 'Normal',
            'amix': 'Mix Down A',
            'repeat': 'Stereo Repeat',
            'composite': 'Composite',
        }
    return {
        'normal': 'Normal',
        'amix': 'Mix Down A',
        'bmix': 'Mix Down B',
        'repeat': 'Stereo Repeat',
        'composite': 'Composite',
        'tvmix': 'Up Mix TV',
        'upmix21': 'Up Mix 2.1',
        'upmix41': 'Up Mix 4.1',
        'upmix61': 'Up Mix 6.1',
        'centeronly': 'Center Only',
        'lfeonly': 'LFE Only',
        'rearonly': 'Rear Only',
    }


def get_busmode_fullnames_reversed(kind) -> dict:
    return {v: k for k, v in get_busmode_fullnames(kind).items()}


def get_busmode_shortnames(kind) -> list:
    return list(get_busmode_fullnames(kind).keys())


def get_busmono_modes() -> list:
    return ['Mono: off', 'Mono: on', 'Stereo Reverse']
