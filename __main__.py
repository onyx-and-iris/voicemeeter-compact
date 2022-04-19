import voicemeeter
import vmcompact


def main():
    with voicemeeter.remote(kind_id) as vmr:
        app = vmcompact.connect(kind_id, vmr)
        app.mainloop()


if __name__ == "__main__":
    kind_id = "banana"

    voicemeeter.launch(kind_id, hide=False)

    main()
