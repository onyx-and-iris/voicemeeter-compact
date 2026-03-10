#!/usr/bin/env python3
"""
Spec file generator for voicemeeter-compact builds.
Generates Python launcher files and PyInstaller spec files from templates.
"""

import argparse
from pathlib import Path

# Build configuration
THEMES = {
    'azure': ['azure-light', 'azure-dark'],
    'forest': ['forest-light', 'forest-dark'],
    'sunvalley': ['sunvalley'],  # Single variant, no light/dark
}

KINDS = ['basic', 'banana', 'potato']

# Templates
PYTHON_TEMPLATE = """import voicemeeterlib

import vmcompact


def main():
    KIND_ID = '{kind}'

    with voicemeeterlib.api(KIND_ID) as vmr:{theme_arg}
        app = vmcompact.connect(KIND_ID, vmr{theme_param})
        app.mainloop()


if __name__ == '__main__':
    main()
"""

SPEC_TEMPLATE = """# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
        ( '../../vmcompact/img', 'img' ),{theme_files}
        ( '../../configs', 'configs' ),
        ]

a = Analysis(
    ['{script_name}'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{kind}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{kind}',
)
"""


def generate_python_file(theme_variant: str, kind: str, output_dir: Path) -> None:
    """Generate a Python launcher file."""
    if theme_variant == 'sunvalley':
        # Sunvalley doesn't use theme parameter
        theme_arg = ''
        theme_param = ''
    else:
        theme_arg = f"\n        theme = '{theme_variant}'"
        theme_param = ', theme=theme'

    content = PYTHON_TEMPLATE.format(
        kind=kind, theme_arg=theme_arg, theme_param=theme_param
    )

    filename = f'{theme_variant}-{kind}.py'
    output_path = output_dir / filename

    with open(output_path, 'w') as f:
        f.write(content)

    print(f'Generated: {output_path}')


def generate_spec_file(theme_variant: str, kind: str, output_dir: Path) -> None:
    """Generate a PyInstaller spec file."""
    script_name = f'{theme_variant}-{kind}.py'

    if theme_variant == 'sunvalley':
        # Sunvalley doesn't include theme files
        theme_files = ''
    else:
        theme_base = theme_variant.split('-')[0]  # 'azure' from 'azure-dark'
        theme_files = f"\n        ( '../../theme/{theme_base}', 'theme' ),"

    content = SPEC_TEMPLATE.format(
        script_name=script_name, theme_files=theme_files, kind=kind
    )

    filename = f'{theme_variant}-{kind}.spec'
    output_path = output_dir / filename

    with open(output_path, 'w') as f:
        f.write(content)

    print(f'Generated: {output_path}')


def generate_all_files(output_base_dir: Path) -> None:
    """Generate all Python and spec files for all theme/kind combinations."""
    for theme_family, theme_variants in THEMES.items():
        theme_dir = output_base_dir / theme_family
        theme_dir.mkdir(parents=True, exist_ok=True)

        for theme_variant in theme_variants:
            for kind in KINDS:
                generate_python_file(theme_variant, kind, theme_dir)
                generate_spec_file(theme_variant, kind, theme_dir)


def clean_existing_files(output_base_dir: Path) -> None:
    """Remove all existing generated files."""
    for theme_family in THEMES.keys():
        theme_dir = output_base_dir / theme_family
        if theme_dir.exists():
            for file in theme_dir.glob('*.py'):
                file.unlink()
                print(f'Removed: {file}')
            for file in theme_dir.glob('*.spec'):
                file.unlink()
                print(f'Removed: {file}')


def main():
    parser = argparse.ArgumentParser(
        description='Generate spec files for voicemeeter-compact'
    )
    parser.add_argument(
        '--clean', action='store_true', help='Clean existing files before generating'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('spec'),
        help='Output directory for spec files (default: spec)',
    )

    args = parser.parse_args()

    if args.clean:
        print('Cleaning existing files...')
        clean_existing_files(args.output_dir)

    print('Generating spec files...')
    generate_all_files(args.output_dir)
    print('Done!')


if __name__ == '__main__':
    main()
