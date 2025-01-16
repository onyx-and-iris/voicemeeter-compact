import voicemeeterlib

import vmcompact


def run():
    KIND_ID = 'potato'

    with voicemeeterlib.api(KIND_ID) as vmr:
        app = vmcompact.connect(KIND_ID, vmr)
        app.mainloop()
