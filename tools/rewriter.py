import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("vm-compact-rewriter")

PACKAGE_DIR = Path(__file__).parent.parent / "vmcompact"

SRC_DIR = Path(__file__).parent / "src"


def write_outs(output, outs: tuple):
    for out in outs:
        output.write(out)


def rewrite_app():
    app_logger = logger.getChild("app")
    app_logger.info("rewriting app.py")
    infile = Path(SRC_DIR) / "app.bk"
    outfile = Path(PACKAGE_DIR) / "app.py"
    with open(infile, "r") as input:
        with open(outfile, "w") as output:
            for line in input:
                match line:
                    # App init()
                    case "    def __init__(self, vmr):\n":
                        output.write("    def __init__(self, vmr, theme):\n")
                    case "        self._vmr = vmr\n":
                        write_outs(
                            output,
                            (
                                "        self._vmr = vmr\n",
                                "        self._theme = theme\n",
                                '        tcldir = Path.cwd() / "theme"\n',
                                "        if not tcldir.is_dir():\n",
                                '            tcldir = Path.cwd() / "builds" / "theme"\n',
                                '        self.tk.call("source", tcldir.resolve() / f"forest-{self._theme}.tcl")\n',
                            ),
                        )
                    # def connect()
                    case "def connect(kind_id: str, vmr) -> App:\n":
                        output.write(
                            'def connect(kind_id: str, vmr, theme="light") -> App:\n'
                        )
                    case "    return VMMIN_cls(vmr)\n":
                        output.write("    return VMMIN_cls(vmr, theme)\n")
                    case _:
                        output.write(line)


def rewrite_builders():
    builders_logger = logger.getChild("builders")
    builders_logger.info("rewriting builders.py")
    infile = Path(SRC_DIR) / "builders.bk"
    outfile = Path(PACKAGE_DIR) / "builders.py"
    with open(infile, "r") as input:
        with open(outfile, "w") as output:
            ignore_next_lines = 0

            for line in input:
                if ignore_next_lines > 0:
                    builders_logger.info(f"ignoring: {line}")
                    ignore_next_lines -= 1
                    continue

                match line:
                    # loading themes
                    case "import sv_ttk\n":
                        output.write("#import sv_ttk\n")
                    case "        self.app.resizable(False, False)\n":
                        write_outs(
                            output,
                            (
                                "        self.app.resizable(False, False)\n"
                                "        if _configuration.themes_enabled:\n",
                                '            ttk.Style().theme_use(f"forest-{self.app._theme}")\n',
                                '            self.logger.info(f"Forest Theme applied")\n',
                            ),
                        )
                        ignore_next_lines = 6
                    # setting navframe button widths
                    case "            variable=self.navframe.submix,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.navframe.submix,\n"
                                "            width=8,\n",
                            ),
                        )
                    case "            variable=self.navframe.channel,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.navframe.channel,\n"
                                "            width=8,\n",
                            ),
                        )
                    case "            variable=self.navframe.extend,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.navframe.extend,\n"
                                "            width=8,\n",
                            ),
                        )
                    case "            variable=self.navframe.info,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.navframe.info,\n"
                                "            width=8,\n",
                            ),
                        )
                    # set channelframe button widths
                    case "            variable=self.labelframe.mute,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.labelframe.mute,\n"
                                "            width=7,\n",
                            ),
                        )
                    case "            variable=self.labelframe.conf,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.labelframe.conf,\n"
                                "            width=7,\n",
                            ),
                        )
                    case "            variable=self.labelframe.on,\n":
                        write_outs(
                            output,
                            (
                                "            variable=self.labelframe.on,\n"
                                "            width=7,\n",
                            ),
                        )
                    # set stripconfigframe button widths
                    case "                    self.configframe.phys_out_params.index(param)\n":
                        write_outs(
                            output,
                            (
                                "                    self.configframe.phys_out_params.index(param)\n",
                                "                ],\n",
                                "                width=6,\n",
                            ),
                        )
                        ignore_next_lines = 1
                    case "                    self.configframe.virt_out_params.index(param)\n":
                        write_outs(
                            output,
                            (
                                "                    self.configframe.virt_out_params.index(param)\n",
                                "                ],\n",
                                "                width=6,\n",
                            ),
                        )
                        ignore_next_lines = 1
                    # This does both strip and bus param vars buttons
                    case "                variable=self.configframe.param_vars[i],\n":
                        write_outs(
                            output,
                            (
                                "                variable=self.configframe.param_vars[i],\n",
                                "                width=6,\n",
                            ),
                        )
                    case _:
                        if "Toggle.TButton" in line:
                            output.write(line.replace("Toggle.TButton", "ToggleButton"))
                        else:
                            output.write(line)


def rewrite_menu():
    menu_logger = logger.getChild("menu")
    menu_logger.info("rewriting menu.py")
    infile = Path(SRC_DIR) / "menu.bk"
    outfile = Path(PACKAGE_DIR) / "menu.py"
    with open(infile, "r") as input:
        with open(outfile, "w") as output:
            ignore_next_lines = 0

            for line in input:
                if ignore_next_lines > 0:
                    menu_logger.info(f"ignoring: {line}")
                    ignore_next_lines -= 1
                    continue
                match line:
                    case "import sv_ttk\n":
                        output.write("#import sv_ttk\n")
                    case "        # layout/themes\n":
                        ignore_next_lines = 14
                    case _:
                        output.write(line)


def prepare_for_build():
    ################# MOVE FILES FROM PACKAGE DIR INTO SRC DIR #########################
    for file in (
        PACKAGE_DIR / "app.py",
        PACKAGE_DIR / "builders.py",
        PACKAGE_DIR / "menu.py",
    ):
        if file.exists():
            logger.debug(f"moving {str(file)}")
            file.rename(SRC_DIR / f"{file.stem}.bk")

    ###################### RUN THE FILE REWRITER FOR EACH *.BK #########################
    steps = (
        rewrite_app,
        rewrite_builders,
        rewrite_menu,
    )
    [step() for step in steps]


def cleanup():
    ########################## RESTORE *.BK FILES #####################################
    for file in (
        PACKAGE_DIR / "app.py",
        PACKAGE_DIR / "builders.py",
        PACKAGE_DIR / "menu.py",
    ):
        file.unlink()

    for file in (
        SRC_DIR / "app.bk",
        SRC_DIR / "builders.bk",
        SRC_DIR / "menu.bk",
    ):
        file.rename(PACKAGE_DIR / f"{file.stem}.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rewrite", action="store_true")
    parser.add_argument("-c", "--cleanup", action="store_true")
    args = parser.parse_args()

    if args.rewrite:
        logger.info("preparing files for build")
        prepare_for_build()
    elif args.cleanup:
        logger.info("cleaning up files")
        cleanup()
