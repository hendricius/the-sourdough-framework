#!/usr/bin/env python
"""Extract figures from the hardcover PDF as seam-free SVG + PDF pairs.

Pipeline per figure:
  1. pymupdf   : single page, redact stray text (captions, side labels, page
                 numbers) inside the crop, set the CropBox.
  2. pdftocairo: lossless SVG of the cropped page (vectors stay vectors).
  3. merge     : InDesign's transparency flattener split every photo into a
                 grid of clipped raster tiles whose clip rects do not quite
                 meet (167.94pt vs 168.00pt), which renders as a hairline
                 white seam through the photo. Re-composite each run of tiles
                 into ONE image at the tiles' native resolution and drop the
                 clip paths. The tiles are OPAQUE: the flattener cut every
                 region where earlier vector content must show through (a
                 caption, the glyphs of a label) out of the clip path, so the
                 clips are rasterised and applied as each tile's alpha, and
                 rectilinear clips are dilated by a pixel so adjacent tiles
                 overlap instead of leaving the seam.
                 A run with nothing drawn underneath is flattened
                 onto white and stored as JPEG; a run that sits on top of
                 earlier artwork keeps its alpha as a JPEG + luminance mask.
  4. rsvg      : the print PDF is rendered from the merged SVG with
                 rsvg-convert (cairosvg cannot do <mask>), then its Flate
                 images are swapped for the very same JPEG bytes so the PDF
                 stays small.
"""
import base64, io, math, os, re, subprocess, sys
import pymupdf, cairosvg
from lxml import etree
from PIL import Image, ImageChops, ImageFilter

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'book-hardcover.pdf')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
ONLY = set(sys.argv[2:])
SVG = '{http://www.w3.org/2000/svg}'
XL = '{http://www.w3.org/1999/xlink}'
JPEG_Q = 88
MAX_PX_PER_PT = 300 / 72

