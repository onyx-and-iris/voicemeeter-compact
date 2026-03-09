import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('vm-compact-rewriter')

PACKAGE_DIR = Path(__file__).parent.parent / 'vmcompact'

SRC_DIR = Path(__file__).parent / 'src'


def write_outs(output, outs: tuple):
    for out in outs:
        output.write(out)


def rewrite_app(theme):
    app_logger = logger.getChild('app')
    app_logger.info('rewriting app.py')
    infile = Path(SRC_DIR) / 'app.bk'
    outfile = Path(PACKAGE_DIR) / 'app.py'
    with open(infile, 'r') as input:
        with open(outfile, 'w') as output:
            for line in input:
                match line:
                    case '        self._vmr = vmr\n':
                        write_outs(
                            output,
                            (
                                '        self._vmr = vmr\n',
                                '        self._theme = theme\n',
                                '        self._theme_name = theme.split("-")[0]\n',
                                '        self._theme_type = theme.split("-")[-1]\n',
                                '        tcldir = Path.cwd() / "theme" / self._theme_name\n',
                                '        if not tcldir.is_dir():\n',
                                '            tcldir = Path.cwd() / "_internal" / "theme"\n',
                                '        match self._theme_name:\n',
                                '            case "forest":\n',
                                '                self.tk.call("source", tcldir.resolve() / f"{self._theme}.tcl")\n',
                                '            case "azure":\n',
                                '                self.tk.call("source", tcldir.resolve() / f"{self._theme_name}.tcl")\n',
                            ),
                        )
                    case _:
                        output.write(line)


def rewrite_builders(theme):
    builders_logger = logger.getChild('builders')
    builders_logger.info('rewriting builders.py')
    infile = Path(SRC_DIR) / 'builders.bk'
    outfile = Path(PACKAGE_DIR) / 'builders.py'
    with open(infile, 'r') as input:
        with open(outfile, 'w') as output:
            ignore_next_lines = 0

            for line in input:
                if ignore_next_lines > 0:
                    builders_logger.info(f'ignoring: {line}')
                    ignore_next_lines -= 1
                    continue

                match line:
                    # loading themes
                    case 'import sv_ttk\n':
                        output.write('#import sv_ttk\n')
                    case '        self.app.resizable(False, False)\n':
                        if theme.startswith('forest'):
                            write_outs(
                                output,
                                (
                                    '        self.app.resizable(False, False)\n'
                                    '        if _configuration.themes_enabled:\n',
                                    '            ttk.Style().theme_use(self.app._theme)\n',
                                    '            self.logger.info(f"{self.app._theme} Theme applied")\n',
                                ),
                            )
                        elif theme.startswith('azure'):
                            write_outs(
                                output,
                                (
                                    '        self.app.resizable(False, False)\n'
                                    '        if _configuration.themes_enabled:\n',
                                    '            self.app.tk.call("set_theme", self.app._theme_type)\n',
                                    '            self.logger.info(f"Azure {self.app._theme_type} Theme applied")\n',
                                ),
                            )
                        ignore_next_lines = 6
                    # setting navframe button widths
                    case '            variable=self.navframe.submix,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.navframe.submix,\n'
                                '            width=8,\n',
                            ),
                        )
                    case '            variable=self.navframe.channel,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.navframe.channel,\n'
                                '            width=8,\n',
                            ),
                        )
                    case '            variable=self.navframe.extend,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.navframe.extend,\n'
                                '            width=8,\n',
                            ),
                        )
                    case '            variable=self.navframe.info,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.navframe.info,\n'
                                '            width=8,\n',
                            ),
                        )
                    # set channelframe button widths
                    case '            variable=self.labelframe.mute,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.labelframe.mute,\n'
                                '            width=7,\n',
                            ),
                        )
                    case '            variable=self.labelframe.conf,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.labelframe.conf,\n'
                                '            width=7,\n',
                            ),
                        )
                    case '            variable=self.labelframe.on,\n':
                        write_outs(
                            output,
                            (
                                '            variable=self.labelframe.on,\n'
                                '            width=7,\n',
                            ),
                        )
                    # set stripconfigframe button widths
                    case '                    self.configframe.phys_out_params.index(param)\n':
                        write_outs(
                            output,
                            (
                                '                    self.configframe.phys_out_params.index(param)\n',
                                '                ],\n',
                                '                width=6,\n',
                            ),
                        )
                        ignore_next_lines = 1
                    case '                    self.configframe.virt_out_params.index(param)\n':
                        write_outs(
                            output,
                            (
                                '                    self.configframe.virt_out_params.index(param)\n',
                                '                ],\n',
                                '                width=6,\n',
                            ),
                        )
                        ignore_next_lines = 1
                    # This does both strip and bus param vars buttons
                    case '                variable=self.configframe.param_vars[i],\n':
                        write_outs(
                            output,
                            (
                                '                variable=self.configframe.param_vars[i],\n',
                                '                width=6,\n',
                            ),
                        )
                    case _:
                        if 'Toggle.TButton' in line:
                            if theme.startswith('forest'):
                                output.write(
                                    line.replace('Toggle.TButton', 'ToggleButton')
                                )
                            elif theme.startswith('azure'):
                                output.write(
                                    line.replace(
                                        'Toggle.TButton', 'Switch.TCheckbutton'
                                    )
                                )
                        else:
                            output.write(line)


