# -*- mode: python ; coding: utf-8 -*-
import os
import glob

# Collect pywinpty binaries into the 'winpty' sub-directory so the package can find its own DLLs
winpty_dir = os.path.join(os.getcwd(), '.venv', 'Lib', 'site-packages', 'winpty')
winpty_binaries = []
for pattern in ['*.dll', '*.exe']:
    for f in glob.glob(os.path.join(winpty_dir, pattern)):
        winpty_binaries.append((f, 'winpty'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=winpty_binaries,
    datas=[],
    hiddenimports=[
        'docker_gui',
        'docker_gui.theme',
        'docker_gui.logger',
        'docker_gui.docker_client',
        'docker_gui.ansi_parser',
        'docker_gui.pty_session',
        'docker_gui.terminal_display',
        'docker_gui.terminal_tab',
        'docker_gui.container_card',
        'docker_gui.create_dialog',
        'docker_gui.main_window',
        'pyte',
        'pyte.screens',
        'pyte.streams',
        'winpty',
        'winpty.ptyprocess',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DockerGUI',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DockerGUI',
)