# name -> (hardcover page, x0, y0, x1, y1, [rects whose TEXT is redacted])
# Coordinates in pt, origin top-left of the 498.9 x 697.3 pt page.
W = 498.898
FIGS = {
 # chapter 4
 'sourdough-starter-stiff':          (73, 128, 116, 389, 358, []),
 'stiff-starter-dry-check':          (74,  80,   0,   W, 592, []),
 'stollen':                          (77,  53,  81, 481, 335, []),
 # chapter 5
 'wheat-kernel-overview':            (84,  70,  50, 450, 636, []),
 # chapter 6
 'flat-breads-selection':            (92,  27, 213,   W, 398, []),
 'flat-bread-wheat':                 (98,  45,  78,   W, 328, []),
 'ethiopian-woman-checking-bread':   (99,   0,   6, 440, 312, [(10, 10, 34, 100)]),
 'injera-pancake-texture':          (100,  85,   0, 368, 171, []),
 'einkorn-crumb':                   (101,  61,  50, 437, 266, [(125, 84, 250, 101)]),
 # chapter 7
 'window-pane-effect':              (116,  50, 421, 455, 697.32, [(378, 448, 464, 502)]),
 'dough-strength-no-kneading':      (124,  75, 278, 455, 514, []),
 'dough-surface-touchpoints':       (126,  70, 150, 382, 357, []),
 'dough-ball-steps':                (127,  65, 245, 425, 606, []),
 'bulk-finished-dough':             (136,  40,   0,   W, 270, [(463, 12, 490, 100), (78, 170, 254, 222)]),
 'dough-being-glued':               (137,   0,   0, 486, 300, [(10, 10, 34, 100)]),
 'stretch-and-fold-steps':          (138,  78, 438, 445, 632, []),
 'dough-requiring-stretch-and-fold':(140,  40, 150, 400, 420, []),
 'divide-preshape':                 (142,  82,  80, 443, 270, []),
 'preshape-direction':              (143, 128, 258, 450, 392, []),
 'preshaped-dough':                 (144,  66,  80, 431, 226, []),
 'step-3-rectangular':              (149,   0,  46, 495, 400, [(10, 10, 34, 100)]),
 'step-4-folding':                  (150,  78, 366, 452, 625, []),
 'step-6-prepare-proofing':         (151,   0, 410,   W, 697.32, [(305, 604, 422, 665), (10, 660, 42, 690)]),
 'step-13-finger-poke-test':        (155, 131, 169, 414, 359, []),
 'bread-scoring-angle':             (159,  60,  90, 425, 314, []),
 'dry-dough-surface':               (160,  30,  88, 430, 314, []),
 # chapter 2 / 3 / 4 (starter)
 'saccharomyces-cerevisiae-microscope': (33, 100, 258, 437, 620, []),
 'bacteria-microscope':              (37, 125, 296, 420, 432, []),
 'sourdough-starter-microbial-war':  (51, 128,  76, 418, 565, []),
 'sourdough-starter':                (67, 165, 155, 375, 430, []),
 'sourdough-starter-liquid':         (69, 165, 110, 380, 352, []),
 # composite: the hardcover spreads the three starter types over two pages
 'sourdough-starter-types':          {'size': (915, 255), 'parts': [
                                        (64, (70, 65, 375, 320),  (0, 0)),      # Liquid
                                        (63, (120, 405, 410, 652), (312, 4)),   # Regular
                                        (64, (70, 338, 375, 585),  (610, 4)),   # Stiff
                                     ]},
 # chapter 7 (more)
 'aliquot-before-after':            (133, 100,  75, 440, 312, []),
 'step-2-flipped-over':             (148,   0, 105, 380, 436, [(80, 433, 375, 465)]),
 # chapter 12 (troubleshooting)
 'sourdough-starter-hooch':         (196, 295, 450, 450, 625, []),
 'tearing-dough':                   (203,   0, 345, 385, 697.32, [(285, 395, 420, 410), (10, 660, 45, 690)]),
 'parbaked-bread':                  (207,  30,  55,   W, 254, []),
 'crumb-structures-book':           (211, 125, 210, 425, 618, []),
 'open-crumb':                      (212,  30, 110, 425, 314, []),
 'honeycomb':                       (213,  85, 170, 415, 360, []),
 'fermented-too-long':              (214,  80, 105, 375, 238, []),
 'fermented-too-short-underbaked':  (216,  80,  82, 390, 218, [(80, 78, 300, 96)]),
 'fools-crumb':                     (217, 115,  70, 430, 231, []),
 'flat-bread':                      (218,  60, 110, 372, 244, [(80, 238, 310, 250)]),
 'baked-too-hot-v2':                (219,  85,  68, 450, 312, [(125, 266, 368, 280), (80, 78, 300, 100)]),
 'no-steam':                        (220,  40, 120, 390, 356, []),
 'apple-experiment-temperatures':   (221, 100,  30, 420, 335, [(128, 311, 420, 333)]),
 # chapter 1 / 2 / 3
 'sourdough-stove':                  (21,  40, 218, 475, 424, []),
 'whole-wheat-crumb':                (32,  80, 418, 448, 624, []),
 'sourdough-starter-activity-indicators': (46, 85, 285, 498.89, 620, []),
 # chapter 6 / 7
 'free-standing-loaf':               (95,  40, 270, 420, 600, [(128, 600, 420, 632)]),
 'loaf-pan-free-standing':           {'size': (690, 335), 'parts': [
                                        (93, (105, 190, 395, 445), (0, 45), [(128, 403, 420, 452)]),   # loaf pan
                                        (95, (40, 270, 420, 600), (310, 0), []),                       # freestanding
                                     ]},
 'step-1-flour-applied':            (147,  85, 105, 420, 436, [(128, 435, 420, 456)]),
 'the-ear':                         (157, 125, 355, 420, 480, []),
 'artistic-scoring':                (158,  50, 300, 475, 604, [(80, 602, 450, 632)]),
 # chapter 8 (non-wheat)
 'final-bread':                     (163,  30, 150, 460, 344, []),
 'ingredients':                     (165, 110, 356, 437, 626, [(128, 620, 420, 642)]),
 'sticky-hands':                    (166,  60, 160, 498.89, 461, [(80, 424, 375, 455), (60, 138, 499, 162), (60, 458, 499, 482)]),
 'crumb':                           (167, 100, 308, 440, 585, []),
 # chapter 10 (baking)
 'baking-process-steam':            (175,  50, 220, 402, 456, []),
 'baking-too-hot':                  (177,  50,  95, 425, 356, [(128, 345, 420, 373)]),
 'dutch-oven-example':              (178,  60, 362, 465, 606, [(84, 590, 375, 640)]),
 'baking-example':                  (181,  50, 375, 420, 615, []),
 # chapter 9 (mix-ins)
 'broa':                            (233,   0, 358, 390, 697.32, [(100, 330, 420, 368), (315, 605, 420, 645), (10, 660, 45, 690)]),
 'beer-bread':                      (234,  60, 386, 475, 646, [(80, 623, 450, 645)]),
 'stollen-close-up':                (235,  90, 352, 440, 596, []),
 'seeds-bread':                     (236, 150, 362, 460, 592, []),
 'apple-swirl':                     (239,  35, 450, 277, 660, []),
 'surface-seeds':                   (240,  80, 270, 447, 425, [(80, 404, 375, 462)]),
 'pumpkin-sourdough':               (229,  34, 343, 448, 620, [(118, 613, 416, 648)]),
 'pumpkin-on-flour':                (232,  90,  85, 352, 320, []),
 'seeded-sourdough':                (232,  90, 370, 352, 614, []),
}


