# Optical Illusion Pixel Art — 25 Presets (Triangles included)
# ------------------------------------------------------------
# Controls:
#   1–9,0,q,w,e,r,t,y,u,i,o  => select preset (25 total)
#   [ / ]                    => density (fewer/more elements)
#   - / =                    => speed down/up
#   T                        => toggle trails (persistence)
#   F                        => fullscreen
#   H                        => help on/off
#   ESC                      => quit
#
# Notes:
# - "Pixel art" look is achieved via drawing with small rects/dots.
# - Smooth animations use dt-timed sin/cos; most presets are GPU-light.
# - Triangle-focused illusions: 1,2,3,4,5, 10 (at least five).
#
# Install:
#   pip install pygame
# Run:
#   python illusions25.py

import math, random, sys
import pygame
from pygame import gfxdraw

# -------------- Setup -------------- #
W, H = 1200, 800
pygame.init()
flags = pygame.RESIZABLE | pygame.SCALED
screen = pygame.display.set_mode((W, H), flags)
pygame.display.set_caption("Optical Illusion Pixel Art — 25 Presets")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI", 16)
bigfont = pygame.font.SysFont("Segoe UI", 24, bold=True)

# Global knobs (modifiable with keys)
density = 1.0    # 0.4 .. 3.0
speed   = 1.0    # 0.25 .. 3.0
use_trails = True
show_help  = True

# Trail surface for persistence
trail = pygame.Surface((W, H), pygame.SRCALPHA)
trail.fill((0,0,0,0))

def clamp(a, lo, hi): return lo if a<lo else hi if a>hi else a

def polar(cx, cy, ang, rad):
    return cx + math.cos(ang)*rad, cy + math.sin(ang)*rad

def draw_pixel(x, y, c):
    # Tiny pixel/rect (2x2) for crisp "pixel art" feel
    pygame.draw.rect(screen, c, (int(x), int(y), 2, 2))

def draw_line(a, b, c, w=1):
    pygame.draw.line(screen, c, a, b, w)

def draw_poly(pts, c, fill=False, w=1):
    if fill:
        pygame.draw.polygon(screen, c, pts, 0)
    else:
        pygame.draw.polygon(screen, c, pts, w)

def tri(cx, cy, r, rot=0):
    return [polar(cx, cy, rot + i*2*math.pi/3, r) for i in range(3)]

def map_range(v, a, b, c, d):
    if b - a == 0: return c
    t = (v - a) / (b - a)
    return c + (d - c)*t

def grid_iter(cols, rows, pad=0):
    for j in range(rows):
        for i in range(cols):
            yield i, j

# Pseudo-random but stable palette per preset
def color_wheel(t):
    # smooth cycling RGB 0..1
    r = 0.5+0.5*math.sin(t)
    g = 0.5+0.5*math.sin(t+2.094)
    b = 0.5+0.5*math.sin(t+4.188)
    return int(r*255), int(g*255), int(b*255)

def alpha_blit(src, alpha):
    s = src.copy()
    s.set_alpha(alpha)
    screen.blit(s, (0,0))

# -------------- Preset drawers -------------- #
# Each function: draw_X(t, rnd, parms)
# where t is time (seconds), rnd is local Random, parms has density, speed, etc.

def draw_bg_fade():
    # Slight fade for trails
    if use_trails:
        # gentle alpha to let older pixels persist
        fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade.fill((0,0,0,12))
        screen.blit(fade, (0,0))
    else:
        screen.fill((6,8,12))

# --- 1. Triangle Kaleido Orbit (triangle) --- #
def draw_tri_kaleido(t, rnd, p):
    w,h = screen.get_size()
    cx, cy = w/2, h/2
    N = int(60 * p['density'])
    base = min(w,h)/3
    for k in range(N):
        a = t*p['speed']*0.8 + k*0.17
        r = base*(0.25+0.7*math.sin(a*2 + k*0.11)**2)
        rot = a + k*0.2
        pts = tri(cx, cy, r, rot)
        col = color_wheel(a*1.8 + k*0.3)
        draw_poly(pts, col, False, 1)

