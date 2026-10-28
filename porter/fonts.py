# The shared-font stand-ins the app hands a game (hle_sdk16.c reads DM_FONT_DIR/standard.ttf and DM_FONT_DIR/nintendo_ext.ttf), made on the player's computer as the iOS build
# makes them (dm/ios/tools/build_ipa.sh): standard.ttf is a system font covering what Nintendo's standard shared font has, nintendo_ext.ttf the controller-button icons that
# dm/tools/make_ext_font.py draws (fontTools). Without them the Android host falls back to the device's Roboto, which has no U+25A1 (□): Link's Awakening looks that glyph up
# as its stand-in for missing characters while laying out its first text, got null and crashed (main+0x111e0d0); and every game's button icons drew as "?".
# The fonts go from the player's computer to their device only, as on iOS.
import importlib.util, os, shutil, sys
from pathlib import Path

from porter.paths import DM
from porter.upstream import nsp, say

_WIN = Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts'
# first found wins; each has U+25A1 (Arial: WGL4's geometric shapes; Arial Unicode and DejaVu Sans: the whole block)
STANDARD = {'darwin': ['/System/Library/Fonts/Supplemental/Arial Unicode.ttf', '/Library/Fonts/Arial Unicode.ttf'], 'win32': [str(_WIN / 'arial.ttf')],
            'linux': ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/TTF/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf']}
LETTERS = {'darwin': ['/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'], 'win32': [str(_WIN / 'arialbd.ttf')],   # the letters knocked out of the button plates
           'linux': ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']}


def _key(): return sys.platform if sys.platform in ('win32', 'darwin') else 'linux'


def _first(table): return next((Path(p) for p in table[_key()] if Path(p).is_file()), None)


def make(out, py, env, logs):
    """standard.ttf and nintendo_ext.ttf in out (the build folder's android/font), each made again only when its source changes: {name in the data pack: file}.
    A piece this computer cannot make is reported and left out, and the host falls back as above"""
    out.mkdir(parents=True, exist_ok=True); got = {}
    std = _first(STANDARD); dst = out / 'standard.ttf'
    if std:
        if not dst.is_file() or dst.stat().st_size != std.stat().st_size: shutil.copyfile(std, dst)
        got['font/standard.ttf'] = dst
    else: say(f'[RED] no stand-in for the standard shared font on this computer (one of {", ".join(STANDARD[_key()])}): '
              'the app falls back to the device\'s Roboto, which lacks symbols some games need')
    letters, ext, kf = _first(LETTERS), out / 'nintendo_ext.ttf', out / 'nintendo_ext.key'
    if not letters or importlib.util.find_spec('fontTools') is None:
        nsp.rmtree(ext); nsp.rmtree(kf)
        say('[RED] the button icons\' font is not made (' + ('no fontTools: pip install fonttools' if letters else 'no bold font for their letters on this computer') + '): button icons draw as "?"')
        return got
    script = DM / 'tools/make_ext_font.py'
    key = nsp.fingerprint(('files', [script, letters]))
    if not (ext.is_file() and nsp.reused(kf, key) is not None):
        nsp.rmtree(kf)
        nsp.run([py, script, ext, letters], logs / 'android_fonts.log', env=env)
        kf.write_text(f'{key}\n')
    got['font/nintendo_ext.ttf'] = ext
    return got
