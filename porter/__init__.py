# porter: the port pipeline. A player's extracted game files (ExeFS and RomFS, extracted from their own Switch) + a game profile → an APK and the game's data pack
# (docs/ARCHITECTURE.md). It reads no NSP or XCI and takes no keys.
#   python -m porter doctor | profiles | inspect <folder> | port <folder> | install <data pack> | devices | config
__version__ = '0.2.0'