# --- 2. Kanizsa Tri Implied (triangle) --- #
def draw_kanizsa_triangle(t, rnd, p):
    w,h = screen.get_size()
    cx, cy = w/2, h/2
    r = min(w,h)*0.28
    # background softly pulses
    bgc = int(14+10*math.sin(t*0.8))
    pygame.draw.rect(screen, (bgc,bgc,bgc), (0,0,w,h))
    # three pacman disks to imply a triangle
    for i in range(3):
        ang = t*0.2 + i*2*math.pi/3
        x,y = polar(cx, cy, ang, r)
        rad = r*0.38
        # wedge cut rotates to keep illusion dynamic
        start = ang + math.pi/6 + math.sin(t*0.6+i)*0.5
        end   = start + math.pi*1.65
        col = (235,235,235)
        pygame.draw.circle(screen, col, (int(x),int(y)), int(rad))
        # erase wedge
        pygame.draw.arc(screen, (bgc,bgc,bgc), (x-rad, y-rad, rad*2, rad*2), start, end, int(rad))
    # ghost triangle outline flicker
    alpha = int(40+40*(0.5+0.5*math.sin(t*2)))
    s = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.polygon(s, (255,255,255,alpha), tri(cx,cy,r*0.92), 4)
    screen.blit(s,(0,0))

# --- 3. Triangle Moiré Field (triangle) --- #
def draw_triangle_moire(t, rnd, p):
    w,h = screen.get_size()
    cols = int(28 * p['density'])
    rows = int(cols * h/w)
    cell = w/cols
    phase = t*p['speed']*1.2
    for j in range(rows):
        for i in range(cols):
            x = i*cell + cell/2
            y = j*cell + cell/2
            r = 0.45*cell*(1+0.6*math.sin(phase + (i*0.3) + (j*0.31)))
            rot = phase*0.5 + (i-j)*0.15
            pts = tri(x,y,r,rot)
            c = int(130+120*math.sin(phase + i*0.2 + j*0.19))
            pygame.draw.polygon(screen, (c,c,c), pts, 1)

# --- 4. Penrose-ish Rotate (triangle feel) --- #
def draw_penrose_suggest(t, rnd, p):
    w,h = screen.get_size()
    cx,cy = w/2,h/2
    rings = int(16 * p['density'])
    for r in range(rings):
        rad = map_range(r, 0, rings-1, min(w,h)*0.05, min(w,h)*0.48)
        segs = 3* (4 + (r%3))
        for k in range(segs):
            a = (k/segs)*2*math.pi + t*p['speed']*0.3*(1 if r%2 else -1)
            x1,y1 = polar(cx,cy,a,rad)
            x2,y2 = polar(cx,cy,a+2*math.pi/3, rad)
            # thin triangle wedge
            col = color_wheel(a*2 + r*0.3)
            pygame.draw.line(screen, col, (x1,y1), (x2,y2), 1)

# --- 5. Triangle Spiral Tunnel (triangle) --- #
def draw_tri_spiral_tunnel(t, rnd, p):
    w,h = screen.get_size()
    cx,cy = w/2,h/2
    layers = int(140 * p['density'])
    for i in range(layers):
        s = map_range(i, 0, layers, min(w,h)*0.5, 6)
        rot = t*p['speed']*0.8 + i*0.21
        pts = tri(cx,cy,s,rot)
        col = (int(160+95*math.sin(i*0.1 + t)),)*3
        pygame.draw.polygon(screen, col, pts, 1)

