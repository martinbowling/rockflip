"""
Rock Flip — GBC sprite/tile generator.

Every sprite is a 16x16 (or 16x32) grid of palette indices:
  '.' / '0' = index 0  (transparent for OBJ sprites, a real color for BG tiles)
  '1' '2' '3' = palette indices 1..3

GBC rules this respects:
  * OBJ palettes: 3 colors + transparent. BG palettes: 4 colors.
  * Colors are RGB555 (each channel 0..31); values below are snapped to multiples of 8.
  * Max 8 OBJ palettes + 8 BG palettes on screen.

Outputs (art/out/):
  <sheet>.png        1x indexed 4-color PNG (feed to png2asset / rgbgfx)
  <sheet>_4x.png     4x preview for humans
  palettes.json      palette table (RGB888 + RGB555 hex)
  mock_screen_4x.png 160x144 mock gameplay frame
Edit the grids, re-run:  python3 make_sprites.py
"""
import json, os, random
from PIL import Image
from regional_detail import terrain_tile,organic_primary,organic_secondary

OUT = os.path.join(os.path.dirname(__file__), "..", "out")

def snap(c):  # RGB888 -> nearest value representable in RGB555
    return tuple((v >> 3) << 3 for v in c)

def rgb555(c):
    r, g, b = (v >> 3 for v in c)
    return f"0x{(b << 10) | (g << 5) | r:04X}"

# ---------------------------------------------------------------- palettes
# OBJ palettes: index 0 transparent (shown magenta in 1x files), 1 = darkest
OBJ = {
    "ranger":     [(255, 0, 255), (40, 32, 24), (200, 136, 56), (248, 208, 160)],
    "tortoise":   [(255, 0, 255), (48, 32, 16), (152, 112, 64), (224, 200, 128)],
    "chuckwalla": [(255, 0, 255), (16, 16, 16), (104, 104, 112), (216, 96, 40)],
    "horned":     [(255, 0, 255), (72, 48, 24), (192, 152, 96), (248, 232, 184)],
    "sidewinder": [(255, 0, 255), (64, 48, 32), (208, 176, 120), (248, 240, 208)],
    "toad":       [(255, 0, 255), (40, 48, 32), (128, 136, 104), (232, 88, 48)],
    "kingsnake":  [(255, 0, 255), (8, 8, 8), (40, 32, 32), (248, 248, 224)],
    "fence":      [(255, 0, 255), (32, 32, 40), (128, 112, 96), (64, 136, 232)],
    "newt":       [(255, 0, 255), (40, 24, 16), (112, 72, 40), (248, 136, 32)],
    "ui":         [(255, 0, 255), (16, 16, 16), (248, 248, 248), (248, 72, 72)],
}
# BG palettes: 4 real colors
BG = {
    "desert":  [(240, 216, 160), (184, 144, 96), (112, 96, 72), (40, 32, 24)],
    "scrub":   [(240, 216, 160), (136, 168, 72), (64, 104, 48), (32, 40, 24)],
    "granite": [(208, 208, 200), (152, 152, 144), (88, 88, 88), (32, 32, 40)],
    "forest":  [(144, 192, 96), (80, 144, 64), (40, 88, 48), (16, 40, 24)],
    "creek":   [(168, 216, 240), (88, 160, 216), (40, 88, 160), (16, 32, 72)],
}
OBJ = {k: [snap(c) for c in v] for k, v in OBJ.items()}
BG = {k: [snap(c) for c in v] for k, v in BG.items()}

# ---------------------------------------------------------------- player (ranger kid w/ camera)
HAT = [
    ".....111111.....",
    "....12222221....",
    "...1222222221...",
]
DOWN_BODY = [
    "..111111111111..",
    "...1333333331...",
    "...1313333131...",
    "...1333333331...",
    "....13333331....",
    "...1122222211...",
    "..122111111221..",
    "..123113311321..",
    "...1211111121...",
    "...1222222221...",
]
UP_BODY = [
    "..111111111111..",
    "...1111111111...",
    "...1111111111...",
    "...1311111131...",
    "....13333331....",
    "...1122222211...",
    "..122222222221..",
    "..321111111123..",
    "...1211111121...",
    "...1222222221...",
]
LEGS_A = ["....12211221....", "....111..111....", "................"]
LEGS_B = ["....12211221....", "....111..11.....", "................"]
SIDE = [
    ".....111111.....",
    "....12222221....",
    "...1222222221...",
    "...11111111111..",
    "...1113333331...",
    "...1113331331...",
    "...1133333331...",
    "....11333331....",
    "....12222211....",
    "....122221111...",
    "....122213321...",
    "....12221111....",
    "....1222221.....",
]
SIDE_A = [".....12121......", ".....11.11......", "................"]
SIDE_B = [".....1221.......", ".....111........", "................"]

def mirror(g):
    return [r[::-1] for r in g]

PLAYER = {
    "down_a": HAT + DOWN_BODY + LEGS_A,
    "down_b": HAT + DOWN_BODY + LEGS_B,
    "down_c": HAT + DOWN_BODY + mirror(LEGS_B),
    "up_a":   HAT + UP_BODY + LEGS_A,
    "up_b":   HAT + UP_BODY + LEGS_B,
    "up_c":   HAT + UP_BODY + mirror(LEGS_B),
    "right_a": SIDE + SIDE_A,
    "right_b": SIDE + SIDE_B,
    "left_a": mirror(SIDE + SIDE_A),
    "left_b": mirror(SIDE + SIDE_B),
}

