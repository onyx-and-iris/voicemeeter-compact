#!/usr/bin/env python3
"""
Dynamic build system for voicemeeter-compact.
Generates spec files on-the-fly and builds executables without storing intermediate files.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict

# Build configuration
THEMES = {
    'azure': ['azure-light', 'azure-dark'],
    'forest': ['forest-light', 'forest-dark'],
    'sunvalley': ['sunvalley'],
}

KINDS = ['basic', 'banana', 'potato']

# Templates (same as spec_generator.py)
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
        ( '{img_path}', 'img' ),{theme_files}
        ( '{config_path}', 'configs' ),
        ]

a = Analysis(
    ['{script_path}'],
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
    name='{theme_variant}-{kind}',
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
    name='{theme_variant}-{kind}',
)
"""


class DynamicBuilder:
    def __init__(self, base_dir: Path, dist_dir: Path):
        self.base_dir = base_dir
        self.dist_dir = dist_dir
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix='vmcompact_build_'))
        print(f'Using temp directory: {self.temp_dir}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f'Cleaned up temp directory: {self.temp_dir}')

    def create_python_file(self, theme_variant: str, kind: str) -> Path:
        """Create a temporary Python launcher file."""
        if theme_variant == 'sunvalley':
            theme_arg = ''
            theme_param = ''
        else:
            theme_arg = f"\n        theme = '{theme_variant}'"
            theme_param = ', theme=theme'

        content = PYTHON_TEMPLATE.format(
            kind=kind, theme_arg=theme_arg, theme_param=theme_param
        )

        py_file = self.temp_dir / f'{theme_variant}-{kind}.py'
        with open(py_file, 'w') as f:
            f.write(content)

        return py_file

    def create_spec_file(self, theme_variant: str, kind: str, py_file: Path) -> Path:
        """Create a temporary PyInstaller spec file."""
        if theme_variant == 'sunvalley':
            theme_files = ''
        else:
            theme_base = theme_variant.split('-')[0]
            theme_path = (self.base_dir / 'theme' / theme_base).as_posix()
            theme_files = f"\n        ( '{theme_path}', 'theme' ),"

        content = SPEC_TEMPLATE.format(
            script_path=py_file.as_posix(),
            img_path=(self.base_dir / 'vmcompact' / 'img').as_posix(),
            config_path=(self.base_dir / 'configs').as_posix(),
            theme_files=theme_files,
            kind=kind,
            theme_variant=theme_variant,
        )

        spec_file = self.temp_dir / f'{theme_variant}-{kind}.spec'
        with open(spec_file, 'w') as f:
            f.write(content)

        return spec_file

    def build_variant(self, theme_variant: str, kind: str) -> bool:
        """Build a single theme/kind variant."""
        print(f'Building {theme_variant}-{kind}...')

        # Create temporary files
        py_file = self.create_python_file(theme_variant, kind)
        spec_file = self.create_spec_file(theme_variant, kind, py_file)

        # Build with PyInstaller
        dist_path = self.dist_dir / f'{theme_variant}-{kind}'
        poetry_bin = os.getenv('POETRY_BIN', 'poetry')
        cmd = [
            poetry_bin,
            'run',
            'pyinstaller',
            '--noconfirm',
            '--distpath',
            str(dist_path.parent),
            str(spec_file),
        ]

        try:
            result = subprocess.run(
                cmd, cwd=self.base_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f'[OK] Built {theme_variant}-{kind}')
                return True
            else:
                print(f'[FAIL] Failed to build {theme_variant}-{kind}')
                print(f'Error: {result.stderr}')
                return False
        except Exception as e:
            print(f'[ERROR] Exception building {theme_variant}-{kind}: {e}')
            return False

    def build_theme(self, theme_family: str) -> Dict[str, bool]:
        """Build all variants for a theme family."""
        results = {}

        if theme_family not in THEMES:
            print(f'Unknown theme: {theme_family}')
            return results

        variants = THEMES[theme_family]

        for variant in variants:
            for kind in KINDS:
                success = self.build_variant(variant, kind)
                results[f'{variant}-{kind}'] = success

        return results


def run_rewriter(theme_family: str, base_dir: Path) -> bool:
    """Run the theme rewriter if needed."""
    if theme_family in ['azure', 'forest']:
        print(f'Running rewriter for {theme_family} theme...')
        poetry_bin = os.getenv('POETRY_BIN', 'poetry')
        cmd = [
            poetry_bin,
            'run',
            'python',
            'tools/rewriter.py',
            '--rewrite',
            '--theme',
            theme_family,
        ]
        try:
            result = subprocess.run(cmd, cwd=base_dir)
            return result.returncode == 0
        except Exception as e:
            print(f'Rewriter failed: {e}')
            return False
    return True


def restore_rewriter(base_dir: Path) -> bool:
    """Restore files after rewriter."""
    print('Restoring rewriter changes...')
    poetry_bin = os.getenv('POETRY_BIN', 'poetry')
    cmd = [poetry_bin, 'run', 'python', 'tools/rewriter.py', '--restore']
    try:
        result = subprocess.run(cmd, cwd=base_dir)
        return result.returncode == 0
    except Exception as e:
        print(f'Restore failed: {e}')
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Dynamic build system for voicemeeter-compact'
    )
    parser.add_argument(
        'themes',
        nargs='*',
        choices=list(THEMES.keys()) + ['all'],
        help='Themes to build (default: all)',
    )
    parser.add_argument(
        '--dist-dir',
        type=Path,
        default=Path('dist'),
        help='Distribution output directory',
    )

    args = parser.parse_args()

    if not args.themes or 'all' in args.themes:
        themes_to_build = list(THEMES.keys())
    else:
        themes_to_build = args.themes

    base_dir = Path.cwd()
    args.dist_dir.mkdir(exist_ok=True)

    print(f'Building themes: {", ".join(themes_to_build)}')

    all_results = {}

    with DynamicBuilder(base_dir, args.dist_dir) as builder:
        for theme_family in themes_to_build:
            # Run rewriter if needed
            if not run_rewriter(theme_family, base_dir):
                print(f'Skipping {theme_family} due to rewriter failure')
                continue

            try:
                # Build theme
                results = builder.build_theme(theme_family)
                all_results.update(results)

            finally:
                # Always restore rewriter changes
                if theme_family in ['azure', 'forest']:
                    restore_rewriter(base_dir)

    # Report results
    print('\n' + '=' * 50)
    print('BUILD SUMMARY')
    print('=' * 50)

    success_count = 0
    total_count = 0

    for build_name, success in all_results.items():
        status = '[OK]' if success else '[FAIL]'
        print(f'{status} {build_name}')
        if success:
            success_count += 1
        total_count += 1

    print(f'\nSuccess: {success_count}/{total_count}')

    if success_count == total_count:
        print('All builds completed successfully!')
        sys.exit(0)
    else:
        print('Some builds failed!')
        sys.exit(1)


if __name__ == '__main__':
    main()
