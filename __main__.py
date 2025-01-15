import voicemeeterlib

import vmcompact


def main():
    KIND_ID = 'banana'

    with voicemeeterlib.api(KIND_ID) as vmr:
        app = vmcompact.connect(KIND_ID, vmr)
        app.mainloop()


if __name__ == '__main__':
    main()