def crop_page(name, pn, x0, y0, x1, y1, strips):
    doc = pymupdf.open(SRC)
    one = pymupdf.open(); one.insert_pdf(doc, from_page=pn - 1, to_page=pn - 1)
    pg = one[0]
    for r in strips:
        pg.add_redact_annot(pymupdf.Rect(*r))
    if strips:
        pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    pg.set_cropbox(pymupdf.Rect(x0, y0, x1, y1))
    tmp = f'{OUT}/{name}.page.pdf'
    one.save(tmp); one.close(); doc.close()
    return tmp


# --- SVG helpers -----------------------------------------------------------
def kids(el):
    return [k for k in el if isinstance(k.tag, str)]


def is_tile(el):
    """A <use> of a raster source, bare or wrapped in (nested) clip <g>s."""
    if el.tag == SVG + 'use':
        return (el.get(XL + 'href') or '').startswith('#source-')
    return el.tag == SVG + 'g' and len(kids(el)) == 1 and is_tile(kids(el)[0])


def tile_use(el):
    return el if el.tag == SVG + 'use' else tile_use(kids(el)[0])


def clip_chain(el):
    """Clip ids applied to a tile, outermost first."""
    ids = []
    while el is not None and el.tag == SVG + 'g':
        m = re.match(r'url\(#([^)]+)\)', el.get('clip-path', '') or '')
        if m:
            ids.append(m.group(1))
        el = kids(el)[0] if kids(el) else None
    return ids


class ClipMasks:
    """Rasterise <clipPath> outlines at canvas resolution, once per clip id."""
    def __init__(self, defs, box, scale, size):
        self.defs, self.box, self.scale, self.size, self.cache = defs, box, scale, size, {}
        self.paths = {}
        for cp in defs.iter(SVG + 'clipPath'):
            self.paths[cp.get('id')] = [k for k in kids(cp)]

    def get(self, cid):
        if cid in self.cache:
            return self.cache[cid]
        parts, rectilinear = [], True
        for k in self.paths.get(cid, []):
            if k.tag == SVG + 'path':
                d = k.get('d', '')
                rectilinear &= not re.search(r'[CcQqSsAa]', d)
                parts.append(f'<path d="{d}" fill="#fff" fill-rule="{k.get("clip-rule", "nonzero")}"/>')
            elif k.tag == SVG + 'rect':
                parts.append('<rect ' + ' '.join(f'{a}="{k.get(a)}"' for a in ('x', 'y', 'width', 'height')) + ' fill="#fff"/>')
        bx0, by0, bx1, by1 = self.box
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bx0} {by0} {bx1 - bx0} {by1 - by0}" '
               f'width="{self.size[0]}" height="{self.size[1]}">{"".join(parts)}</svg>')
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=self.size[0], output_height=self.size[1])
        mask = Image.open(io.BytesIO(png)).convert('RGBA').getchannel('A')
        if rectilinear:
            mask = mask.filter(ImageFilter.MaxFilter(3))
        self.cache[cid] = mask
        return mask


def is_white_bg(el):
    """The page background: a white-filled rect/path, possibly wrapped in clip <g>s."""
    if el.tag in (SVG + 'rect', SVG + 'path'):
        return el.get('fill', '').startswith('rgb(100%') and el.get('stroke', 'none') == 'none'
    if el.tag == SVG + 'g':
        return len(kids(el)) == 1 and is_white_bg(kids(el)[0])
    return False


def matrix_of(el):
    m = re.match(r'matrix\(([^)]*)\)', el.get('transform', '') or '')
    return [float(v) for v in m.group(1).replace(',', ' ').split()] if m else None


def apply(mat, x, y):
    if not mat:
        return x, y
    a, b, c, d, e, f = mat
    return a * x + c * y + e, b * x + d * y + f


