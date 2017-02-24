# -*- mode: python -*-

block_cipher = None


a = Analysis(['client.py'],
             pathex=['.'],
             binaries=None,
             datas=[ ('connect_screen.kv', '.'), ('elements_screen.kv', '.'), ('test_case_entry.kv', '.'), ('choose_command_content.kv', '.'), ('connect_entry.kv', '.')  ],
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
          name='IRONforge',
          icon='IRONfuse.ico',
          debug=False,
          strip=False,
          upx=True,
          console=True )