# ---------------------------------------------------------------- critters (16x16, 1 palette each)
CRITTERS = {
    # Gopherus agassizii — CA state reptile (side view, facing right)
    "tortoise": [
        "................",
        "................",
        "................",
        "................",
        "......1111......",
        "....11232311....",
        "...1232323231...",
        "..123232323231..",
        "..1232323232311.",
        ".122222222222131",
        ".1111111111111..",
        "..1331....1331..",
        "..111.....111...",
        "................",
        "................",
        "................",
    ],
    # Sauromalus ater — chuckwalla (top-down, rusty tail)
    "chuckwalla": [
        "......1111......",
        ".....122221.....",
        ".....121121.....",
        "......1221......",
        "...1.122221.1...",
        "...1122222211...",
        "....12222221....",
        "....12222221....",
        "....12222221....",
        "...1122222211...",
        "...1.123321.1...",
        "......1331......",
        "......1331......",
        "......1331......",
        ".......11.......",
        "................",
    ],
    # Phrynosoma platyrhinos — desert horned lizard (top-down)
    "horned_lizard": [
        "................",
        ".....1.11.1.....",
        "......1111......",
        ".....131131.....",
        "..1..122221..1..",
        "...1123232211...",
        "..123232323231..",
        ".12323232323231.",
        "..123232323231..",
        "...1123232211...",
        "..1..122221..1..",
        "......1221......",
        ".......11.......",
        ".......1........",
        "................",
        "................",
    ],
    # Crotalus cerastes — sidewinder (S-curve, rattle)
    "sidewinder": [
        "................",
        "................",
        "..........1111..",
        ".........131131.",
        ".........122221.",
        "..........1221..",
        "....1111...121..",
        "...123321..121..",
        "..12211221.121..",
        "..121..1211221..",
        "..121...12321...",
        "..1221...111....",
        "...12211........",
        "....1233111.....",
        ".....1111.......",
        "................",
    ],
    # Anaxyrus punctatus — red-spotted toad (front view)
    "red_spotted_toad": [
        "................",
        "................",
        "................",
        "................",
        "....11....11....",
        "...1331..1331...",
        "...1311111131...",
        "..122222222221..",
        "..123222232221..",
        ".12222322222321.",
        ".12222222222221.",
        "1122322222232211",
        "1222111111112221",
        "1111........1111",
        "................",
        "................",
    ],
    # Sceloporus occidentalis — western fence lizard ("blue-belly")
    "fence_lizard": [
        ".......11.......",
        "......1221......",
        "......1221......",
        "...1..1221..1...",
        "....11322311....",
        "......1321......",
        "......1231......",
        "......1321......",
        "....11322311....",
        "...1..1221..1...",
        "......1221......",
        ".......121......",
        ".......11.......",
        "........1.......",
        "........1.......",
        "................",
    ],
    # Taricha torosa — California newt (orange belly peeks at the toes)
    "ca_newt": [
        "................",
        ".......11.......",
        "......1221......",
        ".....132231.....",
        "..33..1221..33..",
        "...3112222113...",
        "......1221......",
        "......1221......",
        "......1221......",
        "...3112222113...",
        "..33..1221..33..",
        ".......121......",
        ".......121......",
        "........11......",
        ".........1......",
        "..........1.....",
    ],
}
# Lampropeltis californiae — California kingsnake: sidewinder body, mirrored,
# re-banded black/cream by row, no rattle, round head (no horns).
def _kingsnake():
    g = [list(r[::-1]) for r in CRITTERS["sidewinder"]]
    g[13] = list("....1112221.....")
    g[14] = list("......111.......")
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            if ch in "23" and y >= 5:
                row[x] = "3" if (y // 2) % 2 == 0 else "2"
    g[2] = list("..1111..........")
    g[3] = list(".122221.........")
    g[4] = list(".131131.........")
    return ["".join(r) for r in g]
CRITTERS["kingsnake"] = _kingsnake()

CRITTER_PAL = {
    "tortoise": "tortoise", "chuckwalla": "chuckwalla", "horned_lizard": "horned",
    "sidewinder": "sidewinder", "red_spotted_toad": "toad", "kingsnake": "kingsnake",
    "fence_lizard": "fence", "ca_newt": "newt",
}

# ---------------------------------------------------------------- UI sprites
UI = {
    # viewfinder corner (top-left); mirror H/V in hardware for the other three
    "vf_corner": [
        "1111111.........",
        "1222221.........",
        "12111111........",
        "121.............",
        "121.............",
        "121.............",
        "111.............",
        "................",
        "................", "................", "................", "................",
        "................", "................", "................", "................",
    ],
    # focus reticle: red when locked
    "reticle": [
        "................",
        "................",
        "......3333......",
        "....33....33....",
        "...3........3...",
        "...3........3...",
        "..3....11....3..",
        "..3...1221...3..",
        "..3...1221...3..",
        "..3....11....3..",
        "...3........3...",
        "...3........3...",
        "....33....33....",
        "......3333......",
        "................",
        "................",
    ],
    # "!" spotted bubble
    "alert": [
        "....11111111....",
        "...1222222221...",
        "..122223322221..",
        "..122223322221..",
        "..122223322221..",
        "..122223322221..",
        "..122222222221..",
        "..122223322221..",
        "...1222222221...",
        "....11112111....",
        ".......121......",
        "........1.......",
        "................", "................", "................", "................",
    ],
    # camera icon for HUD / menu
    "camera": [
        "................",
        "................",
        ".....1111.......",
        "..111122111111..",
        "..122222222231..",
        "..121111112221..",
        "..121222211221..",
        "..121232321221..",
        "..121233321221..",
        "..121222221221..",
        "..122111112221..",
        "..122222222221..",
        "..111111111111..",
        "................", "................", "................",
    ],
}

# ---------------------------------------------------------------- BG tiles (16x16 metatiles)
def noise_tile(seed, base, specks, density):
    rnd = random.Random(seed)
    rows = []
    for _ in range(16):
        row = ""
        for _ in range(16):
            r = rnd.random()
            pick = base
            acc = 0
            for idx, p in zip(specks, density):
                acc += p
                if r < acc:
                    pick = idx
                    break
            row += str(pick)
        rows.append(row)
    return rows

TILES = {
    "sand":      ("desert", noise_tile(1, 0, [1, 2], [0.06, 0.01])),
    "sand_b":    ("desert", noise_tile(2, 0, [1, 2], [0.10, 0.02])),
    "trail":     ("desert", noise_tile(3, 1, [0, 2], [0.12, 0.04])),
    "rock": ("desert", [
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000033333300000",
        "0003311111133000",
        "0031111111111300",
        "0311111111211130",
        "0311121111111130",
        "3111111111111113",
        "3111111112111123",
        "3211111111111123",
        "3221111111111223",
        "0322222222222230",
        "0033333333333300",
        "0000000000000000",
        "0000000000000000",
    ]),
    # rock tipped up/over — dark damp soil revealed where critters hide
    "rock_flipped": ("desert", [
        "0000000000033330",
        "0000000003311113",
        "0000000031111123",
        "0000000031121123",
        "0000000003111230",
        "0000000000322300",
        "0000222222033000",
        "0022222222220000",
        "0222322223222000",
        "0222222222222000",
        "0223222232222000",
        "0222222222222000",
        "0022222322220000",
        "0000222222200000",
        "0000000000000000",
        "0000000000000000",
    ]),
    "creosote": ("scrub", [
        "0000000000000000",
        "0000002200000000",
        "0002212120220000",
        "0021121212112000",
        "0212112121121200",
        "0211212112112120",
        "2121121211211220",
        "2112212122112120",
        "0221121211212200",
        "0022212121122000",
        "0000223232200000",
        "0000003330000000",
        "0000000300000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ]),
    "boulder": ("granite", [
        "0000000000000000",
        "0000033333000000",
        "0003300000330000",
        "0030000000013000",
        "0300000000011300",
        "0300100000001130",
        "3000000000011113",
        "3000000000111113",
        "3100000001111123",
        "3110000011111223",
        "3111111111112223",
        "0311111111122230",
        "0332211112222330",
        "0003332222233300",
        "0000003333300000",
        "0000000000000000",
    ]),
    "pine_grass": ("forest", noise_tile(4, 0, [1, 2], [0.15, 0.04])),
    "creek":     ("creek", noise_tile(5, 1, [0, 2], [0.08, 0.10])),
}

# 16x32 tall trees
TALL = {
    "joshua_tree": ("scrub", [
        "0000000000000000",
        "0020200000202000",
        "0222220002222200",
        "0212120000212120",
        "0022200000222000",
        "0003000000030000",
        "0003000000300000",
        "0000300003000000",
        "0000030030020200",
        "0000003300222220",
        "0000003302121200",
        "0000003330222000",
        "0000003333300000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000003330000000",
        "0000033333000000",
        "0000333133300000",
        "0000000000000000",
        "0000000000000000", "0000000000000000", "0000000000000000",
        "0000000000000000", "0000000000000000", "0000000000000000",
    ]),
    "pine": ("forest", [
        "0000000330000000",
        "0000003223000000",
        "0000032222300000",
        "0000322122230000",
        "0003222222223000",
        "0000032222300000",
        "0000322221230000",
        "0003221222223000",
        "0032222222222300",
        "0000322222230000",
        "0003222212223000",
        "0032212222222300",
        "0322222222212230",
        "3222222122222223",
        "0003222222223000",
        "0032222222212300",
        "0322122222222230",
        "3222222222222223",
        "3333333333333333",
        "0000000330000000",
        "0000000330000000",
        "0000000330000000",
        "0000003333000000",
        "0000000000000000",
        "0000000000000000", "0000000000000000", "0000000000000000", "0000000000000000",
        "0000000000000000", "0000000000000000", "0000000000000000", "0000000000000000",
    ]),
}


# Original notebook font; editable alongside every other pixel grid.
FONT = {'A': '01110 10001 10001 11111 10001 10001 10001', 'B': '11110 10001 10001 11110 10001 10001 11110', 'C': '01111 10000 10000 10000 10000 10000 01111', 'D': '11110 10001 10001 10001 10001 10001 11110', 'E': '11111 10000 10000 11110 10000 10000 11111', 'F': '11111 10000 10000 11110 10000 10000 10000', 'G': '01111 10000 10000 10111 10001 10001 01111', 'H': '10001 10001 10001 11111 10001 10001 10001', 'I': '11111 00100 00100 00100 00100 00100 11111', 'J': '00111 00010 00010 00010 10010 10010 01100', 'K': '10001 10010 10100 11000 10100 10010 10001', 'L': '10000 10000 10000 10000 10000 10000 11111', 'M': '10001 11011 10101 10101 10001 10001 10001', 'N': '10001 11001 10101 10011 10001 10001 10001', 'O': '01110 10001 10001 10001 10001 10001 01110', 'P': '11110 10001 10001 11110 10000 10000 10000', 'Q': '01110 10001 10001 10001 10101 10010 01101', 'R': '11110 10001 10001 11110 10100 10010 10001', 'S': '01111 10000 10000 01110 00001 00001 11110', 'T': '11111 00100 00100 00100 00100 00100 00100', 'U': '10001 10001 10001 10001 10001 10001 01110', 'V': '10001 10001 10001 10001 10001 01010 00100', 'W': '10001 10001 10001 10101 10101 11011 10001', 'X': '10001 10001 01010 00100 01010 10001 10001', 'Y': '10001 10001 01010 00100 00100 00100 00100', 'Z': '11111 00001 00010 00100 01000 10000 11111', '0': '01110 10001 10011 10101 11001 10001 01110', '1': '00100 01100 00100 00100 00100 00100 01110', '2': '01110 10001 00001 00110 01000 10000 11111', '3': '11110 00001 00001 01110 00001 00001 11110', '4': '00010 00110 01010 10010 11111 00010 00010', '5': '11111 10000 10000 11110 00001 00001 11110', '6': '01110 10000 10000 11110 10001 10001 01110', '7': '11111 00001 00010 00100 01000 01000 01000', '8': '01110 10001 10001 01110 10001 10001 01110', '9': '01110 10001 10001 01111 00001 00001 01110', '!': '00100 00100 00100 00100 00100 00000 00100', '?': '01110 10001 00001 00010 00100 00000 00100', ':': '00000 00100 00100 00000 00100 00100 00000', '.': '00000 00000 00000 00000 00000 00110 00110', '-': '00000 00000 00000 11111 00000 00000 00000', '/': '00001 00001 00010 00100 01000 10000 10000', '+': '00000 00100 00100 11111 00100 00100 00000', '>': '10000 01000 00100 00010 00100 01000 10000', '<': '00001 00010 00100 01000 00100 00010 00001', '*': '00000 10101 01110 11111 01110 10101 00000', '[': '01110 01000 01000 01000 01000 01000 01110', ']': '01110 00010 00010 00010 00010 00010 01110', '=': '00000 00000 11111 00000 11111 00000 00000', '|': '00100 00100 00100 00100 00100 00100 00100', '_': '00000 00000 00000 00000 00000 00000 11111'}
# Original5x7 punctuation inexistingASCII slots; no extra tiles or copiedfont.
FONT.update({"'":"00100 00100 01000 00000 00000 00000 00000",
             ",":"00000 00000 00000 00000 00000 00100 01000",
             "^":"00100 01110 11111 00000 00000 00000 00000",
             "@":"01110 10001 10111 10101 10111 10000 01110"})

def make_font():
    im = Image.new("P", (128, 48), 0)
    im.putpalette([240,232,200, 184,144,96, 96,88,64, 32,40,32] + [0]*756)
    for n in range(96):
        for y,row in enumerate(FONT.get(chr(n+32), "00000 "*6+"00000").split()):
            for x,v in enumerate(row):
                if v=="1": im.putpixel(((n%16)*8+x+1,(n//16)*8+y),3)
    im.save(f"{OUT}/field_font.png")

# ---------------------------------------------------------------- deluxe native art
# Original authored pixels. All detail stays on the actual GBC grid, with
# three opaque sprite colors and four colors per background tile.
from PIL import ImageDraw

def native_grid(im):
    return [''.join(str(im.getpixel((x,y))) for x in range(im.width)) for y in range(im.height)]

def native_canvas(w,h,palette):
    im=Image.new('P',(w,h),0)
    im.putpalette(sum((list(c) for c in palette),[])+[0]*(768-len(palette)*3))
    return im

# 16x24 explorer: readable hat band, eyes, scarf, camera lens, shoulder strap,
# pockets, a loaded backpack and alternating boot silhouettes.
DELUXE_DOWN = [
 '................','.....111111.....','....12333321....','...1223333221...',
 '...1222222221...','..111111111111..','...1333333331...','...1313333131...',
 '...1333333331...','....13322331....','....11133111....','...1232112321...',
 '..132221122231..','..132111111231..','..131233332131..','..131231132131..',
 '...1223333221...','...1221111221...','....12222221....','....12211221....',
 '....12311321....','....121..121....','...1111..1111...','................']
DELUXE_UP = [
 '................','.....111111.....','....12333321....','...1223333221...',
 '...1222222221...','..111111111111..','...1112222111...','...1122222211...',
 '...1332222331...','....13333331....','...1121111211...','..132123321231..',
 '..132122221231..','..132122221231..','..131133331131..','..131122221131..',
 '...1121111211...','...1222222221...','....12222221....','....12211221....',
 '....12311321....','....121..121....','...1111..1111...','................']
DELUXE_SIDE = [
 '................','.....111111.....','....12333321....','...1223333221...',
 '...1222222221...','...11111111111..','...1123333331...','...1123331331...',
 '...11233333331..','...1123332231...','....11133111....','...11222321.....',
 '..122122321.....','..12212211111...','..12212123331...','..12212123131...',
 '..11112223331...','...1122211111...','....1222221.....','....1221221.....',
 '....1231231.....','....121.121.....','...1111.1111....','................']

def walking(grid,step):
    g=[list(r) for r in grid]
    if step:
        for y in range(20,24):g[y]=list('................')
        feet=['....12311321....','....121..11.....','...1111.........','........1111....']
        for k,row in enumerate(feet):g[20+k]=list(row[::-1] if step==2 else row)
    return [''.join(r) for r in g]

PLAYER={}
for direction,g in [('down',DELUXE_DOWN),('up',DELUXE_UP),('right',DELUXE_SIDE)]:
    for n in range(3):PLAYER[direction+'_'+chr(97+n)]=walking(g,n)
for n in range(3):PLAYER['left_'+chr(97+n)]=mirror(PLAYER['right_'+chr(97+n)])
# Different silhouettes for future local characters, not palette-only clones.
NPCS={'field_ranger':DELUXE_UP,'trail_buddy':DELUXE_DOWN}

# Ground color is shared at zero to eliminate pasted-on square scenery.
BG['granite'][0]=BG['desert'][0]
BG['creek']=[BG['desert'][0],snap((152,208,224)),snap((48,120,168)),snap((40,56,64))]
BG['camp']=[BG['desert'][0],snap((232,200,128)),snap((64,120,112)),snap((32,40,32))]

# Dedicated 48px portraits preserve each starter silhouette but add anatomy,
# shell plates, bands, brows, toes and intentional light/shadow pixel clusters.
def wildlife_portrait(name):
    im=native_canvas(48,48,OBJ[CRITTER_PAL[name]])
    d=ImageDraw.Draw(im)
    def path(points,color,width=1):d.line(points,fill=color,width=width)
    def oval(box,color,outline=1):d.ellipse(box,fill=color,outline=outline)
    if name=='tortoise':
        oval((7,11,36,33),2);d.polygon([(8,31),(9,24),(15,31),(33,25),(36,32)],fill=1)
        oval((35,23,44,29),3);d.rectangle((34,26,37,30),fill=2);d.point((41,25),fill=1)
        for x in [10,29]:d.polygon([(x,31),(x+5,31),(x+4,39),(x-1,39)],fill=2,outline=1);path([(x,36),(x+3,36)],3)
        for box in [(12,16,21,24),(22,15,30,23),(17,25,27,31)]:
            x,y,x2,y2=box;d.polygon([(x,y+3),(x+3,y),(x2-2,y),(x2,y+4),(x2-3,y2),(x+2,y2)],fill=3,outline=1)
        path([(10,28),(12,20),(17,14),(25,13),(32,17)],3)
        path([(6,31),(2,33),(8,34)],1)
    elif name in ('chuckwalla','horned_lizard','fence_lizard','ca_newt'):
        fat=name in ('chuckwalla','horned_lizard');left=15 if fat else 20;right=33 if fat else 28
        # Four bent limbs, articulated digits, long tapering tail.
        for y in [20,30]:
            for side in [-1,1]:
                base=left if side<0 else right;end=base+side*9
                path([(base+side,y),(end,y-4),(end+side*2,y+1)],1,3)
                path([(base,y),(end,y-4)],3 if name=='ca_newt' else 2,1)
                for off in [-2,0,2]:path([(end+side*2,y+1),(end+side*4,y+off+2)],3 if name=='ca_newt' else 1)
        path([(24,31),(24,38),(29,42),(33,44),(35,44)],1,5)
        path([(24,32),(24,38),(29,42),(34,44)],3 if name in ('chuckwalla','ca_newt') else 2,3)
        oval((left,14,right,34),2)
        d.polygon([(19,15),(17,10),(20,5),(28,5),(31,10),(29,15)],fill=2,outline=1)
        path([(20,8),(22,7),(25,7),(27,8)],3)
        d.point((20,11),1);d.point((28,11),1)
        path([(21,14),(27,14)],1)
        if name=='horned_lizard':
            for x,y in [(18,6),(22,3),(27,3),(30,6)]:d.polygon([(x,y+4),(x-2,y-2),(x+2,y+1)],fill=1)
            for y in range(18,32,4):
                d.polygon([(left,y),(left-3,y+1),(left,y+3)],fill=1);d.polygon([(right,y),(right+3,y+1),(right,y+3)],fill=1)
                for x in range(left+3,right-2,4):d.polygon([(x,y),(x+2,y-1),(x+3,y+2)],fill=3)
        elif name=='chuckwalla':
            for y in range(18,31,3):path([(18,y),(21,y+1),(25,y),(29,y+1)],3 if y%2 else 1)
            path([(17,17),(16,23),(17,28)],3)
        elif name=='fence_lizard':
            for y in range(16,32,3):path([(20,y),(24,y+2),(28,y)],1)
            path([(21,20),(21,29)],3,2);path([(27,20),(27,29)],3,2)
        else:
            path([(22,16),(22,31)],3);path([(25,18),(25,28)],1)
            d.point((21,9),3);d.point((27,9),3)
    elif name in ('sidewinder','kingsnake'):
        points=[(6,37),(8,29),(18,27),(29,34),(38,32),(40,24),(34,20),(22,20),(16,14),(20,8),(30,8)]
        path(points,1,8);path(points,2 if name=='sidewinder' else 3,5)
        if name=='sidewinder':
            for x,y in [(8,32),(12,28),(18,28),(25,31),(34,33),(39,27),(37,22),(29,20),(22,19),(17,13),(22,8)]:
                d.rectangle((x-1,y-1,x+1,y+1),fill=1);d.point((x+2,y),3)
            d.polygon([(29,4),(38,4),(41,8),(37,13),(29,12),(27,8)],fill=2,outline=1)
            path([(30,5),(30,2)],1,2);path([(37,5),(37,2)],1,2)
            d.point((30,7),3);d.point((37,7),3);d.point((31,8),1);d.point((36,8),1)
            for y in range(36,43,2):d.rectangle((4,y,8,y+1),fill=3,outline=1)
        else:
            for a,b in [((8,28),(13,31)),((18,24),(17,30)),((25,28),(22,34)),((35,29),(35,35)),((37,23),(43,23)),((30,17),(30,23)),((20,16),(23,21)),((16,10),(21,13)),((25,5),(25,11))]:path([a,b],1,3)
            d.ellipse((27,4,39,12),fill=1);path([(29,6),(36,6)],3,2);d.point((37,7),3)
            path([(39,9),(44,10),(45,9)],2)
    elif name=='red_spotted_toad':
        oval((9,18,39,37),2);oval((10,12,21,25),2);oval((28,12,39,25),2)
        oval((12,14,20,21),3);oval((30,14,38,21),3);d.rectangle((15,17,19,18),fill=1);d.rectangle((31,17,35,18),fill=1)
        d.polygon([(13,29),(5,31),(3,39),(15,40),(20,35)],fill=2,outline=1)
        d.polygon([(35,29),(43,31),(45,39),(33,40),(28,35)],fill=2,outline=1)
        for x,y in [(17,24),(25,23),(31,26),(20,30),(28,31),(14,34),(34,35)]:d.rectangle((x,y,x+1,y+1),fill=3)
        path([(17,26),(23,28),(29,26)],1)
        for x in [5,8,11,36,39,42]:path([(x,37),(x-1,40)],1)
    return im

PORTRAITS={name:native_grid(wildlife_portrait(name)) for name in CRITTERS}

# Hand-composed metatiles use repeatable clusters rather than random noise.
def detailed_tile(name):
    palette='desert';im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im)
    if name in ('sand','sand_b','pebbles','dry_grass','flowers','tracks','mud'):
        if name=='mud':d.rectangle((0,0,15,15),fill=1)
        for x,y in [(2,3),(10,1),(13,11),(5,13)]:d.line([(x,y),(x+2,y)],fill=1 if name!='mud' else 2)
        if name=='sand_b':
            for y in [5,11]:d.line([(0,y),(4,y-1),(9,y),(15,y-1)],fill=1)
        if name=='pebbles':
            for x,y in [(2,5),(9,10),(12,3)]:d.ellipse((x,y,x+3,y+2),fill=2);d.point((x+1,y),fill=0)
        if name=='dry_grass':
            for x,y in [(3,9),(11,5)]:d.line([(x-2,y-3),(x,y),(x+2,y-4)],fill=2);d.line([(x,y-3),(x,y+1)],fill=1)
        if name=='flowers':
            for x,y in [(4,8),(11,12)]:d.line([(x,y),(x,y+3)],fill=2);d.rectangle((x-1,y-1,x+1,y+1),fill=1);d.point((x,y),fill=0)
        if name=='tracks':
            for x,y in [(3,3),(5,6),(7,9),(9,12)]:d.line([(x,y),(x+2,y+1)],fill=2)
    elif name.startswith('trail'):
        d.rectangle((0,0,15,15),fill=1)
        for x,y in [(1,1),(7,5),(12,10),(3,13)]:d.line([(x,y),(x+2,y)],fill=0);d.point((x+1,y+1),fill=2)
        if name=='trail_l':d.polygon([(0,0),(3,0),(2,5),(4,9),(2,15),(0,15)],fill=0)
        if name=='trail_r':d.polygon([(15,0),(12,0),(13,5),(11,9),(13,15),(15,15)],fill=0)
    elif name in ('rock','rock_flipped','boulder','crevice','burrow','camp'):
        if name=='camp':
            palette='camp';im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im)
            d.polygon([(0,13),(6,2),(10,2),(15,13)],fill=1,outline=3);d.polygon([(6,3),(11,13),(3,13)],fill=2)
            d.line([(6,3),(6,13)],fill=3);d.line([(0,14),(15,14)],fill=3);d.point((11,7),fill=0)
        elif name=='burrow':
            d.ellipse((1,4,14,14),fill=1,outline=2);d.ellipse((4,7,12,14),fill=3);d.line([(2,6),(5,4),(10,4)],fill=0)
            d.line([(5,14),(13,14)],fill=2)
        elif name=='rock_flipped':
            d.ellipse((0,6,13,14),fill=2);d.polygon([(8,1),(14,0),(15,6),(11,9),(7,5)],fill=1,outline=3)
            d.line([(10,2),(13,2),(14,5)],fill=0);d.point((4,10),fill=3);d.point((8,12),fill=1)
        else:
            palette='granite' if name in ('boulder','crevice') else 'desert';im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im)
            d.polygon([(1,12),(1,7),(5,3),(10,2),(14,6),(15,11),(12,14),(5,14)],fill=1,outline=3)
            d.polygon([(2,10),(6,8),(11,7),(14,11),(12,13),(6,13)],fill=2)
            d.line([(3,7),(6,4),(10,4),(12,6)],fill=0);d.line([(6,8),(8,6),(10,7)],fill=3)
            if name=='crevice':d.line([(8,4),(6,8),(9,10),(7,13)],fill=3,width=2)
    elif name in ('creosote','pine_grass','reeds'):
        palette='scrub';im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im)
        d.ellipse((2,11,14,14),fill=2)
        for a,b in [((8,12),(3,6)),((8,12),(12,5)),((8,12),(8,3))]:d.line([a,b],fill=3)
        for x,y in [(2,5),(5,2),(9,2),(11,5),(4,8),(9,8)]:
            d.ellipse((x,y,x+3,y+3),fill=2);d.line([(x,y),(x+2,y)],fill=1)
        if name=='reeds':
            im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im)
            for x in [3,7,12]:d.line([(x,14),(x,2)],fill=2);d.rectangle((x-1,2,x,5),fill=3);d.line([(x,11),(x+3,6)],fill=1)
    elif name.startswith('water') or name=='creek':
        palette='creek';im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im);d.rectangle((0,0,15,15),fill=2)
        for x,y in [(2,4),(9,10),(0,14)]:d.line([(x,y),(x+4,y),(x+5,y-1)],fill=1)
        if name!='creek':
            edge=name[6:]
            for side in edge:
                if side=='n':d.polygon([(0,0),(15,0),(15,3),(10,2),(6,4),(0,2)],fill=0);d.line([(0,3),(5,4),(10,3),(15,4)],fill=3)
                if side=='s':d.polygon([(0,15),(15,15),(15,12),(9,13),(4,11),(0,12)],fill=0);d.line([(0,11),(4,10),(9,12),(15,11)],fill=3)
                if side=='w':d.polygon([(0,0),(0,15),(3,15),(2,9),(4,4),(2,0)],fill=0);d.line([(3,0),(5,4),(3,9),(4,15)],fill=3)
                if side=='e':d.polygon([(15,0),(15,15),(12,15),(13,9),(11,4),(13,0)],fill=0);d.line([(12,0),(10,4),(12,9),(11,15)],fill=3)
    elif name=='log':
        palette='granite';im=native_canvas(16,16,BG[palette]);d=ImageDraw.Draw(im)
        d.polygon([(1,5),(13,3),(15,10),(3,13)],fill=2,outline=3);d.line([(3,6),(12,5)],fill=1);d.line([(4,9),(13,7)],fill=1);d.ellipse((0,5,5,12),fill=1,outline=3)
    return palette,native_grid(im)