def rewrite_menu(theme):
    menu_logger = logger.getChild('menu')
    menu_logger.info('rewriting menu.py')
    infile = Path(SRC_DIR) / 'menu.bk'
    outfile = Path(PACKAGE_DIR) / 'menu.py'
    with open(infile, 'r') as input:
        with open(outfile, 'w') as output:
            ignore_next_lines = 0

            for line in input:
                if ignore_next_lines > 0:
                    menu_logger.info(f'ignoring: {line}')
                    ignore_next_lines -= 1
                    continue
                match line:
                    case 'import sv_ttk\n':
                        output.write('#import sv_ttk\n')
                    case '        # layout/themes\n':
                        ignore_next_lines = 14
                    case _:
                        output.write(line)


def rewrite_navigation(theme):
    navigation_logger = logger.getChild('navigation')
    navigation_logger.info('rewriting navigation.py')
    infile = Path(SRC_DIR) / 'navigation.bk'
    outfile = Path(PACKAGE_DIR) / 'navigation.py'
    with open(infile, 'r') as input:
        with open(outfile, 'w') as output:
            for line in input:
                match line:
                    case '        self.builder.create_info_button()\n':
                        if theme.startswith('azure'):
                            output.write(
                                '        # self.builder.create_info_button()\n'
                            )
                        else:
                            output.write(line)
                    case _:
                        output.write(line)


def prepare_for_build(theme):
    ################# MOVE FILES FROM PACKAGE DIR INTO SRC DIR #########################
    for file in (
        PACKAGE_DIR / 'app.py',
        PACKAGE_DIR / 'builders.py',
        PACKAGE_DIR / 'menu.py',
        PACKAGE_DIR / 'navigation.py',
    ):
        if file.exists():
            logger.debug(f'moving {str(file)}')
            file.rename(SRC_DIR / f'{file.stem}.bk')

    ###################### RUN THE FILE REWRITER FOR EACH *.BK #########################
    for step in (rewrite_app, rewrite_builders, rewrite_menu, rewrite_navigation):
        step(theme)


def cleanup():
    ########################## RESTORE *.BK FILES #####################################
    for file in (
        SRC_DIR / 'app.bk',
        SRC_DIR / 'builders.bk',
        SRC_DIR / 'menu.bk',
        SRC_DIR / 'navigation.bk',
    ):
        if file.exists():
            logger.debug(f'moving {str(file)}')
            file.replace(PACKAGE_DIR / f'{file.stem}.py')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rewrite', action='store_true')
    parser.add_argument('--theme', type=str, default='forest')
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()

    if args.rewrite:
        logger.info('preparing files for build')
        prepare_for_build(args.theme)
    elif args.restore:
        logger.info('cleaning up files')
        cleanup()
