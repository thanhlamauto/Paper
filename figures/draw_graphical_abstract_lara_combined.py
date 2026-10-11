"""Combine Fig. 1's LARA branch and Fig. 3's predictor with training diagrams."""
from pathlib import Path
from xml.sax.saxutils import escape
import base64
from figure_typography import embedded_font_css, font_weight, with_text_shadow

HERE = Path(__file__).resolve().parent
OUT = HERE / 'graphical_abstract_lara_combined.svg'
parts = []
def add(s): parts.append(with_text_shadow(s))
def text(x,y,s,size=34,color='#1a2940',weight=600,anchor='middle'):
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-size="{size}" font-weight="{font_weight(weight)}">{escape(s)}</text>')
def math(x,y,base,sub,size=38,color='#1a2940',hat=False):
    if hat and base == 'A': base = 'Â'
    add(f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" font-size="{size}" font-weight="700"><tspan font-style="italic">{escape(base)}</tspan><tspan baseline-shift="sub" font-size="70%">{escape(sub)}</tspan></text>')
C={
 'neutral':('#eaf0f5','#f9fbfd','#afc1d1','#8da5b9'),
 'source':('#d7ecf2','#f0fbff','#5ba8be','#287e9a'),
 'target':('#fbe0e8','#fff3f6','#db809a','#bd5678'),
 'predict':('#eadcf7','#f9f1ff','#ad84d4','#8455ae'),
 'align':('#ffe9d7','#fff7ed','#e9a666','#c7803a'),
 'embed':('#dff1dd','#f5fcf2','#83bb85','#4e9457')}
def box(x,y,w,h,kind,label='',sub='',size=34,dashed=False):
    f,t,s,e=C[kind];d=14;dash=' stroke-dasharray="12 8"' if dashed else ''
    add(f'<g filter="url(#shadow)"><path d="M{x} {y} l{d} -{d} h{w} l-{d} {d} Z" fill="{t}" stroke="{e}" stroke-width="1.5"/><path d="M{x+w} {y} l{d} -{d} v{h} l-{d} {d} Z" fill="{s}" stroke="{e}" stroke-width="1.5"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{f}" stroke="{e}" stroke-width="2"{dash}/></g>')
    if label:
        text(x+w/2,y+h/2-12 if sub else y+h/2+size/3,label,size)
    if sub: text(x+w/2,y+h/2+35,sub,size-7,'#536782',600)
def line(d,color='#253952',arrow=True,dash=False,width=3.5):
    marker={'#8455ae':'purple','#bd5678':'pink','#8da5b9':'blue','#c7803a':'orange'}.get(color,'dark')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#{marker})"' if arrow else '')+(' stroke-dasharray="9 7"' if dash else '')+'/>')
def panel(x,y,w,h,title,accent='#1c4965',size=42):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="white" stroke="#d8e2eb" stroke-width="2"/><path d="M{x+24} {y} H{x+w-24} Q{x+w} {y} {x+w} {y+24} V{y+92} H{x} V{y+24} Q{x} {y} {x+24} {y} Z" fill="{accent}"/>')
    text(x+w/2,y+63,title,size,'white',800)
def plus(x,y,r=24):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="#253952" stroke-width="3"/>')
    line(f'M{x-r+8} {y} H{x+r-8}',arrow=False);line(f'M{x} {y-r+8} V{y+r-8}',arrow=False)

add('<svg xmlns="http://www.w3.org/2000/svg" width="4920" height="2240" viewBox="0 0 4920 2240" font-family="Nimbus Roman,Times New Roman,Times,serif">')
add(embedded_font_css())
add('<defs>')
for name,color in [('dark','#253952'),('purple','#8455ae'),('pink','#bd5678'),('blue','#8da5b9'),('orange','#c7803a')]:
    add(f'<marker id="{name}" markerWidth="16" markerHeight="16" refX="16" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L16 8 L0 16 Z" fill="{color}"/></marker>')
add('<filter id="shadow" x="-15%" y="-35%" width="140%" height="180%"><feDropShadow dx="4" dy="6" stdDeviation="3" flood-color="#273b56" flood-opacity="0.14"/></filter></defs><rect width="4920" height="2240" fill="#f4f7f9"/>')
panel(40,40,3000,2060,'LARA: overall training architecture','#9a315e',56)
panel(3080,40,1800,2060,'Shared transition predictor Gψ',size=50)

# A single LARA boundary encloses only objectives 02--04.
add('<rect x="750" y="535" width="2250" height="1545" rx="24" fill="#fffafd" stroke="#9a315e" stroke-width="4"/>')
add('<rect x="2420" y="510" width="535" height="64" rx="16" fill="#9a315e"/>')
text(2687,555,'LARA objectives',40,'white',800)

# Four aligned objective lanes: inputs -> transition/comparison -> loss.
text(310,245,'DiT backbone',42,'#536782')
text(1770,245,'Sample layers → predict / compare → loss',42,'#536782')
for y in (1080,1600):
    line(f'M770 {y} H2950','#d8e2eb',False,False,2)
for y in (330,650,970,1290,1610):
    box(120,y,380,110,'neutral')
math(310,403,'v','θ',62)
for lower,upper in ((650,458),(970,778),(1290,1098),(1610,1418)):
    line(f'M310 {lower-32} V{upper}', '#8da5b9',True,True,3.5)
uri='data:image/png;base64,'+base64.b64encode((HERE/'example_dog_noisy_student.png').read_bytes()).decode()
add(f'<rect x="240" y="1880" width="140" height="110" rx="10" fill="white" stroke="#bdccda" stroke-width="2"/><image href="{uri}" x="245" y="1885" width="130" height="100" preserveAspectRatio="xMidYMid slice"/>')
math(425,1950,'x','t',48)
line('M310 1848 V1738',width=4.5)

# Shared hidden-layer bus feeds sampling and the consistency source.
line('M600 705 V1870','#8da5b9',False,True,3.5)
for y in (705,1025,1345,1665):
    line(f'M532 {y} H600','#8da5b9',False,True,3.5)
text(650,625,'Hidden',30,'#63758b')
text(650,667,'layers',30,'#63758b')
for y in (800,1310,1870):
    line(f'M600 {y} H782','#8da5b9',True,True,3.5)

text(800,300,'01  Flow matching',42,'#536782',700,'start')
box(2050,410,350,90,'target');math(2225,472,'u','t',54)
text(1750,472,'Velocity target',35,'#536782')
box(2670,330,270,110,'align');math(2805,403,'L','FM',60)
line('M532 385 H2530 V365 H2652',width=4.5)
line('M2432 455 H2590 V405 H2652',width=4.5)

text(800,590,'02  Prediction',42,'#536782',700,'start')
text(1000,650,'Random pair (a, b)',34,'#536782')
add('<rect x="800" y="670" width="400" height="360" rx="18" fill="#fcfdff" stroke="#8da5b9" stroke-width="2" stroke-dasharray="10 8"/>')
box(850,705,260,100,'source',dashed=True);math(980,772,'A','a',58)
box(850,885,260,100,'target',dashed=True);math(980,952,'A','b',58)
box(1390,705,400,100,'predict','Gψ',size=60)
box(2100,705,310,100,'target');math(2255,772,'A','a→b',52,hat=True)
line('M1142 755 H1372',width=4.5)
line('M1822 755 H2082',width=4.5)
box(1390,890,400,100,'embed')
math(1470,954,'e','t',42);text(1522,952,'+',38)
math(1580,954,'e','a',42);text(1632,952,'+',38)
math(1690,954,'e','b',42)
line('M1590 858 V823','#8455ae',width=4.5)
box(2670,780,270,110,'align');math(2805,853,'L','pred',60)
text(2805,690,'1 random pair',33,'#9a315e',800)
text(2805,735,'per training iteration',28,'#9a315e',700)
line('M2442 755 H2530 V815 H2652',width=4.5)
line('M1142 935 H1270 V1025 H2590 V855 H2652',width=4.5)
text(2225,989,'sg',38,'#96506b')

text(800,1145,'03  Transition consistency · a < b < c',42,'#536782',700,'start')
box(800,1260,350,100,'source')
add('<text x="975" y="1326" text-anchor="middle" fill="#1a2940" font-size="48" font-weight="600">sg(<tspan font-style="italic">A</tspan><tspan baseline-shift="sub" font-size="70%">a</tspan><tspan baseline-shift="baseline">)</tspan></text>')
box(1410,1200,470,100,'predict','Gψ : a → c',size=48)
line('M1182 1310 H1290 V1250 H1392',width=4.5)
box(1410,1420,470,100,'target');math(1645,1487,'A','a→b',52,hat=True)
text(1645,1368,'cached prediction',35,'#63758b')
box(2070,1420,380,100,'predict','EMA : b → c',size=44)
line('M1912 1470 H2052',width=4.5)
text(1982,1434,'sg',38,'#745097')
box(2670,1330,270,110,'align');math(2805,1403,'L','cons',60)
line('M1912 1250 H2530 V1365 H2652',width=4.5)
line('M2482 1470 H2590 V1405 H2652',width=4.5)
text(2536,1434,'sg',38,'#745097')

text(800,1665,'04  Redundancy',42,'#536782',700,'start')
text(1000,1730,'Random pair (i, j)',34,'#536782')
add('<rect x="800" y="1755" width="400" height="290" rx="18" fill="#fcfdff" stroke="#8da5b9" stroke-width="2" stroke-dasharray="10 8"/>')
box(850,1790,260,90,'source',dashed=True);math(980,1853,'A','i',56)
box(850,1920,260,90,'target',dashed=True);math(980,1983,'A','j',56)
text(1690,1730,'Sampled independently of (a, b)',34,'#536782')
line('M1142 1835 H2530 V1875 H2652',width=4.5)
line('M1142 1965 H2590 V1915 H2652',width=4.5)
box(2670,1840,270,110,'align');math(2805,1913,'L','div',60)
text(2805,1750,'1 random pair',33,'#9a315e',800)
text(2805,1795,'per training iteration',28,'#9a315e',700)

# Predictor expands to the right, with a compact embedding legend beside it.
add('<g transform="translate(720 0)">')
text(3695,222,'Embeddings',34,'#536782',700,'start')
for y,sub,meaning in [(290,'t','timestep'),(370,'a','source layer'),(450,'b','target layer')]:
    math(3630,y,'e',sub,42)
    text(3695,y,meaning,32,'#536782',600,'start')

# Predictor detail: short labels and original dimensional path.
for x,k,sub in [(2660,'neutral','t'),(2960,'source','a'),(3260,'target','b')]:
    box(x,230,220,100,k);math(x+110,295,'e',sub,54)
text(2920,295,'+',46);text(3220,295,'+',46)
line('M3070 348 V403',width=4.5)
box(2620,435,900,110,'predict','AdaLN / FiLM',size=48)
text(3070,605,'Condition on timestep + source / target depths',36,'#536782')
line('M2602 490 H2410 V1240 H2462','#8455ae',width=4.5)

# Whole predictor, read from top to bottom.
box(2480,750,340,100,'source');math(2650,817,'A','a',60)
box(2480,950,340,110,'embed','Linear','768 → 384',44)
box(2480,1170,340,140,'predict','Spatial blocks','× 10',40)
box(2480,1440,340,90,'neutral','Layer norm',size=44)
box(2480,1620,340,110,'embed','Linear','384 → 768',44)
box(2480,1840,340,100,'target');math(2650,1907,'A','a→b',54,hat=True)
for a,b in [(868,918),(1078,1138),(1328,1408),(1548,1588),(1748,1808)]:
    line(f'M2650 {a} V{b}',width=4.5)
text(2650,2005,'16 × 16 tokens',36,'#536782')
line('M2852 1240 H3012','#8455ae',False,True,3.5)

# Expand a spatial block beside the path without mixing the training losses here.
add('<rect x="3030" y="690" width="1060" height="1360" rx="18" fill="#faf8fd" stroke="#c9b5df" stroke-width="2" stroke-dasharray="11 8"/>')
text(3560,760,'Conditioned spatial block',44,'#745097')
box(3210,840,610,100,'neutral','Layer norm',size=46)
box(3210,1040,610,100,'predict','Scale + shift',size=46)
box(3210,1240,610,110,'neutral','ConvNeXt',size=48)
plus(3515,1450,34)
box(3210,1570,610,180,'align')
text(3515,1630,'LN · FiLM · MHSA',42)
text(3515,1680,'+ projection + residual',35,'#536782',600)
text(3515,1727,'after blocks 4 and 8',32,'#c7803a')
box(3210,1890,610,100,'neutral','Block output',size=46)
for a,b in [(958,1008),(1158,1208),(1368,1398),(1502,1538),(1768,1858)]:
    line(f'M3515 {a} V{b}',width=4.5)
line('M3192 890 H3090 V1450 H3463','#8da5b9',True,True,3.5)
text(3205,1400,'residual',30,'#63758b')
line('M3552 490 H3990 V1090 H3852','#8455ae',True,True,3.5)
text(3930,1040,'γ, β',36,'#8455ae')
add('</g>')

add('<text x="2460" y="2200" text-anchor="middle" fill="#263951" font-size="50" font-weight="700">L = L<tspan baseline-shift="sub" font-size="70%">FM</tspan><tspan baseline-shift="baseline"> + L</tspan><tspan baseline-shift="sub" font-size="70%">LARA</tspan></text>')
add('</svg>')
OUT.write_text(chr(10).join(parts),encoding='utf-8')
print(OUT)