DETAIL_TILE_ORDER=['sand','sand_b','trail','rock','rock_flipped','creosote','boulder','pine_grass','creek','pebbles','mud','flowers','dry_grass','tracks','trail_l','trail_r','crevice','burrow','camp','reeds','water_nw','water_ne','water_sw','water_se','log']
TILES={name:detailed_tile(name) for name in DETAIL_TILE_ORDER}
# Detailed bark, branching highlights and spiky leaf crowns, preserving original
# sixteen-pixel-wide / two-cell-tall collision silhouette.
tree=native_canvas(16,32,BG['scrub']);d=ImageDraw.Draw(tree)
d.ellipse((3,27,14,30),fill=2)
d.line([(8,28),(8,12),(5,8)],fill=3,width=3);d.line([(8,16),(12,12),(12,7)],fill=3,width=2)
d.line([(7,27),(7,15),(4,10)],fill=1);d.line([(11,13),(11,8)],fill=1)
for cx,cy in [(4,6),(12,5),(8,11),(12,14)]:
    for dx,dy in [(-3,-1),(-2,-4),(0,-4),(2,-3),(3,0),(-3,2),(1,3)]:d.line([(cx,cy),(max(0,min(15,cx+dx)),max(0,cy+dy))],fill=2)
    d.point((cx,cy),fill=1);d.point((cx-1,cy-1),fill=1)
