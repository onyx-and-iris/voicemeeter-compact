import voicemeeter
import vmcompact


if __name__ == "__main__":
    kind_id = "banana"

    voicemeeter.launch(kind_id, hide=False)

    with voicemeeter.remote(kind_id) as vmr:
        app = vmcompact.connect(kind_id, vmr)
        app.mainloop()