# --- 6. Café Wall Warp --- #
def draw_cafe_wall(t, rnd, p):
    w,h = screen.get_size()
    rows = int(18 * p['density'])
    cols = rows*2
    cell = h/rows
    phase = t*p['speed']*0.8
    for j in range(rows):
        off = (j%2)* (cell*0.4*math.sin(phase+j*0.2))
        for i in range(cols):
            x = i*cell + off
            y = j*cell
            c = 255 if (i+j)%2==0 else 20
            pygame.draw.rect(screen, (c,c,c), (x,y,cell,cell))
    # horizontal mortar lines
    for j in range(rows+1):
        y = j*cell
        pygame.draw.line(screen, (80,80,80), (0,y), (w,y), 2)

# --- 7. Bulge Grid (Hermann-like) --- #
def draw_bulge_grid(t, rnd, p):
    w,h = screen.get_size()
    cols = int(36 * p['density'])
    rows = int(cols*h/w)
    cellx = w/cols
    celly = h/rows
    for j in range(rows+1):
        vag = math.sin(t*p['speed']*0.6 + j*0.3)*10
        pygame.draw.line(screen, (200,200,200), (0, j*celly+vag), (w, j*celly-vag), 1)
    for i in range(cols+1):
        vag = math.sin(t*p['speed']*0.7 + i*0.3)*10
        pygame.draw.line(screen, (200,200,200), (i*cellx+vag, 0), (i*cellx-vag, h), 1)

# --- 8. Radiant Lines (Hering) --- #
def draw_radiant(t, rnd, p):
    w,h = screen.get_size()
    cx,cy = w/2,h/2
    rays = int(220 * p['density'])
    for k in range(rays):
        a = k/rays*2*math.pi
        x,y = polar(cx,cy,a, min(w,h)*0.6)
        c = (120+int(120*math.sin(t+p['speed']*k*0.02)),)*3
        draw_line((cx,cy),(x,y),c,1)
    # central circles that appear warped
    for r in range(12):
        rad = 14 + r*14 + 6*math.sin(t*0.8+r*0.3)
        pygame.draw.circle(screen, (240,240,240), (int(cx),int(cy)), int(rad), 2)

# --- 9. Spiral vs Circles (Fraser-ish) --- #
def draw_fraser(t, rnd, p):
    w,h = screen.get_size()
    cx,cy = w/2,h/2
    rounds = int(56 * p['density'])
    for r in range(rounds):
        rad = 12 + r*10
        twist = 0.5*math.sin(t*0.9 + r*0.25)
        for k in range(36):
            a = k/36*2*math.pi + twist
            x,y = polar(cx,cy,a,rad)
            draw_pixel(x,y,(240,240,240))
        # dashes to confuse orientation
        for k in range(12):
            a = k/12*2*math.pi - twist*1.6
            x1,y1 = polar(cx,cy,a,rad-6)
            x2,y2 = polar(cx,cy,a+0.08,rad+6)
            pygame.draw.line(screen, (80,80,80), (x1,y1),(x2,y2),1)

# --- 10. Tri Chroma Drift (triangle) --- #
def draw_tri_chroma_drift(t, rnd, p):
    w,h = screen.get_size()
    cx,cy=w/2,h/2
    N=int(120*p['density'])
    base=min(w,h)*0.48
    for i in range(N):
        s=base*(i/N)
        rot=t*p['speed']*0.6 + i*0.07
        pts=tri(cx,cy,s,rot)
        rr,gg,bb=color_wheel(i*0.1 + t*1.2)
        # RGB slight offsets to induce motion illusion
        off=1.5+0.8*math.sin(t+i*0.2)
        draw_poly([(x+off,y) for (x,y) in pts], (rr,0,0), False,1)
        draw_poly([(x,y+off) for (x,y) in pts], (0,gg,0), False,1)
        draw_poly([(x-off,y-off) for (x,y) in pts], (0,0,bb), False,1)

