import voicemeeterlib

import vmcompact


def run():
    KIND_ID = 'banana'

    with voicemeeterlib.api(KIND_ID) as vmr:
        app = vmcompact.connect(KIND_ID, vmr)
        app.mainloop()
