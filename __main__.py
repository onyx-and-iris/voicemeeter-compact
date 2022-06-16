import voicemeeterlib

import vmcompact


def main():
    with voicemeeterlib.api(kind_id) as vmr:
        app = vmcompact.connect(kind_id, vmr)
        app.mainloop()


if __name__ == "__main__":
    kind_id = "banana"

    main()
