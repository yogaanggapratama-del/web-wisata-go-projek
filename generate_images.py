"""
Generate stylized destination illustrations (SVG-like flat art rendered via PIL).
Used because the sandbox has no access to external photo hosts; these give the
demo a consistent, professional visual identity instead of a broken image icon.
Swap files in static/img/destinations/ with real photography any time.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'img', 'destinations')
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 900, 600

PALETTE = {
    'sky_dawn': ['#F2C572', '#E9895C', '#8C4A3B'],
    'sky_day': ['#BFE3E0', '#6FA8A3', '#1F3A2E'],
    'sky_dusk': ['#E4A6C7', '#8E5A8C', '#2E2A4A'],
    'sky_mist': ['#DCE7E3', '#9FB8AE', '#3A5147'],
}

FOREST = '#1F3A2E'
EMBER = '#BF4E30'
GOLD = '#D4A017'
STONE = '#5B5147'
INK = '#2B2622'


def lerp_color(c1, c2, t):
    c1 = tuple(int(c1[i:i+2], 16) for i in (1, 3, 5))
    c2 = tuple(int(c2[i:i+2], 16) for i in (1, 3, 5))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def sky_gradient(draw, palette_key):
    colors = PALETTE[palette_key]
    n = len(colors) - 1
    for y in range(H):
        t = y / H
        seg = min(int(t * n), n - 1)
        local_t = (t * n) - seg
        c = lerp_color(colors[seg], colors[seg + 1], local_t)
        draw.line([(0, y), (W, y)], fill=c)


def add_grain(img, amount=8):
    noise = Image.effect_noise((W, H), amount).convert('L')
    noise = noise.point(lambda p: 128 + (p - 128) * 0.15)
    img = Image.blend(img.convert('RGB'), noise.convert('RGB'), 0.03)
    return img


def mountain_layer(draw, base_y, height, color, seed, roughness=60):
    rnd = random.Random(seed)
    points = [(0, base_y)]
    x = 0
    step = 60
    y = base_y - height
    while x < W:
        y_off = rnd.randint(-roughness, roughness)
        points.append((x, max(min(base_y, y + y_off), base_y - height - roughness)))
        x += step
    points.append((W, base_y))
    points.append((0, base_y))
    draw.polygon(points, fill=color)


def volcano_peak(draw, cx, base_y, w, h, color, smoke=True):
    draw.polygon([(cx - w / 2, base_y), (cx, base_y - h), (cx + w / 2, base_y)], fill=color)
    # crater notch
    draw.polygon([(cx - w * 0.06, base_y - h + h * 0.08), (cx, base_y - h),
                  (cx + w * 0.06, base_y - h + h * 0.05)], fill=color)


def draw_sun(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def rounded_temple(draw, cx, base_y, scale, color):
    # simple stepped stupa silhouette (generic, non-specific artistic shape)
    tiers = 5
    w0 = 140 * scale
    h0 = 26 * scale
    y = base_y
    for i in range(tiers):
        w = w0 * (1 - i * 0.16)
        draw.rectangle([cx - w / 2, y - h0, cx + w / 2, y], fill=color)
        y -= h0
    draw.polygon([(cx - 10 * scale, y), (cx, y - 40 * scale), (cx + 10 * scale, y)], fill=color)


def river_band(draw, y, thickness, color):
    draw.rectangle([0, y, W, y + thickness], fill=color)


def trees(draw, base_y, color, n=10, seed=1, spread=(0, W), size=(20, 45)):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.randint(*spread)
        s = rnd.randint(*size)
        draw.polygon([(x, base_y), (x - s * 0.4, base_y), (x - s * 0.1, base_y - s),
                      (x + s * 0.1, base_y - s), (x + s * 0.4, base_y)], fill=color)
        draw.polygon([(x - s * 0.28, base_y - s * 0.4), (x, base_y - s * 1.4),
                      (x + s * 0.28, base_y - s * 0.4)], fill=color)


def vignette(img):
    mask = Image.new('L', (W, H), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([-W * 0.3, -H * 0.3, W * 1.3, H * 1.3], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new('RGB', (W, H), (10, 10, 10))
    img = Image.composite(img, dark, mask)
    return img


def label_footer(img, title):
    draw = ImageDraw.Draw(img, 'RGBA')
    draw.rectangle([0, H - 90, W, H], fill=(20, 18, 16, 150))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 34)
    except Exception:
        font = ImageFont.load_default()
    draw.text((36, H - 66), title, font=font, fill='#F5EFE0')
    return img


def save(img, name):
    img = vignette(img)
    img = add_grain(img)
    path = os.path.join(OUT_DIR, name)
    img.convert('RGB').save(path, quality=90)
    print('saved', path)


def scene_kaliurang():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_mist')
    mountain_layer(d, 430, 260, '#3A5147', 3, 40)
    volcano_peak(d, 480, 420, 420, 300, FOREST)
    mountain_layer(d, 470, 90, '#26402F', 7, 25)
    trees(d, 560, INK, n=14, seed=5, size=(24, 50))
    river_band(d, 560, 40, '#7FA69E')
    img = label_footer(img, 'Kaliurang')
    save(img, 'kaliurang.png')


def scene_lava_tour():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_dawn')
    mountain_layer(d, 420, 200, '#6B4A3A', 9, 30)
    volcano_peak(d, 500, 400, 460, 320, '#4A342A')
    # smoke plume
    for i in range(6):
        r = 20 + i * 8
        d.ellipse([500 - r + i * 6, 80 + i * 10 - r, 500 + r + i * 6, 80 + i * 10 + r], fill=(90, 85, 80))
    # jeep silhouette
    d.rectangle([120, 500, 240, 540], fill=INK)
    d.rectangle([140, 470, 210, 500], fill=INK)
    d.ellipse([130, 530, 165, 565], fill=INK)
    d.ellipse([200, 530, 235, 565], fill=INK)
    river_band(d, 560, 40, '#8A6C55')
    img = label_footer(img, 'Lava Tour Merapi')
    save(img, 'lava_tour.png')


def scene_tlogo_putri():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_day')
    mountain_layer(d, 380, 180, '#2E4A3B', 11, 35)
    trees(d, 420, FOREST, n=16, seed=13, size=(22, 40))
    d.rectangle([0, 420, W, H], fill='#3E7C78')
    for i in range(0, W, 40):
        d.arc([i, 430, i + 60, 460], start=200, end=340, fill='#6FB0AA', width=3)
    img = label_footer(img, 'Tlogo Putri Kaliurang')
    save(img, 'tlogo_putri.png')


def scene_museum():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_dusk')
    mountain_layer(d, 430, 120, '#3A3350', 17, 20)
    trees(d, 470, '#241F38', n=10, seed=19, size=(20, 36))
    # museum building
    d.rectangle([300, 340, 600, 470], fill='#E8DFC8')
    for i in range(5):
        x = 330 + i * 55
        d.rectangle([x, 380, x + 26, 470], fill='#C9BDA0')
    d.polygon([(280, 340), (450, 250), (620, 340)], fill='#9C8B5E')
    img = label_footer(img, 'Museum Ullen Sentalu')
    save(img, 'ullen_sentalu.png')


def scene_prambanan():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_dawn')
    mountain_layer(d, 470, 60, '#8C4A3B', 23, 15)
    ground_y = 480
    d.rectangle([0, ground_y, W, H], fill='#7C6A4A')
    rounded_temple(d, 450, ground_y, 1.5, '#4A3A2E')
    rounded_temple(d, 250, ground_y, 0.9, '#5C4A3A')
    rounded_temple(d, 650, ground_y, 0.9, '#5C4A3A')
    img = label_footer(img, 'Candi Prambanan')
    save(img, 'prambanan.png')


def scene_ratu_boko():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_dusk')
    volcano_peak(d, 700, 460, 200, 40, '#2E2A4A', smoke=False)
    d.rectangle([0, 440, W, H], fill='#6E5A44')
    # gate silhouette
    d.rectangle([380, 300, 420, 460], fill=INK)
    d.rectangle([480, 300, 520, 460], fill=INK)
    d.polygon([(370, 300), (400, 250), (430, 300)], fill=INK)
    d.polygon([(470, 300), (500, 250), (530, 300)], fill=INK)
    img = label_footer(img, 'Candi Ratu Boko')
    save(img, 'ratu_boko.png')


def scene_breksi():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_day')
    # cliff carved rock
    d.polygon([(0, 460), (200, 260), (420, 380), (620, 220), (900, 420), (900, 600), (0, 600)], fill='#C9A876')
    d.polygon([(0, 460), (200, 260), (420, 380), (620, 220), (900, 420), (900, 470), (0, 470)], fill='#B08E5E')
    for x, y in [(220, 320), (460, 340), (680, 300)]:
        d.arc([x - 30, y - 30, x + 30, y + 30], 0, 360, fill='#8A6E44', width=4)
    img = label_footer(img, 'Tebing Breksi')
    save(img, 'tebing_breksi.png')


def scene_kalikuning():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    sky_gradient(d, 'sky_mist')
    mountain_layer(d, 420, 160, '#2E4A3B', 29, 30)
    trees(d, 560, FOREST, n=22, seed=31, size=(30, 60), spread=(0, W))
    river_band(d, 560, 40, '#7FA69E')
    img = label_footer(img, 'Kalikuning Adventure Park')
    save(img, 'kalikuning.png')


def scene_logo():
    size = 240
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, size - 10, size - 10], fill=FOREST)
    volcano_peak(d, size / 2, size * 0.72, size * 0.55, size * 0.4, '#F5EFE0')
    d.ellipse([size * 0.62, size * 0.22, size * 0.62 + 26, size * 0.22 + 26], fill=EMBER)
    img.save(os.path.join(os.path.dirname(__file__), 'static', 'img', 'logo.png'))
    print('saved logo')


if __name__ == '__main__':
    scene_kaliurang()
    scene_lava_tour()
    scene_tlogo_putri()
    scene_museum()
    scene_prambanan()
    scene_ratu_boko()
    scene_breksi()
    scene_kalikuning()
    scene_logo()
