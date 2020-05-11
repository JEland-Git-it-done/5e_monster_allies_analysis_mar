# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['addon_pack_witcher.py'],
             pathex=['C:\\Users\\jedel\\PycharmProjects\\5e_monster_allies_analysis_mar\\venv'],
             binaries=[],
             datas=[('cleaned_kfc_monstercopy.csv', '.'), ('mtf_monsters.xlsx', '.'), ('kfc_monsters.xlsx', '.'), ('kfc_monstercopy.csv', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='addon_pack_witcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='addon_pack_witcher')