# --- 11. Rotating Snakes-ish --- #
def draw_rot_snakes(t, rnd, p):
    w,h = screen.get_size()
    cx,cy=w/2,h/2
    rings = int(10*p['density'])+6
    seg = 36
    for r in range(1,rings+1):
        R = r*min(w,h)*0.045 + 40
        for k in range(seg):
            a = (k/seg)*2*math.pi
            # 8-color loop for drift
            idx = (k + r*2) % 8
            c = [ (235,64,64), (255,200,0), (240,240,240), (40,40,40),
                  (64,64,235), (0,180,255), (240,240,240), (40,40,40) ][idx]
            # arc rotates subtly
            rot = t*p['speed']*0.3*(1 if r%2 else -1)
            x1,y1=polar(cx,cy,a+rot,R-14)
            x2,y2=polar(cx,cy,a+rot+2*math.pi/seg,R+14)
            pygame.draw.arc(screen, c, (cx-R,cy-R,R*2,R*2), a+rot, a+rot+2*math.pi/seg, 10)

# --- 12. Offset Checkerboard (breathing) --- #
def draw_checker_breathe(t, rnd, p):
    w,h=screen.get_size()
    cols=int(22*p['density'])
    rows=int(cols*h/w)
    cw=w/cols; ch=h/rows
    off = 0.5*math.sin(t*p['speed']*2)
    for j in range(rows):
        for i in range(cols):
            x=i*cw + (ch*0.4 if j%2 else -ch*0.4)*off
            y=j*ch
            c=255 if (i+j)%2==0 else 10
            pygame.draw.rect(screen,(c,c,c),(x,y,cw,ch))

