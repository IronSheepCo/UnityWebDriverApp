# -*- mode: python -*-

block_cipher = None


a = Analysis(['client.py'],
             pathex=['/Users/macpro/Documents/ironsheep/UnityWebDriverClient'],
             binaries=None,
             datas=[ ('connect_screen.kv', '.') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='client',
          debug=False,
          strip=False,
          upx=True,
          console=True )