TALL['joshua_tree']=('scrub',native_grid(tree))

# Sixteen regional palette/art kits, all at the native palette/tile grid. These
# are authored visual-kit showrooms for future maps, not implemented districts.
REGION_ART=[
 ('D01','MOJAVE',[(240,216,160),(184,144,96),(112,96,72),(40,32,24)],'desert'),
 ('D02','COLORADO DESERT',[(248,216,144),(200,152,80),(144,96,56),(64,40,32)],'desert'),
 ('D03','EASTERN BASIN',[(200,200,152),(152,152,104),(96,112,80),(40,56,48)],'basin'),
 ('D04','SIERRA FOOTHILLS',[(224,216,144),(168,168,80),(96,128,64),(40,64,40)],'oak'),
 ('D05','SIERRA HIGH COUNTRY',[(216,224,208),(160,184,160),(88,120,112),(32,56,64)],'alpine'),
 ('D06','SACRAMENTO VALLEY',[(216,224,152),(152,184,88),(80,136,72),(32,64,48)],'wetland'),
 ('D07','SAN JOAQUIN VALLEY',[(232,224,152),(192,176,96),(120,128,72),(48,64,40)],'grass'),
 ('D08','BAY AND DELTA',[(208,224,184),(136,176,128),(72,128,112),(32,64,64)],'wetland'),
 ('D09','CENTRAL COAST',[(224,216,168),(168,176,120),(96,136,104),(40,64,64)],'coast'),
 ('D10','SOUTH COAST',[(232,216,152),(176,160,88),(104,128,72),(48,64,48)],'coast'),
 ('D11','SOUTHERN MOUNTAINS',[(224,216,184),(160,160,112),(88,120,88),(40,56,56)],'oak'),
 ('D12','CHANNEL ISLANDS',[(224,224,176),(168,184,120),(88,136,112),(32,72,80)],'island'),
 ('D13','NORTH COAST',[(176,208,160),(104,152,104),(48,96,72),(16,40,40)],'redwood'),
 ('D14','KLAMATH MOUNTAINS',[(192,208,152),(120,160,96),(64,112,72),(24,48,40)],'forest'),
 ('D15','CASCADES',[(200,208,176),(136,160,120),(80,112,104),(32,48,56)],'volcanic'),
 ('D16','MODOC PLATEAU',[(208,208,152),(160,168,104),(104,128,88),(48,64,56)],'basin')]

REGION_LAYOUTS={'D01': ['GGSSSSSGGG', 'SCSSCTSSGS', 'SJSSTSSCSS', 'SjSSTTTTTT', 'SSSCTSSGSS', 'SCSSSSSCCS', 'GGSSGSSSGG'], 'D02': ['GSSSSCSSGG', 'SCSSTSSWWS', 'SSSSTSCWWS', 'TTTTTTTTTS', 'SCSSSCSSTS', 'SSCSSSSTCS', 'GSSSSSSSGG'], 'D03': ['GGGSSSSGGG', 'SSGSSCTSSG', 'SCSSSSTSSS', 'TTTTTTTTTT', 'SSSGSSSCSC', 'SGSSSSSCSS', 'GGSSGGSSGG'], 'D04': ['GGSSCSSCGG', 'SCSSSTSCSS', 'SSCSSTSSCS', 'TTTTTTTTTT', 'SCSSCTSSCS', 'SSSSSTSSSS', 'GGCSCSSCGG'], 'D05': ['GGGSSSSGGG', 'SGSSCTWWGS', 'SSSCTSWWSG', 'TTTTTTTTTT', 'SSGGSTSCSS', 'SCSSSTSSCS', 'GGGSSSSGGG'], 'D06': ['CSSSSCCSSC', 'SWWSTSSCWS', 'SWWSTSSWWS', 'TTTTTTTTTT', 'SCWWSTSCCS', 'SSWWSTSSCS', 'CCSSSCSSCC'], 'D07': ['SSCSSSSCCS', 'SCSSSTSSSS', 'SSSSSTSSCS', 'TTTTTTTTTT', 'SCSSSTSCSS', 'SSCSSTSSSS', 'GGSSCSSSGG'], 'D08': ['CSSWWWSSCC', 'SSSTWWWWSS', 'SCSTSSWWSC', 'TTTTTTTTTT', 'SCSSSWWSTS', 'SSCSWWWSTC', 'CCSSWWSSCC'], 'D09': ['GGGSSSSCGG', 'GWWSSCTSSS', 'GWWSCSTCSS', 'TTTTTTTTTT', 'SSCSSCTSSG', 'SCSSSSSCCG', 'GGSSCSSGGG'], 'D10': ['GGCCSSSSGG', 'SSCSSTSCSS', 'CSSSSTSSCS', 'TTTTTTTTTT', 'SCSSSTSCSS', 'SSSCCSSSCS', 'GGSSSSCCGG'], 'D11': ['GGGSSSSGGG', 'GSSCTSSCSG', 'SSSCTSSSGS', 'TTTTTTTTTT', 'SCSSSTSSCS', 'SSCSSSTSSS', 'GGSSSSCGGG'], 'D12': ['WWWSSSSWWW', 'WWSSTSSSWW', 'WSSCTSSCSW', 'TTTTTTTTTT', 'WSSSSCTSSW', 'WWSSSCSSWW', 'WWWSSSSWWW'], 'D13': ['CCSSSSSCCC', 'CSSSCSTWWC', 'SSCCSSTWWC', 'TTTTTTTTTT', 'CSCCSSTCSC', 'CCSSSSTSSC', 'CCCWWWCCCC'], 'D14': ['GGCCSSCCGG', 'CCSSSTSSCC', 'CSSSSTCCSC', 'TTTTTTTTTT', 'SCSSCTCSCC', 'CCSSSTSSCS', 'GGCCSSCCGG'], 'D15': ['GGGSSSSGGG', 'GGSCSTSSGG', 'SSSCSTSSCS', 'TTTTTTTTTT', 'SGSSSTSCCS', 'GSSSSSSSGG', 'GGGSSSSGGG'], 'D16': ['GGSSSCSSGG', 'SSCSSTSSCS', 'SCSSSTSSSG', 'TTTTTTTTTT', 'SSCSSTSCSS', 'SCSSSSSSCS', 'GGSSGGSSGG']}