GLYPHS = {}


def bbox(el):
    """Bounding box (x0, y0, x1, y1) of a drawable, in user units."""
    pts = []
    if el.tag == SVG + 'path':
        nums = [float(v) for v in re.findall(r'-?\d+\.?\d*(?:e-?\d+)?', el.get('d', ''))]
        pts = list(zip(nums[0::2], nums[1::2]))
    elif el.tag == SVG + 'rect':
        x, y, w, h = (float(el.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
        pts = [(x, y), (x + w, y + h)]
    elif el.tag == SVG + 'image':
        x, y, w, h = (float(el.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
        pts = [(x, y), (x + w, y + h)]
    elif el.tag == SVG + 'use':
        x, y = float(el.get('x', 0)), float(el.get('y', 0))
        g = GLYPHS.get((el.get(XL + 'href') or '')[1:])
        if g is None:
            return None                                    # empty glyph (space)
        pts = [(x + g[0], y + g[1]), (x + g[2], y + g[3])]
    elif el.tag == SVG + 'g':
        boxes = [b for b in (bbox(k) for k in kids(el)) if b]
        if not boxes:
            return None
        pts = [(b[0], b[1]) for b in boxes] + [(b[2], b[3]) for b in boxes]
    if not pts:
        return None
    mat = matrix_of(el)
    pts = [apply(mat, x, y) for x, y in pts]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def intersects(a, b, margin=0.5):
    return not (a[2] < b[0] + margin or b[2] < a[0] + margin or a[3] < b[1] + margin or b[3] < a[1] + margin)


def merge_tiles(svg_in, svg_out):
    """Composite every raster tile of the page into ONE JPEG.

    The image goes where the first tile was, so vector art drawn before it
    (a starburst behind a photo) stays underneath and everything after it
    stays on top. Where such earlier art would show through a not-fully-
    opaque part of the tiles, the image carries its alpha as a luminance
    <mask>; otherwise it is flattened onto white. verify() diffs the result
    against the untouched cairo SVG so an ordering mistake cannot go unseen.
    """
    tree = etree.parse(svg_in)
    root = tree.getroot()
    vb = [float(v) for v in root.get('viewBox').split()]
    defs = root.find(SVG + 'defs')
    GLYPHS.clear()
    for g in defs.iter(SVG + 'g'):
        if (g.get('id') or '').startswith('glyph-'):
            b = bbox(g)
            if b:
                GLYPHS[g.get('id')] = b
    sources = {}
    for im in defs.iter(SVG + 'image'):
        raw = base64.b64decode(im.get(XL + 'href').split(',', 1)[1])
        sources[im.get('id')] = Image.open(io.BytesIO(raw)).convert('RGBA')

    children = [c for c in root if isinstance(c.tag, str) and c is not defs]
    tile_els = [c for c in children if is_tile(c)]
    if not tile_els:
        tree.write(svg_out, xml_declaration=True, encoding='utf-8')
        return []

    tiles = []
    for g in tile_els:
        u = tile_use(g)
        mat = matrix_of(u)
        img = sources[u.get(XL + 'href')[1:]]
        w, h = img.size
        corners = [apply(mat, px, py) for px, py in ((0, 0), (w, 0), (0, h), (w, h))]
        tiles.append((mat, img, corners, clip_chain(g)))
    xs = [p[0] for t in tiles for p in t[2]]; ys = [p[1] for t in tiles for p in t[2]]
    bx0, by0 = max(min(xs), vb[0]), max(min(ys), vb[1])
    bx1, by1 = min(max(xs), vb[0] + vb[2]), min(max(ys), vb[1] + vb[3])
    box = (bx0, by0, bx1, by1)
    scale = min(max(1 / math.hypot(t[0][0], t[0][1]) for t in tiles), MAX_PX_PER_PT)
    cw, ch = max(1, round((bx1 - bx0) * scale)), max(1, round((by1 - by0) * scale))
    canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    clips = ClipMasks(defs, box, scale, (cw, ch))
    for (mat, img, corners, chain) in tiles:
        a, b, c_, d, e, f = mat
        A, B, C = a * scale, c_ * scale, (e - bx0) * scale
        D, E, F = b * scale, d * scale, (f - by0) * scale
        det = A * E - B * D
        inv = (E / det, -B / det, (B * F - E * C) / det, -D / det, A / det, (D * C - A * F) / det)
        layer = img.transform((cw, ch), Image.AFFINE, inv, resample=Image.BICUBIC)
        alpha = layer.getchannel('A')
        for cid in chain:
            alpha = ImageChops.multiply(alpha, clips.get(cid))
        layer.putalpha(alpha)
        canvas = Image.alpha_composite(canvas, layer)

    # Anything drawn BEFORE the first tile that lies under a translucent part
    # of the canvas must stay visible: keep the alpha as a mask in that case.
    first = tile_els[0]
    alpha = canvas.getchannel('A')
    needs_mask = False
    for c in children:
        if c is first:
            break
        if is_tile(c) or is_white_bg(c):
            continue
        d = bbox(c)
        if not d or not intersects(box, d, margin=0.1):
            continue
        ix0, iy0 = max(box[0], d[0]), max(box[1], d[1])
        ix1, iy1 = min(box[2], d[2]), min(box[3], d[3])
        px = (int((ix0 - bx0) * scale), int((iy0 - by0) * scale),
              min(cw, int((ix1 - bx0) * scale) + 1), min(ch, int((iy1 - by0) * scale) + 1))
        if px[2] > px[0] and px[3] > px[1] and alpha.crop(px).getextrema()[0] < 255:
            needs_mask = True
            break

    flat = Image.new('RGB', (cw, ch), (255, 255, 255)); flat.paste(canvas, mask=alpha)
    buf = io.BytesIO(); flat.save(buf, 'JPEG', quality=JPEG_Q, optimize=True, progressive=True)
    new = etree.Element(SVG + 'image')
    for k, v in (('x', bx0), ('y', by0), ('width', bx1 - bx0), ('height', by1 - by0)):
        new.set(k, f'{v:.3f}')
    new.set('preserveAspectRatio', 'none')
    new.set(XL + 'href', 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode())
    if needs_mask:
        mask = etree.SubElement(defs, SVG + 'mask', id='mask-photo', maskUnits='userSpaceOnUse')
        for k in ('x', 'y', 'width', 'height'):
            mask.set(k, new.get(k))
        mimg = etree.SubElement(mask, SVG + 'image')
        for k in ('x', 'y', 'width', 'height', 'preserveAspectRatio'):
            mimg.set(k, new.get(k))
        abuf = io.BytesIO(); alpha.save(abuf, 'PNG', optimize=True)
        mimg.set(XL + 'href', 'data:image/png;base64,' + base64.b64encode(abuf.getvalue()).decode())
        new.set('mask', 'url(#mask-photo)')
    first.addprevious(new)
    for g in tile_els:
        root.remove(g)

    body = etree.tostring(root, encoding='unicode')
    for el in list(defs):
        if el.tag == SVG + 'image' and f'#{el.get("id")}' not in body:
            defs.remove(el)
        elif el.tag == SVG + 'clipPath' and f'url(#{el.get("id")})' not in body:
            defs.remove(el)
    tree.write(svg_out, xml_declaration=True, encoding='utf-8')
    return [(cw, ch, buf.getvalue())]


def build_one(name, spec):
    """crop -> cairo SVG -> merged SVG. Returns (svg path, raw svg path, jpegs)."""
    page_pdf = crop_page(name, *spec)
    raw_svg = f'{OUT}/{name}.raw.svg'
    subprocess.run(['pdftocairo', '-svg', '-f', '1', '-l', '1', page_pdf, raw_svg], check=True)
    jpegs = merge_tiles(raw_svg, f'{OUT}/{name}.svg')
    os.remove(page_pdf)
    return f'{OUT}/{name}.svg', raw_svg, jpegs


def prefix_ids(root, prefix):
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if el.get('id'):
            el.set('id', prefix + el.get('id'))
        for attr, val in list(el.attrib.items()):
            if attr == XL + 'href' and val.startswith('#'):
                el.set(attr, '#' + prefix + val[1:])
            elif 'url(#' in val:
                el.set(attr, re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{prefix}{m.group(1)})', val))


def build_composite(name, spec):
    """Crop every part on its own, then nest the merged SVGs side by side."""
    w, h = spec['size']
    outer = etree.Element(SVG + 'svg', nsmap={None: SVG[1:-1], 'xlink': XL[1:-1]})
    outer.set('width', f'{w}pt'); outer.set('height', f'{h}pt'); outer.set('viewBox', f'0 0 {w} {h}')
    raws, jpegs = [], []
    for i, part_spec in enumerate(spec['parts']):
        pn, clip, (dx, dy) = part_spec[:3]
        strips = part_spec[3] if len(part_spec) > 3 else []
        pname = f'{name}.part{i}'
        svg, raw, jp = build_one(pname, (pn, *clip, strips))
        jpegs += jp; raws.append((raw, dx, dy))
        part = etree.parse(svg).getroot()
        prefix_ids(part, f'p{i}-')
        part.set('x', str(dx)); part.set('y', str(dy))
        for k in ('width', 'height'):
            part.set(k, part.get(k).replace('pt', ''))
        outer.append(part)
        os.remove(svg)
    etree.ElementTree(outer).write(f'{OUT}/{name}.svg', xml_declaration=True, encoding='utf-8')
    # the reference render: the untouched parts, nested the same way
    ref = etree.Element(SVG + 'svg', nsmap={None: SVG[1:-1], 'xlink': XL[1:-1]})
    for k in ('width', 'height', 'viewBox'):
        ref.set(k, outer.get(k))
    for i, (raw, dx, dy) in enumerate(raws):
        part = etree.parse(raw).getroot(); prefix_ids(part, f'p{i}-')
        part.set('x', str(dx)); part.set('y', str(dy))
        for k in ('width', 'height'):
            part.set(k, part.get(k).replace('pt', ''))
        ref.append(part); os.remove(raw)
    raw_svg = f'{OUT}/{name}.raw.svg'
    etree.ElementTree(ref).write(raw_svg, xml_declaration=True, encoding='utf-8')
    return f'{OUT}/{name}.svg', raw_svg, jpegs


def verify(raw_svg, merged_svg, name):
    """Fraction of pixels that differ from the untouched cairo SVG (rsvg)."""
    a, b = f'{OUT}/{name}.raw.png', f'{OUT}/{name}.svg.png'
    subprocess.run(['rsvg-convert', '-f', 'png', '-d', '110', '-p', '110', '-o', a, raw_svg], check=True)
    subprocess.run(['rsvg-convert', '-f', 'png', '-d', '110', '-p', '110', '-o', b, merged_svg], check=True)
    ia, ib = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
    diff = ImageChops.difference(ia, ib).convert('L').point(lambda v: 255 if v > 48 else 0)
    hist = diff.histogram()
    os.remove(a)
    return hist[255] / (ia.width * ia.height)


def svg_to_pdf(svg, pdf, jpegs):
    subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', pdf, svg], check=True)
    if not jpegs:
        return
    doc = pymupdf.open(pdf)
    pg = doc[0]
    # rsvg re-rasterises each image at the output resolution (1785 px where
    # the JPEG has 1780), so match on the nearest size, not an exact one.
    for im in pg.get_images(full=True):
        xref, w, h, cs, filt = im[0], im[2], im[3], im[5], im[8]
        if cs not in ('DeviceRGB', 'ICCBased') or filt == 'DCTDecode':
            continue
        near = [(abs(jw - w) + abs(jh - h), data) for (jw, jh, data) in jpegs if abs(jw - w) <= 8 and abs(jh - h) <= 8]
        if near:
            pg.replace_image(xref, stream=min(near)[1])
    doc.save(pdf + '.tmp', garbage=4, deflate=True); doc.close()
    os.replace(pdf + '.tmp', pdf)


os.makedirs(OUT, exist_ok=True)
for name, spec in FIGS.items():
    if ONLY and name not in ONLY:
        continue
    if isinstance(spec, dict):
        svg, raw_svg, jpegs = build_composite(name, spec)
    else:
        svg, raw_svg, jpegs = build_one(name, spec)
    svg_to_pdf(svg, f'{OUT}/{name}.pdf', jpegs)
    subprocess.run(['pdftocairo', '-png', '-r', '110', '-singlefile', f'{OUT}/{name}.pdf', f'{OUT}/{name}'], check=True)
    changed = verify(raw_svg, svg, name)
    os.remove(raw_svg)
    ps = [l for l in subprocess.run(['pdfinfo', f'{OUT}/{name}.pdf'], capture_output=True, text=True).stdout.splitlines() if l.startswith('Page size')][0].split(':', 1)[1].strip()
    flag = '  <-- CHECK' if changed > 0.01 else ''
    print(f"{name:34s} svg {os.path.getsize(f'{OUT}/{name}.svg')//1024:5d}K  pdf {os.path.getsize(f'{OUT}/{name}.pdf')//1024:5d}K  diff {changed*100:5.2f}%  {ps}{flag}")
