"""Generate the logo variants for white and light backgrounds, and the bracketed square icon.

Light variants swap the inks of the existing logo files:
  white (letters, mark)  ->  carbon  #0A0909
  acid  (brackets, slash) ->  acid-ink #598C00

Acid #B6FF2E is 1.21:1 on white, so it disappears. acid-ink is the same hue at OKLCH L 0.58: 4.06:1 on white,
comfortably past the 3:1 that graphics need. It is for brackets and slashes on light surfaces only.

The bracketed square puts the mark between the wordmark's brackets: [▲]. Bracket proportions come from the
lockup (stroke 0.092 and arm 0.31 of the bracket height), the brackets stand 1.2x the mark's height, and the
group keeps the square icon's optical centre, with its corners inside the circular-crop safe zone.

  python3 tools/render_logo_variants.py      SVGs into brand/ and brand/square/, PNGs into brand/png/ and brand/square/

Needs cairosvg and pillow.
"""
import io
import re
from pathlib import Path

import cairosvg
from PIL import Image

BRAND = Path(__file__).resolve().parent.parent / 'brand'
SQUARE = BRAND / 'square'
PNG = BRAND / 'png'

CARBON, WHITE, ACID, ACID_INK = '#0A0909', '#FFFFFF', '#B6FF2E', '#598C00'
RULE, RULE_LIGHT = '#2C2A29', '#E7E2DE'    # grid lines on carbon, and their counterpart on white

MARK = [
    [(0, 519.62), (300, 0), (542.84, 420.62), (466.63, 420.62), (300, 132), (76.21, 519.62)],
    [(114.32, 519.62), (300, 198), (338.11, 264), (228.63, 453.62), (561.89, 453.62), (600, 519.62)],
]


def recolor(svg, mapping, comment):
    for a, b in mapping.items():
        svg = svg.replace(f'"{a}"', f'"{b}"')
    return re.sub(r'<!--.*?-->', f'<!-- {comment} -->', svg, count=1, flags=re.S)


def square_parts(svg):
    """The ground, the grid group and the registration group of a square icon (registration may be absent)."""
    grid = re.search(r'<g stroke="#2C2A29".*?</g>', svg, flags=re.S).group(0)
    reg = re.search(r'<g stroke="#B6FF2E".*?</g>', svg, flags=re.S)
    return grid, reg.group(0) if reg else ''


def bracket_square(grid, ground, mark_ink, bracket_ink, comment):
    W = 208                                   # mark width; height is W x 0.866
    k = W / 600
    mh = 519.62 * k
    cy = 242.92                               # optical centre of the mark, as in the square icon
    hb = mh * 1.2                             # bracket height
    t, arm, gap = hb * 0.092, hb * 0.312, 34
    total = 2 * arm + 2 * gap + W
    x0 = (512 - total) / 2
    mx, my = x0 + arm + gap, cy - mh / 2
    by = cy - hb / 2
    f = lambda n: f'{n:.2f}'
    polys = ''.join('<polygon points="' + ' '.join(f'{f(mx + x * k)},{f(my + y * k)}' for x, y in p) + '"/>' for p in MARK)
    lx, rx = x0, 512 - x0
    left = f'M{f(lx)} {f(by)}H{f(lx + arm)}V{f(by + t)}H{f(lx + t)}V{f(by + hb - t)}H{f(lx + arm)}V{f(by + hb)}H{f(lx)}Z'
    right = f'M{f(rx)} {f(by)}H{f(rx - arm)}V{f(by + t)}H{f(rx - t)}V{f(by + hb - t)}H{f(rx - arm)}V{f(by + hb)}H{f(rx)}Z'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
            f'  <!-- {comment} -->\n'
            f'  <rect width="512" height="512" fill="{ground}"/>\n'
            f'  {grid}\n'
            f'  <g fill="{mark_ink}">{polys}</g>\n'
            f'  <path fill="{bracket_ink}" d="{left} {right}"/>\n'
            f'</svg>\n')


def png(svg, width, out, height=None):
    data = cairosvg.svg2png(bytestring=svg.encode(), output_width=width, output_height=height)
    Image.open(io.BytesIO(data)).save(out, optimize=True)
    return out


def main():
    made = []
    light = {WHITE: CARBON, ACID: ACID_INK}

    # lockups for white backgrounds
    for name, comment in [
        ('astralabs-lockup', 'AstraLabs lockup for white and light backgrounds. Letters and mark carbon #0A0909, brackets and slash acid-ink #598C00.'),
        ('astralabs-lockup-stacked', 'AstraLabs stacked lockup for white and light backgrounds. Letters and mark carbon #0A0909, brackets and slash acid-ink #598C00.'),
        ('astralabs-lockup-mono', 'AstraLabs lockup, single-ink carbon #0A0909, for one-color printing on white and light backgrounds.'),
    ]:
        svg = recolor((BRAND / f'{name}.svg').read_text(), light, comment)
        out = BRAND / f'{name}-light.svg'
        out.write_text(svg)
        made.append(out)
        for w in (1200, 2400):
            made.append(png(svg, w, PNG / f'{name}-light-{w}w.png'))

    # square icons for white backgrounds: white ground, light grid, carbon mark, acid-ink registration
    sq_light = {CARBON: '__GROUND__', WHITE: CARBON, RULE: RULE_LIGHT, ACID: ACID_INK}
    for name, comment in [
        ('astralabs-square', 'AstraLabs square icon for white and light backgrounds. White ground, light 32-unit lab grid, carbon mark optically centred, corners inside the circular-crop safe zone.'),
        ('astralabs-square-reg', 'AstraLabs square icon with registration marks, for white and light backgrounds. White ground, light lab grid, carbon mark, acid-ink registration marks.'),
    ]:
        svg = recolor((SQUARE / f'{name}.svg').read_text(), sq_light, comment).replace('"__GROUND__"', f'"{WHITE}"')
        out = SQUARE / f'{name}-light.svg'
        out.write_text(svg)
        made.append(out)
        for n in (128, 512, 1024):
            made.append(png(svg, n, SQUARE / f'{name}-light-{n}.png'))

    # the bracketed square, on carbon and on white
    grid, _ = square_parts((SQUARE / 'astralabs-square.svg').read_text())
    for name, svg in [
        ('astralabs-square-brackets', bracket_square(grid, CARBON, WHITE, ACID,
            'AstraLabs bracketed square icon. Carbon ground, 32-unit lab grid, white mark between acid brackets, optically centred, corners inside the circular-crop safe zone.')),
        ('astralabs-square-brackets-light', bracket_square(grid.replace(RULE, RULE_LIGHT), WHITE, CARBON, ACID_INK,
            'AstraLabs bracketed square icon for white and light backgrounds. White ground, light lab grid, carbon mark between acid-ink brackets.')),
    ]:
        out = SQUARE / f'{name}.svg'
        out.write_text(svg)
        made.append(out)
        for n in (128, 512, 1024):
            made.append(png(svg, n, SQUARE / f'{name}-{n}.png'))

    for m in made:
        print(m.relative_to(BRAND.parent))


if __name__ == '__main__':
    main()