# Fixed authored route, additional habitat layers and individual landmark
# compositions. Its rooms are not claims about exact geographical localities.
def region_showroom(region,map_context=None):
    rid,name,ground,kind=region;ground=[snap(c) for c in ground]
    palettes=[ground,[ground[0],snap((152,184,96)),snap((72,128,72)),snap((24,64,48))],
              [ground[0],snap((184,184,160)),snap((120,128,120)),snap((48,64,64))],
              [ground[0],snap((152,208,224)),snap((64,144,176)),snap((24,64,96))]]
    im=Image.new('RGB',(160,144),ground[0]);detail=Image.new('P',(160,112),0)
    # A P image needs an explicit palette or PNG serialization can collapse
    # indices2/3 to1. Runtime palettes are per8px tile; these four neutral entries
    # preserve the exact native index values rather than color-quantizing them.
    detail.putpalette([0,0,0,8,8,8,16,16,16,24,24,24]+[0]*756)
    attrs=[0]*280
    layout=REGION_LAYOUTS[rid]
    # W is authored water in every district, including desert/basin/forest.
    # Regional color themes never turn a valid spring into dry land.
    water=True
    tile_names=[]
    for y,row in enumerate(layout):
        for x,c in enumerate(row):
            tile='boulder' if c=='G' else 'creosote' if c=='C' else 'trail' if c=='T' else 'creek' if c=='W' and water else ['sand','sand_b','pebbles','dry_grass','flowers'][(x+y*3)%5]
            tile_names.append(tile)
            p,g=TILES[tile];family=2 if c=='G' else 1 if c=='C' else 3 if c=='W' and water else 0
            proposal=terrain_tile(rid,kind,map_context,c,x,y)
            if proposal:g,family=proposal
            a=grid_img(g,palettes[family],False).convert('RGB');im.paste(a,(x*16,16+y*16))
            for iy in range(16):
                for ix in range(16):detail.putpixel((x*16+ix,y*16+iy),int(g[iy][ix]))
            for ty in range(2):
                for tx in range(2):attrs[(y*2+ty)*20+x*2+tx]=family
    # Each landmark is composed on its native grid, with one family per 8px tile.
    layer=native_canvas(32,48,palettes[1]);pen=ImageDraw.Draw(layer)
    if kind=='redwood':
        # Full native32x48 taperedbole with layered bark and branch fans.
        pen.polygon([(10,0),(22,0),(22,28),(27,46),(3,46),(9,28)],fill=2,outline=3)
        for x in (11,14,18,21):pen.line([(x,1),(x-1,27),(x-3 if x<16 else x+3,45)],fill=3)
        pen.line([(12,2),(11,25),(8,44)],fill=1);pen.line([(19,2),(19,26),(22,43)],fill=1)
        for y in (5,15):
            for side in (-1,1):
                pen.line([(16,y),(16+side*14,y+6)],fill=3,width=2)
                for step in (4,8,12):pen.line([(16+side*step,y+step//2),(16+side*(step+2),y+step//2-3)],fill=2)
    elif kind in ('forest','alpine','volcanic','oak'):
        if kind=='oak':
            pen.ellipse((0,1,31,25),fill=2,outline=3);pen.ellipse((3,3,15,15),fill=1);pen.ellipse((17,6,28,17),fill=1)
        else:
            for y,w in [(2,5),(9,9),(17,13),(26,16)]:
                pen.polygon([(16,y),(16-w,y+12),(16+w-1,y+12)],fill=2,outline=3)
                pen.line([(16,y+1),(16-w+3,y+10)],fill=1)
        pen.rectangle((13,23,18,46),fill=3);pen.line([(14,26),(14,44)],fill=1)
        if kind=='redwood':pen.line([(17,25),(17,44)],fill=2)
    elif rid=='D02':
        pen.line([(15,45),(17,14)],fill=3,width=4);pen.line([(15,42),(16,17)],fill=1)
        for ex,ey in [(1,7),(3,16),(8,3),(25,2),(31,10),(29,19)]:
            pen.line([(17,13),(ex,ey)],fill=2,width=3);pen.line([(17,12),(ex,ey-1)],fill=1)
        pen.ellipse((13,11,20,18),fill=3)
    elif kind=='basin':
        # Original wind-shapedjuniper/sage landscape crown, crooked groundedbole.
        pen.line([(16,45),(13,33),(17,21),(14,13)],fill=3,width=5)
        pen.line([(15,43),(12,33),(16,22)],fill=1)
        for box in ((0,17,14,31),(9,6,26,24),(18,19,31,32)):
            pen.ellipse(box,fill=2,outline=3)
            pen.line([(box[0]+4,box[1]+3),(box[2]-4,box[1]+2)],fill=1)
        pen.line([(14,25),(4,21)],fill=3,width=2);pen.line([(17,30),(25,26)],fill=3,width=2)
    elif kind=='desert':
        for x,y in [(8,4),(23,10),(16,20)]:
            pen.line([(x,46),(x,y)],fill=3,width=3)
            for dx,dy in [(-6,-4),(6,-5),(-6,1),(5,2)]:pen.line([(x,y),(x+dx,y+dy)],fill=2,width=2)
            pen.point((x,y),fill=1)
    elif kind in ('coast','island'):
        pen.polygon([(0,35),(6,15),(17,4),(29,20),(31,40)],fill=2,outline=3)
        pen.line([(9,16),(17,6),(25,20)],fill=1);pen.line([(4,33),(14,29),(26,32)],fill=3)
        if kind=='island':pen.line([(21,6),(21,1)],fill=3);pen.line([(18,2),(24,2)],fill=3)
    else:
        for x in [3,10,18,26]:
            pen.line([(x,46),(x,8)],fill=2);pen.rectangle((x-1,5,x+1,13),fill=3);pen.line([(x,29),(x+4,17)],fill=1)
    revised=organic_primary(rid,kind)
    if revised is not None:layer=revised
    protected={(0,3),(9,3)}
    if map_context and map_context.get('art_protected_cells'):
        protected.update(map(tuple,map_context['art_protected_cells']))
    if map_context and not map_context.get('art_protected_cells'):
        if map_context.get('camp'):
            cx,cy=map_context['camp'];protected.add((cx,cy))
            protected.update((cx+dx,cy+dy) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)))
        for sx,sy in map_context.get('observation_tiles',[]):
            protected.add((sx,sy));protected.update((sx+dx,sy+dy) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)))
    def can_stamp(px,py,width,height):
        if px<0 or py<0 or px+width>160 or py+height>112:return False
        cells={(x//16,y//16) for y in range(py,py+height) for x in range(px,px+width)}
        # Large opaque scenery must agree with actual collision. No props over
        # water, paths, camps, arrival cells, observation sites or standing cells.
        return all((x,y) not in protected and layout[y][x] in 'GJj' for x,y in cells)
    def stamp(prop,px,py,family):
        assert px%8==py%8==0 and can_stamp(px,py,prop.width,prop.height)
        for ty in range(prop.height//8):
            for tx in range(prop.width//8):
                gx=px//8+tx;gy=py//8+ty
                attrs[gy*20+gx]=family
                for y in range(8):
                    for x in range(8):
                        vx=gx*8+x;vy=gy*8+y;v=prop.getpixel((tx*8+x,ty*8+y))
                        if not v:v=detail.getpixel((vx,vy))
                        detail.putpixel((vx,vy),v);im.putpixel((vx,vy+16),palettes[family][v])
    def place_prop(prop,family,preferred):
        candidates=[(x*16,y*16) for y in range(7) for x in range(10)]
        candidates.sort(key=lambda xy:abs(xy[0]-preferred[0])+abs(xy[1]-preferred[1]))
        for px,py in candidates:
            if can_stamp(px,py,prop.width,prop.height):stamp(prop,px,py,family);return
        # Keep a complete small silhouette inside a real blocked16px tile if a
        # larger footprint cannot fit. Never chop scenery across walkable cells.
        small=prop.resize((16,16),Image.Resampling.NEAREST)
        for px,py in candidates:
            if can_stamp(px,py,16,16):stamp(small,px,py,family);return
        # No honest location: omit this decorative prop rather than fake collision.
    hero=(map_context or {}).get('landmark_primary')
    preferred=(hero['x']*16,hero['y']*16) if hero else (16,0)
    place_prop(layer,1,preferred)
    prop=native_canvas(32,32,palettes[2]);pen=ImageDraw.Draw(prop)
    if rid in ('D01','D03','D05','D11','D15','D16'):
        pen.polygon([(0,29),(0,12),(6,7),(12,9),(18,2),(27,5),(31,13),(31,30)],fill=2,outline=3)
        pen.polygon([(2,13),(7,9),(12,11),(19,4),(26,7),(27,11),(18,10),(10,14)],fill=1)
        for y in [17,23,28]:pen.line([(1,y),(9,y-2),(18,y),(30,y-1)],fill=3)
        pen.line([(18,11),(16,17),(21,22),(19,30)],fill=3)
        if rid=='D05':pen.polygon([(5,9),(7,8),(13,10),(18,3),(26,6),(23,8),(19,6),(14,12)],fill=0)
        if rid=='D15':
            for x in [5,12,22,28]:pen.line([(x,13),(x-2,29)],fill=3,width=2)
    elif rid in ('D02','D04','D07','D10'):
        pen.rectangle((2,23,29,27),fill=2);pen.line([(3,23),(28,23)],fill=1)
        for x in [5,13,24]:pen.rectangle((x,17,x+1,31),fill=3)
        if rid in ('D04','D10'):
            pen.ellipse((4,0,28,20),fill=2,outline=3);pen.ellipse((6,2,16,11),fill=1)
            pen.rectangle((14,14,18,31),fill=3);pen.line([(15,15),(15,29)],fill=1)
        else:
            for x,y in [(4,7),(12,4),(25,6)]:pen.line([(x,y),(x+2,18)],fill=3);pen.line([(x-2,y-1),(x,y),(x+3,y-2)],fill=2)
    elif rid in ('D06','D08'):
        pen.polygon([(0,10),(31,10),(31,25),(0,25)],fill=2,outline=3)
        for x in range(2,31,4):pen.line([(x,11),(x,24)],fill=1)
        pen.line([(0,7),(31,7)],fill=3);pen.line([(0,28),(31,28)],fill=3)
        for x in [2,27]:pen.line([(x,3),(x,31)],fill=3)
    elif rid in ('D09','D12'):
        pen.polygon([(0,30),(3,17),(13,9),(23,12),(31,24),(31,31)],fill=2,outline=3)
        pen.line([(4,18),(13,11),(23,14)],fill=1)
        pen.line([(1,27),(10,26),(13,28),(23,27),(30,29)],fill=0)
        pen.line([(3,30),(11,29),(19,31)],fill=1)
    else:
        pen.polygon([(1,19),(27,11),(31,18),(5,28)],fill=2,outline=3)
        pen.line([(5,21),(27,15)],fill=1);pen.ellipse((0,19,7,28),fill=1,outline=3)
        for x in [8,17,24]:pen.line([(x,17),(x-3,8),(x+1,11),(x+3,5)],fill=2)
        if rid=='D13':pen.rectangle((22,0,31,18),fill=3);pen.line([(24,1),(24,16)],fill=1)
    revised=organic_secondary(rid)
    if revised is not None:prop=revised
    secondary=(map_context or {}).get('landmark_secondary')
    preferred=(secondary['x']*16,secondary['y']*16) if secondary else (112,64)
    place_prop(prop,1 if rid in ('D04','D06','D08','D10') else 2,preferred)
    # Labels/HUD from the original field font, preserving a readable quiet margin.
    for n,ch in enumerate(name[:20]):
        for y,row in enumerate(FONT.get(ch,'00000 '*6+'00000').split()):
            for x,v in enumerate(row):
                if v=='1':im.putpixel((n*8+x+1,y+3),ground[3])
    return im,detail,attrs,palettes

def export_deluxe():
    for name,g in PORTRAITS.items():
        im=native_canvas(48,48,OBJ[CRITTER_PAL[name]])
        for y,row in enumerate(g):
            for x,ch in enumerate(row):im.putpixel((x,y),int(ch))
        im.save(f'{OUT}/portrait_{name}.png')
        im.resize((32,32),Image.Resampling.NEAREST).save(f'{OUT}/portrait32_{name}.png')
    sheet=Image.new('RGB',(4*56,2*64),BG['desert'][0])
    for i,name in enumerate(PORTRAITS):
        im=grid_img(PORTRAITS[name],OBJ[CRITTER_PAL[name]],True)
        sheet.paste(im,((i%4)*56+4,(i//4)*64+4),im)
    sheet.resize((sheet.width*3,sheet.height*3),Image.Resampling.NEAREST).save(f'{OUT}/portraits_3x.png')
    for room,layout in enumerate([
        [['crevice','sand','pebbles','sand','sand','dry_grass','sand','creosote'],['sand_b','sand','sand','sand','sand','sand','sand','sand_b'],['dry_grass','sand','sand','sand','sand','sand','sand','pebbles'],['sand','pebbles','sand','sand','sand','sand','sand','crevice']],
        [['reeds','sand','sand','sand','sand','sand','sand','boulder'],['mud','sand','sand','sand','sand','sand','sand','dry_grass'],['sand','sand','sand','sand','sand','sand','sand','reeds'],['water_nw','water_n','sand','sand','sand','sand','water_n','water_ne']]
    ]):
        im=Image.new('P',(128,64),0);attrs=[]
        for y,row in enumerate(layout):
            for x,name in enumerate(row):
                if name not in TILES:name='creek'
                palette,g=TILES[name]
                for iy,r in enumerate(g):
                    for ix,v in enumerate(r):im.putpixel((x*16+ix,y*16+iy),int(v))
        for ty in range(8):
            for tx in range(16):
                name=layout[ty//2][tx//2]
                palette=TILES.get(name,TILES['creek'])[0]
                attrs.append({'desert':0,'scrub':1,'granite':2,'forest':3,'creek':4,'camp':6}[palette])
        im.putpalette(sum((list(c) for c in BG['desert']),[])+[0]*756)
        im.save(f'{OUT}/photo_habitat_{room}.png')
        with open(f'{OUT}/photo_habitat_{room}.json','w') as f:json.dump(attrs,f)
    # Connected formations replace rows of repeated isolated round rocks.
    outcrop=native_canvas(32,16,BG['granite']);pen=ImageDraw.Draw(outcrop)
    pen.polygon([(0,13),(2,6),(7,2),(12,3),(17,1),(23,3),(28,7),(31,6),(31,14),(0,15)],fill=2,outline=3)
    pen.polygon([(3,6),(8,3),(12,5),(18,3),(23,5),(25,8),(18,7),(11,8)],fill=1)
    pen.line([(1,11),(10,10),(17,12),(30,10)],fill=3)
    pen.line([(13,5),(11,9),(15,12),(14,14)],fill=3)
    pen.line([(22,6),(20,10),(23,13)],fill=3)
    outcrop.save(f'{OUT}/outcrop.png')
    horizon=native_canvas(160,8,BG['granite']);pen=ImageDraw.Draw(horizon)
    pen.polygon([(0,8),(0,6),(12,4),(19,4),(22,2),(32,2),(35,5),(50,6),(58,3),(66,3),(70,5),(79,4),(89,1),(94,1),(106,5),(117,4),(130,2),(143,3),(153,6),(159,5),(159,8)],fill=2)
    pen.line([(0,6),(12,4),(19,4),(22,2),(32,2),(35,5),(50,6),(58,3),(66,3),(70,5),(79,4),(89,1),(94,1),(106,5),(117,4),(130,2),(143,3),(153,6),(159,5)],fill=1)
    horizon.save(f'{OUT}/horizon.png')
    logo=native_canvas(72,8,BG['desert'])
    for n,ch in enumerate('ROCK FLIP'):
        for y,row in enumerate(FONT.get(ch,'00000 '*6+'00000').split()):
            for x,v in enumerate(row):
                if v=='1':logo.putpixel((n*8+x+1,y),3)
    logo.resize((144,16),Image.Resampling.NEAREST).save(f'{OUT}/title_logo.png')
    cycle=native_canvas(64,32,BG['creek'])
    for k,name in enumerate(['water_nw','water_ne','water_sw','water_se']):
        original=TILES[name][1]
        for frame in range(2):
            for y,row in enumerate(original):
                for x,ch in enumerate(row):
                    v=int(ch)
                    if frame and v in (1,2):
                        v=2
                        if (y in (5,11) and (x+frame*2)%9 in (2,3,4)):v=1
                    cycle.putpixel((k*16+x,frame*16+y),v)
    cycle.save(f'{OUT}/water_cycle.png')
    manifest=[];contact=Image.new('RGB',(4*160,4*160),(32,40,32))
    for i,region in enumerate(REGION_ART):
        im,indices,attrs,palettes=region_showroom(region)
        im.save(f'{OUT}/region_{region[0]}.png')
        indices.save(f'{OUT}/region_{region[0]}_indices.png')
        contact.paste(im,((i%4)*160,(i//4)*160))
        manifest.append({'id':region[0],'name':region[1],'kind':region[3],'status':'authored_visual_kit_not_playable_district','palette_slots':palettes,'attributes':attrs,'tilemap_size':[20,14]})
    contact.resize((1280,1280),Image.Resampling.NEAREST).save(f'{OUT}/all_regions_2x.png')
    with open(f'{OUT}/region_art_manifest.json','w') as f:json.dump(manifest,f,indent=2)


# ---------------------------------------------------------------- render helpers
def check(name, g, h=16):
    assert len(g) == h, f"{name}: {len(g)} rows"
    for i, r in enumerate(g):
        assert len(r) == 16, f"{name} row {i}: len {len(r)} -> {r!r}"

def grid_img(g, pal, transparent):
    h = len(g)
    im = Image.new("RGBA", (len(g[0]), h))
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            i = 0 if ch == "." else int(ch)
            if transparent and i == 0:
                im.putpixel((x, y), (0, 0, 0, 0))
            else:
                im.putpixel((x, y), pal[i] + (255,))
    return im

def indexed_sheet(grids, pal, cols, h=16):
    """1x indexed PNG, palette index == grid index (what GB converters want)."""
    rows = (len(grids) + cols - 1) // cols
    im = Image.new("P", (16 * cols, h * rows), 0)
    flat = []
    for c in pal:
        flat += list(c)
    im.putpalette(flat + [0] * (768 - len(flat)))
    for n, g in enumerate(grids):
        ox, oy = (n % cols) * 16, (n // cols) * h
        for y, row in enumerate(g):
            for x, ch in enumerate(row):
                im.putpixel((ox + x, oy + y), 0 if ch == "." else int(ch))
    return im

def preview(items, cols, h=16, scale=4, transparent=True, bg=(232, 224, 208)):
    rows = (len(items) + cols - 1) // cols
    pad = 4
    W = cols * (16 + pad) + pad
    H = rows * (h + pad) + pad
    im = Image.new("RGBA", (W, H), bg + (255,))
    for n, (g, pal) in enumerate(items):
        t = grid_img(g, pal, transparent)
        ox = pad + (n % cols) * (16 + pad)
        oy = pad + (n // cols) * (h + pad)
        im.alpha_composite(t, (ox, oy))
    return im.resize((W * scale, H * scale), Image.NEAREST)


# First six retain the approved still pixels; second poses add calm native motion.
# These are authored source poses, not proof of final biology/motion in a cartridge.
FIRST18_ART=['tortoise','chuckwalla','horned_lizard','sidewinder','red_spotted_toad','kingsnake',
 'fence_lizard','newt','chorus_frog','tiger_salamander','island_night_lizard','alligator_lizard',
 'banded_gecko','desert_iguana','rosy_boa','western_pond_turtle','arboreal_salamander','yellow_legged_frog']

def starter_motion(name,still):
    im=still.copy();d=ImageDraw.Draw(im)
    if name=='tortoise':
        head=still.crop((35,22,46,31));d.rectangle((35,22,45,30),fill=0);im.paste(head,(35,21))
    elif name in ('chuckwalla','horned_lizard'):
        # Quiet eyelid blink; chuckwalla is not drawn puffing defensively.
        d.line([(19,11),(22,11)],fill=1);d.line([(26,11),(29,11)],fill=1)
    elif name=='sidewinder':
        head=still.crop((28,2,43,14));d.rectangle((28,2,42,13),fill=0);im.paste(head,(29,2))
    elif name=='red_spotted_toad':
        d.rectangle((13,15,19,19),fill=2);d.rectangle((31,15,37,19),fill=2)
        d.line([(13,17),(19,17)],fill=1);d.line([(31,17),(37,17)],fill=1)
    else:
        # A brief natural tongue flick keeps the coiled body and feet-free shape.
        d.line([(39,9),(46,10),(47,8)],fill=2);d.line([(45,10),(47,12)],fill=2)
    return im


def far_pose_frames(meta,out):
    """Explicit native32 poses; preserve ALL48 source/frame-zero pixels.

    Current native48 motions survive exact nearest-neighbor conversion. Every
    unsupported future collapse fails production loudly and requires a deliberate
    source-informed far pose, never random marker pixels or fabricated anatomy.
    """
    source=[Image.open(out/f) for f in meta['frames']]
    poses=[im.resize((32,32),Image.Resampling.NEAREST) for im in source]
    recipe='native48pose_resampled_exactly_and_checked'
    changed=sum(a!=b for a,b in zip(poses[0].get_flattened_data(),poses[1].get_flattened_data()))
    if not changed:raise ValueError(f"32px pose collapse for{meta['art_id']}; author a meaningful independent far pose")
    names=[]
    for n,im in enumerate(poses):
        name=f"portrait32_{meta['art_id']}_idle{n}.png";im.save(out/name);names.append(name)
    meta['frames32']=meta['portrait32_frames']=names
    meta['far_animation_authorship']=recipe
    return changed

def emit_full_species_art(pj):
    from pathlib import Path
    import hashlib
    from species_art import emit_species_art
    from species_wave2 import emit_species_wave2
    from species_wave3_reptiles import emit_species_wave3_reptiles
    from species_wave3_salamanders import emit_species_wave3_salamanders
    from species_wave3_frogs import emit_species_wave3_frogs
    root=Path(__file__).resolve().parents[2];out=Path(OUT)
    registry={r['species_id']:r for r in json.loads((root/'data/production_roster.json').read_text())['records']}
    assert set(registry)==set(range(151)), 'Full source-art inventory requires exact151 stable identities'
    result={}
    for sid,name in enumerate(FIRST18_ART[:6]):
        im=Image.open(out/f'portrait_{name}.png');other=starter_motion(name,im);frames=[]
        for f,frame in enumerate([im,other]):
            filename=f'portrait_{name}_idle{f}.png';frame.save(out/filename);frames.append(filename)
        animation=native_canvas(96,48,OBJ[CRITTER_PAL[name]])
        animation.paste(im,(0,0));animation.paste(other,(48,0));filename=f'portrait_{name}_animation.png';animation.save(out/filename)
        colors=OBJ[CRITTER_PAL[name]]
        result[name]={'art_id':name,'species_id':sid,'icon':f'critter_{name}.png','portrait':f'portrait_{name}.png','portrait32':f'portrait32_{name}.png','frames':frames,'animation_sheet':filename,'palette':colors,'palette_rgb555':[rgb555(c) for c in colors],'frame_duration_ticks':36,'behavior_animation':{'tortoise':'head_lift','chuckwalla':'quiet_blink','horned_lizard':'quiet_blink','sidewinder':'quiet_head_sway','red_spotted_toad':'quiet_blink','kingsnake':'natural_tongue_flick'}[name],'review_notes':['First still preserved exactly; second calm native pose authored.','Independent anatomy/native animation and human review remain pending.']}
    firstwave=emit_species_art(out)
    for name,meta in firstwave.items():meta['species_id']=FIRST18_ART.index(name)
    for wave in [firstwave,emit_species_wave2(out),emit_species_wave3_reptiles(out),emit_species_wave3_salamanders(out),emit_species_wave3_frogs(out)]:
        for name,meta in wave.items():
            assert name not in result, 'Duplicate canonical art identity'
            result[name]=meta
    ids=[m['species_id'] for m in result.values()]
    assert len(result)==151 and set(ids)==set(range(151)) and len(ids)==len(set(ids))
    checks=[];portrait_grids={};frame_grids=[]
    for name,meta in sorted(result.items(),key=lambda item:item[1]['species_id']):
        sid=meta['species_id'];record=registry[sid]
        meta.update({'canonical_scientific_name':record['canonical_scientific_name'],'scientific_name_provisional':record['canonical_scientific_name'],'common_name':record['common_name'],'status':'art_only_pending_independent_anatomy_native_and_human_review','taxon_count_approval':False,'allowed_districts_from_roster':[p['region_id'] for p in record['region_permissions']],'dimensions':[48,48],'icon_dimensions':[16,16],'source_entrypoint':'art/src/make_sprites.py'})
        far_changed=far_pose_frames(meta,out)
        colors=[tuple(c) for c in meta['palette']]
        assert len(colors)==4 and len(set(colors))==4 and all(0<=v<=248 and v%8==0 for c in colors for v in c), name+' palette is notfour distinctRGB555colors'
        assert meta['palette_rgb555']==[rgb555(c) for c in colors]
        pj['obj'][name]=[{'rgb':'#%02X%02X%02X'%c,'rgb555':v} for c,v in zip(colors,meta['palette_rgb555'])]
        pj['obj'][name][0]['note']='transparent forOBJ; nativeBG habitat index'
        pj['critter_palette_map'][name]=name
        images=[]
        for filename,size in [(meta['icon'],(16,16)),(meta['portrait'],(48,48)),(meta['portrait32'],(32,32)),(meta['animation_sheet'],(96,48)),*[(f,(48,48)) for f in meta['frames']],*[(f,(32,32)) for f in meta['frames32']]]:
            im=Image.open(out/filename);assert im.mode=='P' and im.size==size and set(im.get_flattened_data())<={0,1,2,3},name+' nativeassetcontract'
            assert im.getpalette()[:12]==[v for c in colors for v in c],name+' nativepaletteorder'
        a=Image.open(out/meta['frames'][0]);b=Image.open(out/meta['frames'][1]);grid=bytes(a.get_flattened_data());assert grid not in portrait_grids, f'Identical nativeportrait grids {name} and {portrait_grids.get(grid)}'
        portrait_grids[grid]=name;changed=sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()));assert changed>0,name+' staticframepair'
        still=Image.open(out/meta['portrait']);assert bytes(still.get_flattened_data())==grid,name+' still/frame0 mismatch'
        unique={tuple(a.crop((x,y,x+8,y+8)).get_flattened_data()) for y in range(0,48,8) for x in range(0,48,8)}
        assert len(unique)<=36 and sum(v!=0 for v in grid)>20
        icon_image=Image.open(out/meta['icon']);assert sum(v!=0 for v in icon_image.get_flattened_data())>5,name+' blankicon'
        checks.append({'species_id':sid,'art_id':name,'canonical_scientific_name':record['canonical_scientific_name'],'unique_tiles_frame0':len(unique),'frame_change_pixels':changed,'far_frame_change_pixels':far_changed,'far_frame_sha256':[hashlib.sha256((out/f).read_bytes()).hexdigest() for f in meta['frames32']],'portrait_sha256':hashlib.sha256((out/meta['portrait']).read_bytes()).hexdigest()})
    (out/'species-art-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    icon_grids={bytes(Image.open(out/m['icon']).get_flattened_data()) for m in result.values()}
    receipt={'species_count':151,'unique_native_icon_patterns':len(icon_grids),'portrait_frames':302,'explicit_far32_frames':302,'all_far32_frame_pairs_distinct':True,'native_indexed_icons':151,'independent_native_portrait_grids':len(portrait_grids),'all_frame_pairs_distinct':True,'palette_contract':'four distinctRGB555 colors;index0habitat/OBJtransparent','scope':'source_art_authored_not_native_or_physical_acceptance','native_observed':False,'human_approved':False,'records':checks}
    (out/'all-species-art-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (root/'output/qa').mkdir(parents=True,exist_ok=True)
    (root/'output/qa/all-species-art-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    # Paginated native-size/2x source review. Background indexzero composited out
    # forhumanpreviewonly; imported PNGs remain truefourcolor indexedassets.
    ordered=sorted(result.values(),key=lambda m:m['species_id'])
    gallery=[]
    for page in range((151+23)//24):
        sheet=Image.new('RGB',(6*110,4*76),(208,200,168));d=ImageDraw.Draw(sheet)
        for n,meta in enumerate(ordered[page*24:page*24+24]):
            x=(n%6)*110;y=(n//6)*76
            for f in range(2):
                im=Image.open(out/meta['frames'][f]);rgba=im.convert('RGBA');mask=Image.new('L',im.size);mask.putdata([255 if v else 0 for v in im.get_flattened_data()]);rgba.putalpha(mask);sheet.paste(rgba,(x+f*50+2,y+2),rgba)
            d.text((x+2,y+51),f"{meta['species_id']+1}: "+meta['common_name'][:13],fill=(32,32,32))
        filename=f'all_species_page_{page+1:02d}_2x.png';sheet.resize((1320,608),Image.Resampling.NEAREST).save(out/filename);gallery.append(filename)
    (out/'all-species-gallery.json').write_text(json.dumps({'pages':gallery,'source_preview_only':True},indent=2)+'\n')
    far_receipt={'species_count':151,'explicit_far32_frames':302,'all_frame_pairs_distinct':True,'far_generation_modifies48_source':False,'far_generation_changes_native48_motion':False,'scope':'explicit_native32_source_not_emulator_observation','native_observed':False,'records':[{'species_id':r['species_id'],'art_id':r['art_id'],'far_frame_change_pixels':r['far_frame_change_pixels'],'far_frame_sha256':r['far_frame_sha256']} for r in checks]}
    (out/'all-species-far-art-validation.json').write_text(json.dumps(far_receipt,indent=2)+'\n')
    (root/'output/qa/all-species-far-art-validation.json').write_text(json.dumps(far_receipt,indent=2)+'\n')
    for page in range((151+23)//24):
        sheet=Image.new('RGB',(6*78,4*62),(208,200,168));d=ImageDraw.Draw(sheet)
        for n,meta in enumerate(ordered[page*24:page*24+24]):
            x=(n%6)*78;y=(n//6)*62
            for f in range(2):
                im=Image.open(out/meta['frames32'][f]);rgba=im.convert('RGBA');mask=Image.new('L',im.size);mask.putdata([255 if v else 0 for v in im.get_flattened_data()]);rgba.putalpha(mask);sheet.paste(rgba,(x+f*35+3,y+2),rgba)
            d.text((x+2,y+39),str(meta['species_id']+1)+': '+meta['common_name'][:8],fill=(32,32,32))
        sheet.resize((936,496),Image.Resampling.NEAREST).save(out/f'all_species_far_page_{page+1:02d}_2x.png')
    return result

def main():
    os.makedirs(OUT, exist_ok=True)
    for k, g in PLAYER.items(): check("player." + k, g, 24)
    for k, g in CRITTERS.items(): check("critter." + k, g)
    for k, g in UI.items(): check("ui." + k, g)
    for k, (_, g) in TILES.items(): check("tile." + k, g)
    for k, (_, g) in TALL.items(): check("tall." + k, g, 32)

    make_font()

    # player
    from explorer_actions import emit_explorer_actions
    emit_explorer_actions(OUT,PLAYER,OBJ["ranger"])
    pnames = list(PLAYER)
    indexed_sheet([PLAYER[k] for k in pnames], OBJ["ranger"], len(pnames), h=24).save(f"{OUT}/player.png")
    preview([(PLAYER[k], OBJ["ranger"]) for k in pnames], len(pnames), h=24).save(f"{OUT}/player_4x.png")

    # critters: one indexed PNG each (each has its own OBJ palette) + combined preview
    for k, g in CRITTERS.items():
        indexed_sheet([g], OBJ[CRITTER_PAL[k]], 1).save(f"{OUT}/critter_{k}.png")
    preview([(g, OBJ[CRITTER_PAL[k]]) for k, g in CRITTERS.items()], 4).save(f"{OUT}/critters_4x.png")

    # ui
    unames = list(UI)
    indexed_sheet([UI[k] for k in unames], OBJ["ui"], 4).save(f"{OUT}/ui.png")
    preview([(UI[k], OBJ["ui"]) for k in unames], 4).save(f"{OUT}/ui_4x.png")

    # bg tiles grouped by palette
    by_pal = {}
    for k, (p, g) in TILES.items():
        by_pal.setdefault(p, []).append((k, g))
    for p, items in by_pal.items():
        indexed_sheet([g for _, g in items], BG[p], len(items)).save(f"{OUT}/tiles_{p}.png")
    for k, (p, g) in TALL.items():
        indexed_sheet([g], BG[p], 1, h=32).save(f"{OUT}/tall_{k}.png")
    prev = preview([(g, BG[p]) for _, (p, g) in TILES.items()], 5, transparent=False)
    prev.save(f"{OUT}/tiles_4x.png")
    preview([(g, BG[p]) for _, (p, g) in TALL.items()], 2, h=32, transparent=False).save(f"{OUT}/tall_4x.png")

    # palettes.json
    pj = {"obj": {}, "bg": {}}
    for k, v in OBJ.items():
        pj["obj"][k] = [{"rgb": "#%02X%02X%02X" % c, "rgb555": rgb555(c)} for c in v]
        pj["obj"][k][0]["note"] = "transparent"
    for k, v in BG.items():
        pj["bg"][k] = [{"rgb": "#%02X%02X%02X" % c, "rgb555": rgb555(c)} for c in v]
    pj["critter_palette_map"] = CRITTER_PAL
    pj["terrain_runtime_order"] = DETAIL_TILE_ORDER
    pj["sheet_order"] = {"player": pnames, "ui": unames,
                         **{f"tiles_{p}": [k for k, _ in items] for p, items in by_pal.items()}}
    with open(f"{OUT}/palettes.json", "w") as f:
        json.dump(pj, f, indent=2)

    export_deluxe()
    emit_full_species_art(pj)
    from ranger_art import emit_ranger_art
    for name,meta in emit_ranger_art(OUT).items():
        pj['obj']['npc_'+name]=[{'rgb':'#%02X%02X%02X'%tuple(c),'rgb555':v} for c,v in zip(meta['palette'],meta['palette_rgb555'])]
    from rock_restore_art import emit_rock_restore_art
    emit_rock_restore_art(OUT,TILES,BG['desert'])
    from marine_art import emit_marine_art
    sea=emit_marine_art(OUT)
    pj['bg']['marine']=[{'rgb':'#%02X%02X%02X'%tuple(c),'rgb555':v} for c,v in zip(sea['palette'],sea['palette_rgb555'])]
    with open(f"{OUT}/palettes.json",'w') as f:json.dump(pj,f,indent=2)
    # Regional layouts are authored game terrain, not fixed showroom collisions.
    from pathlib import Path
    world_path=Path(__file__).resolve().parents[2]/'data/world.json'
    manifest={}
    world_sites=json.loads((world_path.parent/'foundation_encounters.json').read_text())['records']
    for m in json.loads(world_path.read_text())['maps']:
        if m['art_style']=='desert':continue
        region=next(r for r in REGION_ART if r[0]==m['district_id'])
        if m.get('art_variant')=='midmontane_woodland':region=(region[0],region[1],[(168,184,128),(128,152,96),(80,112,64),(32,56,40)],'forest')
        old=REGION_LAYOUTS[region[0]];REGION_LAYOUTS[region[0]]=m['terrain']
        context={**m,'observation_tiles':[(site['game_tile_x'],site['game_tile_y']) for site in world_sites if site['room_id']==m['id']]}
        im,indices,attrs,slots=region_showroom(region,context)
        REGION_LAYOUTS[region[0]]=old
        prefix=f"map_{m['id']:04d}"
        indices.save(f'{OUT}/{prefix}_indices.png');im.save(f'{OUT}/{prefix}.png')
        manifest[str(m['id'])]={'indices':prefix+'_indices.png','attributes':attrs,'palette_slots':slots}
    with open(f'{OUT}/world-art-manifest.json','w') as f:json.dump(manifest,f,indent=2)
    mock_screen()
    from title_scene import emit_title
    emit_title(OUT,FONT)
    print("done ->", os.path.abspath(OUT))

def mock_screen():
    """160x144 mock: desert map, player, flipped rock, chuckwalla, viewfinder."""
    scr = Image.new("RGBA", (160, 144))
    layout = [
        "SSsSTSsSSS",
        "SJSSTSSCSS",
        "SJSSTSsSSS",
        "SSsCTTTTsS",
        "SSSSSSsTSS",
        "SRSSFSSTSR",
        "SSsSSSSTSS",
        "CSSSRSSTSC",
        "SSSSSSsTSS",
    ]
    key = {"S": "sand", "s": "sand_b", "T": "trail", "C": "creosote", "R": "rock",
           "F": "rock_flipped", "J": "sand"}
    for ty, row in enumerate(layout):
        for tx, ch in enumerate(row):
            p, g = TILES[key[ch]]
            scr.alpha_composite(grid_img(g, BG[p], False), (tx * 16, ty * 16))
    jp, jg = TALL["joshua_tree"]
    jt = grid_img(jg, BG[jp], True)
    # treat palette index 0 as transparent for overlay preview only
    px = jt.load()
    for y in range(32):
        for x in range(16):
            if jg[y][x] == "0":
                px[x, y] = (0, 0, 0, 0)
    scr.alpha_composite(jt, (16, 8))
    scr.alpha_composite(grid_img(CRITTERS["chuckwalla"], OBJ["chuckwalla"], True), (64, 80))
    scr.alpha_composite(grid_img(UI["alert"], OBJ["ui"], True), (72, 48))
    scr.alpha_composite(grid_img(PLAYER["right_a"], OBJ["ranger"], True), (44, 76))
    # HUD strip
    hud = Image.new("RGBA", (160, 16), OBJ["ui"][1] + (255,))
    scr.alpha_composite(hud, (0, 128))
    scr.alpha_composite(grid_img(UI["camera"], OBJ["ui"], True), (2, 128))
    scr.resize((640, 576), Image.NEAREST).save(f"{OUT}/mock_screen_4x.png")

    # photo-mode mock: zoomed critter in viewfinder
    ph = Image.new("RGBA", (160, 144), BG["desert"][0] + (255,))
    rp, rg = TILES["rock_flipped"]
    ph.alpha_composite(grid_img(rg, BG[rp], False).resize((64, 64), Image.NEAREST), (48, 40))
    ph.alpha_composite(grid_img(CRITTERS["chuckwalla"], OBJ["chuckwalla"], True).resize((48, 48), Image.NEAREST), (56, 44))
    c = grid_img(UI["vf_corner"], OBJ["ui"], True)
    ph.alpha_composite(c, (16, 16))
    ph.alpha_composite(c.transpose(Image.FLIP_LEFT_RIGHT), (128, 16))
    ph.alpha_composite(c.transpose(Image.FLIP_TOP_BOTTOM), (16, 112))
    ph.alpha_composite(c.transpose(Image.ROTATE_180), (128, 112))
    ph.alpha_composite(grid_img(UI["reticle"], OBJ["ui"], True), (72, 60))
    ph.resize((640, 576), Image.NEAREST).save(f"{OUT}/mock_photo_4x.png")

if __name__ == "__main__":
    main()
