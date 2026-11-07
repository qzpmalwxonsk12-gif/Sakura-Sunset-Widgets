"""Original daytime plate, reference-derived Go position and deterministic petal loop.

Explicitly requested Pillow compositing keeps every stone reproducible. No rendering on device.
"""
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from PIL import Image, ImageDraw
from generate_assets import bitmap_xml

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'app/src/main/res'
W, H, N = 480, 270, 96
COLORS = ['#ffdfeb', '#ffbed4', '#e98db5', '#c76b98']


def board_position():
    reference = Image.open(ROOT/'art/source/go-position-reference.png').convert('RGB')
    rows, samples = [], []
    for row in range(19):
        line = ''
        for col in range(19):
            x, y = round(147+col*36.3), round(115+row*36.4)
            # Off-grid samples distinguish dark stones from the thin black grid.
            values = [sum(reference.getpixel((x+dx,y+dy)))/3
                      for dx,dy in [(-7,-7),(7,-7),(-7,7),(7,7)]]
            shade = statistics.median(values)
            stone = 'B' if shade < 85 else 'W' if shade > 180 else '.'
            line += stone
            samples.append(dict(row=row, col=col, x=x, y=y, shade=round(shade,2), stone=stone))
        rows.append(line)
    return rows, samples


def project(u, v):
    # Four corners INSIDE the smoothed surface of the revised 1672x941 source.
    # Top-left of source board maps to back corner; row order is preserved.
    a,b,c,d = (857,487),(1148,549),(927,624),(635,548)
    return ((a[0]*(1-u)*(1-v)+b[0]*u*(1-v)+c[0]*u*v+d[0]*(1-u)*v)*W/1672,
            (a[1]*(1-u)*(1-v)+b[1]*u*(1-v)+c[1]*u*v+d[1]*(1-u)*v)*H/941)


def draw_board(base, rows):
    draw = ImageDraw.Draw(base)
    for i in range(19):
        for start,end in [(project(i/18,0),project(i/18,1)),(project(0,i/18),project(1,i/18))]:
            # Quiet hairline cuts: the stones, rather than the grid, carry the contrast.
            draw.line([(round(x),round(y)) for x,y in [start,end]], fill='#948879')
    for row,line in enumerate(rows):
        for col,stone in enumerate(line):
            if stone == '.': continue
            x,y = map(round,project(col/18,row/18))
            color = '#101320' if stone == 'B' else '#fffaf0'
            draw.line((x-1,y+1,x+1,y+1),fill='#292332' if stone == 'B' else '#776a71')
            draw.line((x-1,y,x+1,y),fill=color)
            draw.point((x,y-1),fill='#242937' if stone=='B' else '#ffffff')
    return base


def petal_specs():
    rng=random.Random(261026)
    sites=[(116,17),(171,30),(207,51),(240,69),(282,55),(321,76),(355,86),(380,69)]
    return [dict(x=sites[i%8][0]+rng.uniform(-8,8),y=sites[i%8][1]+rng.uniform(-5,5),
                 phase=i*N/22, land_x=345+rng.uniform(-55,60),land_y=225+rng.uniform(-15,28),
                 swirl=rng.random()*math.tau,size=1+(i%6==0),color=i%4) for i in range(22)]


def position(p, frame):
    t=((frame+p['phase'])%N)/N
    # First 72%: drift from canopy to ground. Then accelerate gently along ground.
    if t < .72:
        q=t/.72
        x=p['x']+(p['land_x']-p['x'])*q+4*math.sin(math.tau*q)*math.sin(math.pi*q)
        y=p['y']+(p['land_y']-p['y'])*q+3*math.sin(math.tau*q+p['swirl'])*math.sin(math.pi*q)
    else:
        q=(t-.72)/.28
        x=p['land_x']+(W+12-p['land_x'])*q*q
        y=p['land_y']+8*q+math.sin(q*math.tau)*1.5
    return x,y,t


def render(base, frame):
    im=base.convert('RGBA'); draw=ImageDraw.Draw(im)
    for p in petal_specs():
        fx,fy,t=position(p,frame); x,y=round(fx),round(fy)
        if t < .012: continue
        color=COLORS[p['color']]
        draw.point((x,y), fill=color)
        if t > .025 and int(t*15+p['swirl'])%3:
            draw.point((x+1,y),fill=color)
        if p['size']==2 and t>.025: draw.point((x,y+1),fill=COLORS[0])
    mask=Image.new('L',(W,H)); ImageDraw.Draw(mask).rounded_rectangle((0,0,W-1,H-1),radius=7,fill=255)
    im.putalpha(mask)
    return im