# --- 13. Radial Tunnel (pixel) --- #
def draw_radial_tunnel(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    rings=int(320*p['density'])
    for i in range(rings):
        a=t*p['speed']*0.6 + i*0.08
        r=2+i*2
        x,y=polar(cx,cy,a,r)
        col=(int(140+115*math.sin(i*0.1+t)),)*3
        draw_pixel(x,y,col)

# --- 14. Hex Moiré Drift --- #
def draw_hex_moire(t, rnd, p):
    w,h=screen.get_size()
    size=16/max(0.5,p['density']*0.8)
    dx=size*math.sqrt(3); dy=size*1.5
    cols=int(w/dx)+2; rows=int(h/dy)+2
    ph=t*p['speed']*0.5
    for j in range(rows):
        for i in range(cols):
            x=i*dx + (j%2)*dx/2 + math.sin(ph+i*0.3+j*0.2)*6
            y=j*dy + math.cos(ph+i*0.2+j*0.3)*3
            c=(200,200,200) if (i+j)%2==0 else (50,50,50)
            pygame.draw.circle(screen,c,(int(x),int(y)),int(size),1)

# --- 15. Wave Interference (two fields) --- #
def draw_wave_interf(t, rnd, p):
    w,h=screen.get_size()
    cols=int(110*p['density'])
    rows=int(cols*h/w)
    cw=w/cols; ch=h/rows
    s1= (math.sin(t*p['speed']*0.8)+1.2)
    s2= (math.cos(t*p['speed']*0.7)+1.2)
    for j in range(rows):
        for i in range(cols):
            val = math.sin(i*0.18*s1 + t*0.9) + math.cos(j*0.15*s2 + t*1.1)
            c = int(map_range(val, -2, 2, 20, 235))
            pygame.draw.rect(screen,(c,c,c),(i*cw,j*ch,cw,ch))

# --- 16. Lissajous Dot Field --- #
def draw_lissajous_field(t, rnd, p):
    w,h=screen.get_size()
    n=int(420*p['density'])
    for i in range(n):
        a=i*0.07
        x = w/2 + math.sin(t*p['speed']*1.1 + a*3)*w*0.38*math.sin(a*0.3)
        y = h/2 + math.cos(t*p['speed']*1.3 + a*4)*h*0.28*math.cos(a*0.2)
        col=color_wheel(a*0.7+t*1.2)
        draw_pixel(x,y,col)

# --- 17. Vortex Spiral Dashes --- #
def draw_vortex_dashes(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    arms=int(16*p['density'])+12
    segs=140
    for aidx in range(arms):
        base=aidx/arms*2*math.pi + t*p['speed']*0.2
        for k in range(segs):
            r=6+k*3
            a=base + k*0.06
            x,y=polar(cx,cy,a,r)
            if k%2==0:
                draw_pixel(x,y,(240,240,240))
            else:
                draw_pixel(x,y,(40,40,40))

# --- 18. Concentric Zig Rings --- #
def draw_zig_rings(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    rings=int(42*p['density'])
    for r in range(1,rings+1):
        R=r*10
        pts=[]
        zig= int(10 + 10*math.sin(t*0.7 + r))
        for k in range(zig):
            a=k/zig*2*math.pi + r*0.11 + t*p['speed']*0.3
            jitter = 4*math.sin(k*0.7 + r*0.3 + t)
            x,y=polar(cx,cy,a,R+jitter)
            pts.append((x,y))
        pygame.draw.polygon(screen,(220,220,220),pts,1)

# --- 19. Chromatic Grid Drift --- #
def draw_chroma_grid(t, rnd, p):
    w,h=screen.get_size()
    cols=int(36*p['density'])
    rows=int(cols*h/w)
    cw=w/cols; ch=h/rows
    for j in range(rows):
        for i in range(cols):
            a=t*p['speed'] + i*0.2 + j*0.21
            x=i*cw; y=j*ch
            rr=int(120+120*math.sin(a))
            gg=int(120+120*math.sin(a+2))
            bb=int(120+120*math.sin(a+4))
            pygame.draw.rect(screen,(rr,gg,bb),(x,y,cw-1,ch-1))

# --- 20. Pixel Tunnel Zoom --- #
def draw_pixel_tunnel(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    n=int(1600*p['density'])
    for i in range(n):
        a=rnd.random()*2*math.pi
        r=(i/n)**0.6 * (min(w,h)*0.5)
        x,y=polar(cx,cy,a + t*p['speed']*0.15, r)
        col=(int(100+155*(i/n)),)*3
        draw_pixel(x,y,col)

# --- 21. Illusory Tilted Lines (Zöllner-ish) --- #
def draw_zollner(t, rnd, p):
    w,h=screen.get_size()
    main_gap=int(48/p['density'])+6
    # main parallel lines
    for y in range(0,h,main_gap):
        pygame.draw.line(screen,(230,230,230),(0,y),(w,y),1)
    # short skewers
    seg=int(24*p['density'])+12
    for k in range(seg):
        x=int(k*w/seg)
        ang = 0.8*math.sin(t*p['speed']*0.7 + k*0.6)
        for y in range(0,h,main_gap*2):
            x1,y1 = x-18,y-10
            x2,y2 = x+18,y+10
            cs=math.cos(ang); sn=math.sin(ang)
            cx,cy=x,(y+main_gap)
            ax = cx + (x1-x)*cs - (y1-cy)*sn
            ay = cy + (x1-x)*sn + (y1-cy)*cs
            bx = cx + (x2-x)*cs - (y2-cy)*sn
            by = cy + (x2-x)*sn + (y2-cy)*cs
            pygame.draw.line(screen,(120,120,120),(ax,ay),(bx,by),1)

# --- 22. Spiral Checker Twist --- #
def draw_spiral_checker(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    for r in range(8, int(min(w,h)*0.6), 10):
        tiles=int(max(8, r/10))
        for k in range(tiles):
            a=k/tiles*2*math.pi + t*p['speed']*0.4
            x1,y1=polar(cx,cy,a,r)
            x2,y2=polar(cx,cy,a+2*math.pi/tiles,r+10)
            c=(255,255,255) if (k+(r//10))%2==0 else (15,15,15)
            pygame.draw.polygon(screen,c,[(x1,y1),(x2,y2),
                                          polar(cx,cy,a+2*math.pi/tiles,r),
                                          polar(cx,cy,a,r+10)],0)

# --- 23. Impossible Steps (Escher-ish) --- #
def draw_impossible_steps(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    # a rotating 4-segment "stair" ring
    R=min(w,h)*0.28
    segs=36
    rot=t*p['speed']*0.4
    for s in range(segs):
        a0= (s/segs)*2*math.pi + rot
        a1= ((s+1)/segs)*2*math.pi + rot
        x0,y0=polar(cx,cy,a0,R)
        x1,y1=polar(cx,cy,a1,R)
        x2,y2=polar(cx,cy,a1,R+26)
        x3,y3=polar(cx,cy,a0,R+26)
        c=(220,220,220) if s%2==0 else (40,40,40)
        pygame.draw.polygon(screen,c,[(x0,y0),(x1,y1),(x2,y2),(x3,y3)],0)
    # inner square misalignment to trick depth
    s=R*0.9
    theta=t*p['speed']*0.6
    pts=[(cx+s*math.cos(theta+i*math.pi/2), cy+s*math.sin(theta+i*math.pi/2)) for i in range(4)]
    pygame.draw.polygon(screen,(250,250,250),pts,3)

# --- 24. Parallax Starfield Circle Illusion --- #
def draw_parallax_stars(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    n=int(900*p['density'])
    for i in range(n):
        ang = rnd.random()*2*math.pi
        r = (rnd.random()**0.6)*min(w,h)*0.45
        x,y=polar(cx,cy, ang + 0.1*math.sin(t*p['speed']*0.6 + r*0.01), r)
        draw_pixel(x,y,(230,230,230))
    # faint circles that seem to wobble
    for R in range(60, int(min(w,h)*0.5), 60):
        pygame.draw.circle(screen,(100,100,100),(int(cx),int(cy)),R,1)

# --- 25. Kaleido Rings (finale) --- #
def draw_kaleido_rings(t, rnd, p):
    w,h=screen.get_size()
    cx,cy=w/2,h/2
    rings=int(60*p['density'])
    for r in range(1,rings+1):
        R = r*min(w,h)*0.007 + 10
        seg = 12 + (r%6)*2
        for k in range(seg):
            a = k/seg*2*math.pi + t*p['speed']*0.3*(1 if r%2 else -1)
            x,y=polar(cx,cy,a,R)
            col=color_wheel(a*3 + r*0.2)
            gfxdraw.pixel(screen, int(x), int(y), col)

# -------------- Registry -------------- #
PRESETS = [
    ("Triangle Kaleido Orbit",     draw_tri_kaleido),
    ("Kanizsa Implied Triangle",   draw_kanizsa_triangle),
    ("Triangle Moiré Field",       draw_triangle_moire),
    ("Penrose-ish Rotate",         draw_penrose_suggest),
    ("Triangle Spiral Tunnel",     draw_tri_spiral_tunnel),
    ("Café Wall Warp",             draw_cafe_wall),
    ("Bulge Grid",                 draw_bulge_grid),
    ("Radiant Lines (Hering)",     draw_radiant),
    ("Fraser Spiral-ish",          draw_fraser),
    ("Tri Chroma Drift",           draw_tri_chroma_drift),
    ("Rotating Snakes-ish",        draw_rot_snakes),
    ("Breathing Checkerboard",     draw_checker_breathe),
    ("Radial Pixel Tunnel",        draw_radial_tunnel),
    ("Hex Moiré Drift",            draw_hex_moire),
    ("Wave Interference",          draw_wave_interf),
    ("Lissajous Dot Field",        draw_lissajous_field),
    ("Vortex Spiral Dashes",       draw_vortex_dashes),
    ("Concentric Zig Rings",       draw_zig_rings),
    ("Chromatic Grid Drift",       draw_chroma_grid),
    ("Pixel Tunnel Zoom",          draw_pixel_tunnel),
    ("Zöllner Tilt Illusion",      draw_zollner),
    ("Spiral Checker Twist",       draw_spiral_checker),
    ("Impossible Steps",           draw_impossible_steps),
    ("Parallax Starfield",         draw_parallax_stars),
    ("Kaleido Rings",              draw_kaleido_rings),
]
assert len(PRESETS) == 25

# Map keys to index: 1..9,0,q..o
KEY_ORDER = [
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
    pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t,
    pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p,
    pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_g,
]
assert len(KEY_ORDER) == len(PRESETS)

# -------------- Main Loop -------------- #
preset_idx = 0
seed_base = 1337
running = True
time_start = pygame.time.get_ticks()

def draw_help_overlay():
    w,h=screen.get_size()
    pad=10
    s=pygame.Surface((w,0), pygame.SRCALPHA)
    lines = [
        f"Preset {preset_idx+1}/25 — {PRESETS[preset_idx][0]}",
        "Controls: 1–9,0,q–o switch | [ / ] density | - / = speed | T trails | F fullscreen | H help | ESC quit",
        f"Density: {density:.2f}   Speed: {speed:.2f}   Trails: {'ON' if use_trails else 'OFF'}"
    ]
    y=10
    for i,ln in enumerate(lines):
        txt = bigfont.render(ln if i==0 else "", True, (0,0,0))
        if i==0:
            # Title badge
            label = bigfont.render(lines[0], True, (255,255,255))
            bg = pygame.Surface((label.get_width()+20, label.get_height()+10), pygame.SRCALPHA)
            bg.fill((0,0,0,120))
            screen.blit(bg,(pad,y))
            screen.blit(label,(pad+10,y+5))
            y += label.get_height()+16
        else:
            small = font.render(lines[i], True, (235,235,235))
            screen.blit(small,(pad,y))
            y += small.get_height()+6

while running:
    dt = clock.tick(60)/1000.0
    # event
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running=False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running=False
            elif e.key in KEY_ORDER:
                preset_idx = KEY_ORDER.index(e.key)
                # reset trail
                trail = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                trail.fill((0,0,0,0))
            elif e.key == pygame.K_LEFTBRACKET:
                density = clamp(density-0.1, 0.4, 3.0)
            elif e.key == pygame.K_RIGHTBRACKET:
                density = clamp(density+0.1, 0.4, 3.0)
            elif e.key == pygame.K_MINUS:
                speed = clamp(speed-0.1, 0.25, 3.0)
            elif e.key == pygame.K_EQUALS:
                speed = clamp(speed+0.1, 0.25, 3.0)
            elif e.key == pygame.K_t:
                use_trails = not use_trails
            elif e.key == pygame.K_h:
                show_help = not show_help
            elif e.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
        elif e.type == pygame.VIDEORESIZE:
            W,H = e.w, e.h
            screen = pygame.display.set_mode((W,H), flags)
            # rebuild trail surface to new size
            trail = pygame.Surface((W,H), pygame.SRCALPHA)
            trail.fill((0,0,0,0))

    t = (pygame.time.get_ticks() - time_start)/1000.0
    params = {'density': density, 'speed': speed}

    if not use_trails:
        screen.fill((6,8,12))
    else:
        # composite trail then dim slightly
        screen.blit(trail,(0,0))
        fader = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fader.fill((0,0,0,24))
        screen.blit(fader,(0,0))

    # Each draw should build upon current screen; also update trail if enabled
    local_random = random.Random(seed_base + preset_idx*999)
    name, drawer = PRESETS[preset_idx]
    drawer(t, local_random, params)

    if use_trails:
        # copy current frame into trail buffer for persistence
        trail.blit(screen,(0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

    if show_help:
        draw_help_overlay()

    pygame.display.flip()

pygame.quit()