def main():
    rows,samples=board_position()
    data=dict(size=19,orientation='Rows top to bottom and columns left to right in supplied overhead reference',
              rows=rows,black=sum(r.count('B') for r in rows),white=sum(r.count('W') for r in rows),samples=samples)
    (ROOT/'art/go-position.json').write_text(json.dumps(data,indent=2)+'\n')
    setup=[]
    for stone,property_name in [('B','AB'),('W','AW')]:
        points=''.join(f'[{chr(97+col)}{chr(97+row)}]' for row,line in enumerate(rows)
                       for col,s in enumerate(line) if s==stone)
        setup.append(property_name+points)
    (ROOT/'art/immortals-position.sgf').write_text(
        '(;GM[1]FF[4]CA[UTF-8]SZ[19]GN[The Immortals Chess Game]'+''.join(setup)+')\n')
    # Large legible orthographic verification preview, not the widget's game camera.
    board=Image.new('RGB',(760,760),'#aaa69e'); d=ImageDraw.Draw(board)
    for i in range(19):
        n=20+i*40; d.line((20,n,740,n), fill='#58535b'); d.line((n,20,n,740),fill='#58535b')
    for row,line in enumerate(rows):
        for col,s in enumerate(line):
            if s!='.':
                x,y=20+col*40,20+row*40
                d.ellipse((x-14,y-14,x+14,y+14), fill='#252630' if s=='B' else '#f6f1e6')
    board.save(ROOT/'art/previews/immortals-board-position.png')
    annotated=Image.open(ROOT/'art/source/go-position-reference.png').convert('RGB'); d=ImageDraw.Draw(annotated)
    for s in samples:
        d.text((s['x']-3,s['y']-5),s['stone'], fill='#ff5050')
    annotated.save(ROOT/'art/previews/board-extraction-check.png')
    source=Image.open(ROOT/'art/source/immortals-stone-day.png').convert('RGB')
    base=source.resize((W,H),Image.Resampling.NEAREST).quantize(colors=96,dither=Image.Dither.NONE).convert('RGB')
    base=draw_board(base,rows); base.save(ROOT/'art/immortals-base.png')
    colors=sorted(set(base.get_flattened_data())|{tuple(bytes.fromhex(c[1:])) for c in COLORS})
    assert len(colors)<255
    lookup={c:i for i,c in enumerate(colors)}
    frames=[]; hashes=[]
    for i in range(N):
        im=render(base,i); frames.append(im)
        indexed=Image.frombytes('P',im.size,bytes(lookup[(r,g,b)] if a else 255 for r,g,b,a in im.get_flattened_data()))
        indexed.putpalette([v for c in colors for v in c]+[0]*(768-len(colors)*3)); indexed.info['transparency']=255
        name=f'immortals_frame_{i:03d}'
        path=RES/f'drawable-nodpi/{name}_pixels.png'; indexed.save(path,optimize=True)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        (RES/f'drawable/{name}.xml').write_text(bitmap_xml(name+'_pixels'))
    (RES/'drawable/immortals_preview.xml').write_text(bitmap_xml('immortals_frame_000_pixels'))
    (ROOT/'app/src/main/java/com/sakurasunset/widget/ImmortalsFrames.kt').write_text(
        'package com.sakurasunset.widget\n\n// Generated by tools/generate_immortals.py\nobject ImmortalsFrames {\n    val resources = intArrayOf(\n'+
        ''.join(f'        R.drawable.immortals_frame_{i:03d},\n' for i in range(N))+'    )\n}\n')
    frames[0].resize((960,540),Image.Resampling.NEAREST).save(ROOT/'art/previews/immortals-painting.png')
    frames[0].save(ROOT/'art/previews/immortals-loop.gif',save_all=True,append_images=frames[1:],duration=[120,130]*48,loop=0,disposal=2,optimize=True)
    metrics=dict(canvas=[W,H],frames=N,fps=8,loop_ms=12000,black=data['black'],white=data['white'],
                 png_bytes=sum(p.stat().st_size for p in (RES/'drawable-nodpi').glob('immortals_frame*png')),
                 all_frames_decoded_upper_bound_bytes=W*H*4*N,frame_sha256=hashes)
    (ROOT/'art/immortals-manifest.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metrics.items() if k!='frame_sha256'},indent=2))


if __name__=='__main__': main()
