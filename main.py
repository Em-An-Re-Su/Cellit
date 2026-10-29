# -*- coding: utf-8 -*-
"""Bio3D - 3D 인체 탐험: 피부(메스) → 장기 → 조직(세포) → 세포소기관 → 핵(DNA) → 형질 → 약물/시야(POV)
실행: pip install -r requirements.txt && python main.py
조작: 드래그=회전 / 휠=확대 / V=시야(POV) / Backspace=뒤로 / 메스 버튼 후 몸통을 드래그해 절개"""
import math, os, random
from ursina import *
from ursina.shaders import basic_lighting_shader as LIT

for f in ('C:/Windows/Fonts/malgun.ttf', '/System/Library/Fonts/AppleSDGothicNeo.ttc',
          '/usr/share/fonts/truetype/nanum/NanumGothic.ttf', '/Library/Fonts/NanumGothic.ttf'):
    if os.path.exists(f):
        Text.default_font = f; break
app = Ursina(title='Bio3D 생명과학 3D 인체 탐험', borderless=False)
window.color = Color(.04, .05, .09, 1)
def C(r, g, b, a=1): return Color(r/255, g/255, b/255, a)

# ───────── 메시 생성 도구 ─────────
def mk(v, t):
    m = Mesh(vertices=v, triangles=t, mode='triangle')
    try: m.generate_normals()
    except Exception: pass
    return m

def path(keys, n):
    P, R = [], []
    for k in range(n):
        s = k/(n-1)*(len(keys)-1); i = int(min(s, len(keys)-2)); f = s-i; f = f*f*(3-2*f)
        a, b = keys[i], keys[i+1]
        P.append(tuple(a[0][j]+(b[0][j]-a[0][j])*f for j in range(3)))
        R.append((a[1][0]+(b[1][0]-a[1][0])*f, a[1][1]+(b[1][1]-a[1][1])*f))
    return P, R

def tube(pts, rad, seg=14):
    P = [Vec3(*p) for p in pts]; n = len(P); V = []; T = []
    for i in range(n):
        t = (P[min(i+1, n-1)]-P[max(i-1, 0)]).normalized()
        ref = Vec3(0, 0, 1) if abs(t.z) < .9 else Vec3(1, 0, 0)
        u = t.cross(ref).normalized(); v = t.cross(u); ru, rv = rad[i]
        for j in range(seg+1):
            a = 2*math.pi*j/seg; q = P[i]+u*(math.cos(a)*ru)+v*(math.sin(a)*rv)
            V.append((q.x, q.y, q.z))
    for i in range(n-1):
        for j in range(seg):
            a = i*(seg+1)+j; b = a+seg+1; T += [(a, a+1, b), (a+1, b+1, b)]
    for i, end in ((0, 0), (n-1, 1)):
        c = len(V); V.append((P[i].x, P[i].y, P[i].z)); base = i*(seg+1)
        for j in range(seg): T.append((c, base+j, base+j+1) if end == 0 else (c, base+j+1, base+j))
    return mk(V, T)

def blob(rx, ry, rz, fn=None, res=22):
    V = []; T = []
    for i in range(res+1):
        th = math.pi*i/res
        for j in range(res+1):
            ph = 2*math.pi*j/res
            x, y, z = math.sin(th)*math.cos(ph), math.cos(th), math.sin(th)*math.sin(ph)
            if fn: x, y, z = fn(x, y, z)
            V.append((x*rx, y*ry, z*rz))
    for i in range(res):
        for j in range(res):
            a = i*(res+1)+j; b = a+res+1; T += [(a, b, a+1), (a+1, b, b+1)]
    return mk(V, T)

def ball(parent, kind, mesh, pos, col, scale=1, collide=True):
    e = Entity(parent=parent, model=mesh, position=pos, color=col, scale=scale, shader=LIT, double_sided=True)
    e.kind = kind
    if collide: e.collider = 'box'
    return e

# ───────── 데이터 ─────────
# key: 이름, 색, 역할, 제거 결과, (심박,수축기혈압,SpO2,의식 변화, 치명여부), 세포[(이름,설명,미토콘드리아수)]
ORG = {
 'brain': ('뇌', C(230, 160, 170), '사고·기억·감각·운동을 통제하고 호흡·심박을 조절하는 중추.',
           '의식 소실, 호흡·심박 조절 중단 → 즉시 사망.', (-72, -120, -60, -100, True),
           [('뉴런(신경세포)', '가지돌기로 신호를 받고 축삭으로 활동전위를 전달', 8), ('별아교세포', '신경 영양 공급·혈액뇌장벽 유지', 5), ('희소돌기아교세포', '축삭을 말이집으로 감싸 신호 속도 향상', 4)]),
 'heart': ('심장', C(190, 40, 55), '혈액을 전신으로 펌프질하는 근육 기관(1일 약 10만 회 박동).',
           '순환 정지 → 뇌·장기에 산소 공급 중단, 수 분 내 사망.', (-72, -120, -60, -100, True),
           [('심근세포', '미토콘드리아가 매우 많아 쉬지 않고 수축', 14), ('동방결절 조율세포', '스스로 전기 신호를 만들어 박동 속도 결정', 6), ('혈관내피세포', '혈관 안쪽을 덮고 혈류·혈압 조절', 4)]),
 'lung': ('폐', C(225, 140, 150), '폐포에서 산소를 받아들이고 이산화탄소를 내보내는 가스교환 기관.',
          '산소 흡수 불가 → 심한 저산소증, 의식 저하, 생명 위독.', (30, -20, -45, -40, False),
          [('제1형 폐포세포', '얇고 넓어 산소·CO₂ 확산 담당', 3), ('제2형 폐포세포', '표면활성제를 분비해 폐포 붕괴 방지', 7), ('폐포 대식세포', '먼지·세균을 삼켜 제거', 5)]),
 'liver': ('간', C(140, 60, 40), '해독, 담즙·단백질 합성, 글리코젠 저장을 하는 인체의 화학공장.',
           '독소 해독·혈액응고 인자 합성 불가 → 수일 내 간부전으로 사망.', (20, -20, -5, -35, False),
           [('간세포', '해독·합성·저장; 활면소포체와 미토콘드리아가 풍부', 12), ('쿠퍼세포', '혈액 속 이물질을 먹는 간 상주 대식세포', 5), ('간성상세포', '비타민A 저장, 손상 시 섬유화에 관여', 4)]),
 'stomach': ('위', C(235, 150, 130), '염산과 펩신으로 음식물을 죽처럼 분해해 소화를 시작.',
             '철·비타민B12 흡수 저하, 덤핑증후군 — 식이 조절로 생존 가능.', (5, -5, 0, -5, False),
             [('벽세포', '염산(HCl)과 내인자 분비', 12), ('주세포', '펩시노겐(단백질 분해효소 전구체) 분비', 6), ('점액세포', '점액으로 위벽을 산으로부터 보호', 4)]),
 'pancreas': ('이자(췌장)', C(240, 200, 120), '인슐린·글루카곤으로 혈당 조절 + 소화효소 분비.',
              '당뇨병 유사 고혈당, 지방·단백질 소화 장애 — 인슐린·효소 투여 필요.', (10, -5, 0, -15, False),
              [('베타세포', '인슐린을 분비해 혈당 낮춤', 7), ('알파세포', '글루카곤을 분비해 혈당 높임', 6), ('샘꽈리세포', '소화효소를 십이지장으로 분비', 8)]),
 'spleen': ('지라(비장)', C(120, 40, 90), '낡은 적혈구를 걸러 제거하고 면역 반응을 돕는다.',
            '생존 가능하나 특정 세균 감염에 취약해짐.', (0, 0, 0, 0, False),
            [('비장 대식세포', '낡은 적혈구 분해, 철 재활용', 5), ('B림프구', '항체를 만드는 면역세포', 3), ('T림프구', '감염세포를 직접 공격·면역 조절', 3)]),
 'kidney': ('콩팥(신장)', C(150, 55, 50), '혈액을 여과해 노폐물 배출, 수분·전해질·혈압 조절.',
            '양쪽 제거 시 요독증·고칼륨혈증·부종 → 투석 없이는 수일 내 위독.', (15, 20, -5, -25, False),
            [('발세포(Podocyte)', '사구체 여과막을 구성', 6), ('근위세뇨관세포', '포도당·물·이온 재흡수(미토콘드리아 풍부)', 13), ('사구체 내피세포', '구멍 뚫린 혈관벽으로 혈액 여과', 4)]),
 'intestine': ('장(소장·대장)', C(235, 170, 150), '융털로 영양분과 수분을 흡수하고 장내 미생물과 공생.',
               '영양분·수분 흡수 불가 → 심한 영양실조·탈수.', (15, -15, 0, -20, False),
               [('장 흡수세포', '미세융털로 영양소 흡수', 10), ('술잔세포', '점액 분비로 장벽 보호', 4), ('파네트세포', '항균물질 분비로 장내 세균 조절', 6)]),
 'bladder': ('방광', C(240, 210, 140), '콩팥에서 내려온 소변을 저장했다가 배출.',
             '소변 저장·배출 불가 → 카테터·요루 등 우회 필요(생존 가능).', (5, 0, 0, -5, False),
             [('요로상피세포', '소변의 독성에서 벽을 보호', 4), ('평활근세포', '수축해 소변 배출', 7), ('섬유모세포', '결합조직 지지', 4)]),
}
ORGL = {
 'nucleus': ('핵', '유전정보(DNA)를 보관하는 사령탑. 핵막 구멍으로 mRNA를 내보냄.  ▶ 클릭하면 DNA로 확대!'),
 'mito': ('미토콘드리아', '포도당 등을 산화해 ATP(에너지)를 만드는 세포의 발전소. 자체 DNA 보유.'),
 'er': ('소포체', '단백질·지질 합성/운반 통로. 리보솜이 붙으면 거친면, 없으면 매끈면.'),
 'golgi': ('골지체', '단백질을 가공·포장해 분비소낭으로 내보내는 우체국.'),
 'ribo': ('리보솜', 'mRNA를 읽어 아미노산을 이어 단백질을 합성.'),
 'lyso': ('리소좀', '가수분해효소로 노폐물·세균을 분해하는 세포 내 소화기관.'),
 'vesicle': ('소낭', '물질을 막으로 싸서 세포 안팎으로 운반.'),
 'dend': ('가지돌기', '다른 뉴런의 신호를 받아들이는 수상돌기.'),
}
BASES = 'ATGC'; BCOL = [C(235, 70, 70), C(70, 120, 240), C(70, 210, 110), C(245, 210, 60)]
SKIN = [C(255, 226, 200), C(240, 200, 165), C(212, 160, 120), C(170, 115, 80), C(120, 80, 55), C(85, 55, 40)]
HAIR = [C(230, 200, 120), C(150, 110, 70), C(90, 60, 40), C(25, 22, 22), C(150, 60, 40), C(225, 225, 225)]
EYE = [C(70, 130, 220), C(80, 160, 90), C(110, 70, 40), C(25, 20, 20), C(130, 140, 150), C(200, 140, 40)]
HT = [.93, .96, 1, 1.03, 1.06, 1.1]; MUS = [.9, .95, 1, 1.05, 1.1, 1.16]
GENES = [('피부색(MC1R)', ['매우 밝음', '밝음', '보통', '갈색', '짙은 갈색', '매우 짙음']),
         ('키(GH)', ['×%.2f' % h for h in HT]), ('머리색(HERC2)', ['금발', '연갈색', '갈색', '검정', '적갈색', '백발']),
         ('눈색(OCA2)', ['파랑', '녹색', '갈색', '검정', '회색', '호박색']), ('근육량(MSTN)', ['×%.2f' % m for m in MUS])]
def score(s): return sum((i+1)*b for i, b in enumerate(s)) % 6
rng = random.Random(7); SEQ = []
for g in range(5):
    while True:
        s = [rng.randrange(4) for _ in range(6)]
        if score(s) == 2: break
    SEQ.append(s)

# 약물: (이름, 분류, 작용, 위험, 심박, 수축기혈압, SpO2, 의식, 흐림, 겹침, 일렁임, 채도, 비네팅, 밝기, 색조RGBA, 박동)
DRUGS = [
 ('알코올', '중추억제', 'GABA 작용↑ 억제 → 판단력·균형 저하, 시야 흐림·겹침', '고용량: 호흡억제, 혼수, 급성 알코올중독', 8, -8, -6, -30, .5, .8, .2, .9, .4, .95, (1, .6, .4, .08), 0),
 ('카페인', '각성제', '아데노신 수용체 차단 → 각성, 동공 확대', '과량: 부정맥·불안·경련', 12, 10, 0, 8, 0, 0, 0, 1.1, 0, 1.08, (1, 1, .9, .02), 1),
 ('니코틴', '각성제', '니코틴성 수용체 자극 → 혈관 수축, 심박·혈압 상승', '중독성, 심혈관 질환 위험', 15, 15, -1, 3, 0, 0, 0, 1, .1, 1, (.9, .9, .9, .03), 0),
 ('대마(THC)', '환각/억제', 'CB1 수용체 활성 → 지각 왜곡, 시간 감각 변화, 충혈', '불안·정신병 위험, 인지 저하', 20, -3, 0, -12, .2, .3, .5, 1.3, .2, 1.0, (.6, 1, .5, .07), 0),
 ('코카인', '각성제', '도파민·노르에피네프린 재흡수 차단 → 극단적 흥분, 동공 확대', '심근경색·뇌졸중·돌연사', 45, 40, -3, 15, 0, .1, 0, 1.4, .35, 1.2, (1, 1, 1, .05), 1),
 ('메스암페타민', '각성제', '도파민 방출 폭증 → 과각성, 터널시야', '정신병·심장 손상·치아 손상', 50, 45, -3, 10, 0, .1, .1, 1.3, .6, 1.2, (.9, 1, 1, .05), 1),
 ('헤로인/모르핀(오피오이드)', '중추억제', 'μ-오피오이드 수용체 → 진통·도취, 동공 축소(핀포인트)', '호흡억제로 사망 위험(과량)', -20, -25, -22, -45, .5, .3, .1, .6, .85, .7, (.5, .5, .6, .1), 0),
 ('LSD', '환각제', '5-HT2A 수용체 작용제 → 시각 왜곡, 색·무늬 변형', '불안(배드트립), 플래시백', 15, 8, 0, -10, .1, .4, 1, 1.9, .1, 1.1, (.8, .3, 1, .1), 0),
 ('실로시빈', '환각제', '5-HT2A 작용 → 물결치는 지각, 시각 패턴', '심한 불안·정신적 위험', 10, 6, 0, -12, .1, .3, 1, 1.7, .1, 1.05, (.4, 1, .6, .1), 0),
 ('MDMA', '각성/환각', '세로토닌 방출↑ → 다행감, 동공 확대, 체온 상승', '고체온증·저나트륨혈증', 35, 25, -2, -5, 0, .2, .3, 1.6, .15, 1.15, (1, .5, .9, .08), 1),
 ('디아제팜(벤조디아제핀)', '중추억제', 'GABA-A 작용 증강 → 진정, 졸림', '알코올과 병용 시 호흡억제', -12, -15, -8, -40, .6, .6, 0, .8, .6, .8, (.5, .6, .8, .08), 0),
 ('케타민', '해리성 마취', 'NMDA 수용체 차단 → 해리·유체이탈 감각', '방광 손상, 해리 장애', 10, 12, -3, -35, .3, .5, .8, 1.1, .5, .9, (.6, .8, 1, .1), 0),
 ('프로포폴(마취제)', '전신마취', 'GABA-A 증강 → 급속 의식 소실', '호흡·혈압 저하 — 전문 모니터링 필수', -15, -35, -15, -70, .8, .5, 0, .5, .95, .6, (0, 0, .1, .2), 0),
 ('아드레날린(에피네프린)', '응급약', 'α·β 수용체 자극 → 심박↑, 기관지 확장, 동공 확대', '고혈압·부정맥(아나필락시스 치료제)', 55, 45, 2, 10, 0, 0, 0, 1.2, .5, 1.15, (1, .9, .9, .04), 1),
]
DOSE = {1: .5, 2: 1., 3: 1.8}

# ───────── 상태 ─────────
class G: pass
G.level = 'body'; G.sel = None; G.removed = set(); G.open = False; G.scalpel = False; G.pov = False
G.busy = False; G.stack = []; G.t = 0; G.cut = []; G.act = []; G.dose = 2; G.cell = None; G.md = (0, 0)
G.v = dict(hr=72., sb=120., sp=98., co=100.)

S = {k: Entity(enabled=(k == 'body')) for k in ('body', 'tissue', 'cell', 'dna')}
DirectionalLight(rotation=(40, -30, 0)); AmbientLight(color=Color(.45, .45, .5, 1))
pivot = Entity(); camera.parent = pivot; camera.fov = 60

# ───────── 방 환경 ─────────
room = Entity(parent=S['body'])
Entity(parent=room, model='plane', scale=14, color=C(150, 140, 130), shader=LIT)
Entity(parent=room, model='cube', position=(0, 3, -7), scale=(14, 6, .2), color=C(220, 205, 185), shader=LIT)
Entity(parent=room, model='cube', position=(2.5, 2.4, -6.85), scale=(2, 1.4, .05), color=C(255, 250, 200))
Entity(parent=room, model='cube', position=(-3, 2.4, -6.85), scale=(1.2, 1.6, .05), color=C(220, 60, 60))
Entity(parent=room, model='cube', position=(-2.5, .3, -5), scale=(2.4, .6, .9), color=C(60, 90, 200), shader=LIT)
Entity(parent=room, model='cube', position=(2, .4, -3.5), scale=(1.2, .06, .8), color=C(150, 100, 60), shader=LIT)
Entity(parent=room, model='sphere', position=(1, .25, -2.4), scale=.5, color=C(230, 40, 40), shader=LIT)
Entity(parent=room, model='sphere', position=(-1.2, .45, -3.2), scale=.9, color=C(40, 170, 70), shader=LIT)
Entity(parent=room, model='sphere', position=(3.5, 2.2, -4), scale=.4, color=C(255, 240, 150))

# ───────── 인체 모델 ─────────
body = Entity(parent=S['body']); skin_parts = []
def sk(mesh, pos=(0, 0, 0)):
    e = ball(body, 'skin', mesh, pos, SKIN[2]); skin_parts.append(e); return e
torso_keys = [((0, .86, 0), (.17, .1)), ((0, .95, 0), (.155, .095)), ((0, 1.07, 0), (.135, .088)), ((0, 1.2, 0), (.15, .1)),
              ((0, 1.35, 0), (.175, .11)), ((0, 1.46, 0), (.2, .1)), ((0, 1.53, 0), (.09, .07))]
torso = sk(tube(*path(torso_keys, 30), seg=22))
sk(tube([(0, 1.5, 0), (0, 1.62, 0)], [(.045, .045)]*2, seg=12))
def headfn(x, y, z):
    k = 1 if y > -.3 else 1+(y+.3)*.55
    return x*k, y, z*k
sk(blob(.085, .115, .1, headfn), (0, 1.69, 0)); sk(blob(.012, .014, .02), (0, 1.67, -.1))
for s in (-1, 1):
    sk(tube(*path([((s*.21, 1.46, 0), (.05, .05)), ((s*.25, 1.4, 0), (.048, .048)), ((s*.3, 1.17, 0), (.037, .037)), ((s*.33, .93, -.02), (.028, .028))], 14), seg=12))
    sk(blob(.03, .05, .02), (s*.335, .88, -.02))
    sk(tube(*path([((s*.085, .9, 0), (.085, .085)), ((s*.09, .5, -.005), (.058, .058)), ((s*.085, .1, 0), (.038, .038))], 18), seg=14))
    sk(blob(.04, .03, .09), (s*.085, .04, -.04))
irises = []
for s in (-1, 1):
    ball(body, 'eye', blob(.014, .014, .01), (s*.035, 1.7, -.092), C(250, 250, 250), collide=False)
    irises.append(ball(body, 'eye', blob(.008, .008, .006), (s*.035, 1.7, -.1), EYE[2], collide=False))
hair = ball(body, 'hair', blob(.09, .125, .105, lambda x, y, z: (x, max(y, .15), z)), (0, 1.7, .003), HAIR[2], collide=False)
ghost = Entity(parent=body, model=torso.model, color=Color(.95, .75, .65, .13), double_sided=True, enabled=False)

def gyri(x, y, z):
    k = 1+.05*math.sin(11*x)*math.sin(11*y+1)*math.sin(11*z)+(.05 if abs(x) < .08 else 0)*-1
    return x*k, y*k, z*k
organs = {}
def organ(key, parts):
    o = Entity(parent=body)
    for mesh, pos in parts: ball(o, key, mesh, pos, ORG[key][1])
    organs[key] = o
organ('brain', [(blob(.075, .06, .085, gyri, 28), (0, 1.725, 0))])
organ('heart', [(blob(.05, .062, .045, lambda x, y, z: (x+.25*y*(1 if y > 0 else 0)*.4, y, z)), (.03, 1.3, -.035)),
                (tube([(.02, 1.34, -.03), (.02, 1.42, -.03), (-.02, 1.46, -.02), (-.04, 1.4, 0)], [(.016, .016)]*4, 10), (0, 0, 0))])
organ('lung', [(blob(.065, .115, .07, lambda x, y, z: (x, y, z*(1-.15*y))), (s*.095, 1.31, -.005)) for s in (-1, 1)])
organ('liver', [(blob(.115, .05, .075, lambda x, y, z: (x*(1+.2*(-1 if x < 0 else 0)), y, z)), (-.06, 1.15, -.035))])
organ('stomach', [(blob(.06, .075, .05, lambda x, y, z: (x+.3*y, y, z)), (.075, 1.15, -.03))])
organ('pancreas', [(tube([(-.06, 1.1, -.01), (0, 1.115, -.015), (.08, 1.125, -.01)], [(.012, .01), (.016, .012), (.02, .014)], 10), (0, 0, 0))])
organ('spleen', [(blob(.03, .055, .03), (.125, 1.18, .02))])
organ('kidney', [(blob(.027, .045, .025, lambda x, y, z: (x-.25*(1-abs(y))*(-1 if x < 0 else 1)*0, y, z)), (s*.07, 1.1, .045)) for s in (-1, 1)])
pts = [(.075*math.sin(.8*k), 1.04-.06*(k % 3)*.6+.03*math.cos(.55*k), -.02+.02*math.sin(1.3*k)) for k in range(90)]
organ('intestine', [(tube(pts, [(.014, .014)]*90, 8), (0, 0, 0))])
organ('bladder', [(blob(.04, .035, .035), (0, .93, -.025))])

# ───────── UI ─────────
ui = camera.ui
fade = Entity(parent=ui, model='quad', scale=(3, 3), color=Color(0, 0, 0, 0), z=-.9)
bg = Entity(parent=ui, model='quad', color=Color(0, 0, 0, .55), scale=(.5, .8), position=(.62, .02), z=1)
info = Text(parent=ui, position=(.38, .4), origin=(-.5, .5), wordwrap=26, scale=.9, text='')
crumb = Text(parent=ui, position=(0, .48), origin=(0, 0), text='')
vit = Text(parent=ui, position=(-.85, -.36), origin=(-.5, .5), text='')
tip = Text(parent=ui, text='', scale=1.1, z=-1, background=True)
trait_txt = Text(parent=ui, position=(-.85, .3), origin=(-.5, .5), text='', enabled=False)
def btn(t, x, y, fn, w=.15, h=.045, col=None):
    b = Button(parent=ui, text=t, scale=(w, h), position=(x, y), on_click=fn)
    if col: b.color = col
    return b
def say(t): info.text = t

# ───────── 로직 ─────────
def targets():
    hr, sb, sp, co = 72., 120., 98., 100.; dead = False
    for k in G.removed:
        d = ORG[k][4]; hr += d[0]; sb += d[1]; sp += d[2]; co += d[3]; dead |= d[4]
    for dr, I in G.act:
        hr += dr[4]*I; sb += dr[5]*I; sp += dr[6]*I; co += dr[7]*I
    return hr, sb, max(0, min(100, sp)), max(0, min(100, co)), dead

def traits(): return [score(s) for s in SEQ]
def apply_traits():
    sk_, h, ha, ey, mu = traits()
    for p in skin_parts: p.color = SKIN[sk_]
    body.scale = (MUS[mu], HT[h], MUS[mu]); hair.color = HAIR[ha]
    for e in irises: e.color = EYE[ey]
    trait_txt.text = '[ 형질 ]\n' + '\n'.join('%s: %s' % (GENES[i][0], GENES[i][1][v]) for i, v in enumerate(traits()))
apply_traits()

def organ_text(k):
    d = ORG[k]; t = '[%s]\n%s\n\n구성 세포:\n' % (d[0], d[2]) + '\n'.join('· ' + c[0] for c in d[5])
    if k in G.removed: t += '\n\n▶ 제거 결과\n' + d[3]
    else: t += '\n\n(적출해 보거나 [세포 확대]를 누르세요)'
    return t

def select(k):
    G.sel = k; say(organ_text(k)); b_act.enabled = True
    pivot.animate_position(organs[k].world_position, duration=.6)
    camera.animate('z', -.9, duration=.6)
def deselect():
    G.sel = None; b_act.enabled = False
    pivot.animate_position(Vec3(0, 1, 0), duration=.6); camera.animate('z', -3.2, duration=.6)
    say('메스로 몸통을 드래그해 절개한 뒤, 장기를 클릭해 보세요.' if not G.open else '장기를 클릭하세요.')

def remove_sel():
    if G.sel: organs[G.sel].enabled = False; G.removed.add(G.sel); say(organ_text(G.sel))
def restore_sel():
    if G.sel: organs[G.sel].enabled = True; G.removed.discard(G.sel); say(organ_text(G.sel))
def toggle_scalpel():
    G.scalpel = not G.scalpel
    say('메스 모드: 몸통 위를 드래그해 절개하세요.' if G.scalpel else '메스 해제.')
    if G.open and G.scalpel: close_skin()
def open_skin():
    G.open = True; torso.enabled = False; ghost.enabled = True
    for p in skin_parts: p.collider = None
    for c in G.cut: destroy(c)
    G.cut = []; G.scalpel = False; say('절개 완료! 이제 장기가 보입니다. 장기를 클릭하세요.')
def close_skin():
    G.open = False; torso.enabled = True; ghost.enabled = False; G.scalpel = True
    for p in skin_parts: p.collider = 'box'
    say('피부를 봉합했습니다. 다시 절개할 수 있습니다.')

def go(level, ctx=None, back=False):
    if G.busy: return
    G.busy = True
    if not back: camera.animate('z', camera.z*.35, duration=.35)
    fade.animate('alpha', 1, duration=.35)
    def f():
        if not back: G.stack.append((G.level, G.ctx))
        swap(level, ctx); fade.animate('alpha', 0, duration=.4); G.busy = False
    invoke(f, delay=.4)
def back():
    if G.busy: return
    if G.level == 'body':
        if G.sel: deselect()
    else:
        lv, cx = G.stack.pop(); go(lv, cx, back=True)
G.ctx = None

def clear(e):
    for c in list(e.children): destroy(c)

def swap(level, ctx):
    for s in S.values(): s.enabled = False
    S[level].enabled = True; G.level = level; G.ctx = ctx; pivot.rotation = (0, 180 if level == 'body' else 0, 0)
    b_act.enabled = False; trait_txt.enabled = (level == 'dna'); G.pov = False
    camera.z = -{'body': 3.2, 'tissue': 8, 'cell': 6, 'dna': 12}[level]
    pivot.position = Vec3(0, 1, 0) if level == 'body' else Vec3(0, 0, 0)
    names = ['인체']
    if G.sel and level != 'body': names.append(ORG[G.sel][0])
    if level in ('cell', 'dna') and G.cell is not None: names.append(ORG[G.sel][5][G.cell][0])
    if level == 'dna': names.append('핵 · DNA')
    crumb.text = ' ▶ '.join(names)
    if level == 'body': G.sel = None; say('메스 버튼을 누르고 몸통을 드래그해 절개하세요.')
    elif level == 'tissue': build_tissue()
    elif level == 'cell': build_cell()
    elif level == 'dna': build_dna()

def zoom_tissue():
    if G.sel: go('tissue')

def build_tissue():
    r = S['tissue']; clear(r); k = G.sel
    for i, c in enumerate(ORG[k][5]):
        x = (i-1)*3.2
        e = Entity(parent=r, model='sphere', position=(x, 0, 0), scale=2.4, color=Color(.95, .6, .6, .3), double_sided=True, collider='sphere'); e.kind = i
        Entity(parent=e, model='sphere', scale=.38, color=C(70, 90, 200), shader=LIT)
        for _ in range(c[2]//2): Entity(parent=e, model='sphere', scale=(.12, .06, .06), position=Vec3(*[random.uniform(-.3, .3) for _ in range(3)]), color=C(240, 130, 40))
    say('[%s의 세포]\n' % ORG[k][0] + '\n\n'.join('● %s\n   %s' % (c[0], c[1]) for c in ORG[k][5]) + '\n\n세포를 클릭하면 확대됩니다.')

def build_cell():
    r = S['cell']; clear(r); c = ORG[G.sel][5][G.cell]; R = random.Random(3)
    Entity(parent=r, model='sphere', scale=5, color=Color(.95, .65, .7, .16), double_sided=True)
    def add(kind, model, pos, sc, col, rot=(0, 0, 0)):
        e = Entity(parent=r, model=model, position=pos, scale=sc, color=col, rotation=rot, shader=LIT, collider='box'); e.kind = kind; return e
    def rp(a, b):
        v = Vec3(R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(-1, 1)).normalized(); return v*R.uniform(a, b)
    add('nucleus', 'sphere', (0, 0, 0), 1.3, C(70, 90, 210)); add('nucleus', 'sphere', (.2, .1, -.5), .35, C(30, 40, 120))
    for _ in range(c[2]): add('mito', 'sphere', rp(1.1, 2.0), (.55, .25, .25), C(245, 140, 40), (R.uniform(0, 180),)*3)
    pts = [(1.0*math.cos(a), .35*math.sin(3*a), 1.0*math.sin(a)) for a in [i*.2 for i in range(32)]]
    e = ball(r, 'er', tube(pts, [(.07, .07)]*32, 8), (0, 0, 0), C(240, 220, 120)); e.scale = 1.15
    for i in range(4): add('golgi', 'sphere', (1.6, .5+i*.14-.25, 0), (1.0-.06*i, .08, .6), C(230, 190, 90), (0, 0, 20))
    for _ in range(40): add('ribo', 'sphere', rp(1.1, 2.1), .09, C(40, 40, 60))
    for _ in range(3): add('lyso', 'sphere', rp(1.2, 2.0), .22, C(80, 190, 90))
    for _ in range(4): add('vesicle', 'sphere', rp(1.2, 2.1), .15, C(240, 150, 200))
    if '뉴런' in c[0]:
        for _ in range(5):
            d = Vec3(R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(-1, 1)).normalized()
            e = ball(r, 'dend', tube([tuple(d*2.0), tuple(d*3.3), tuple(d*4.4+Vec3(.3, .3, 0))], [(.2, .2), (.12, .12), (.04, .04)], 10), (0, 0, 0), C(235, 190, 200))
    say('[%s]\n%s\n\n세포소기관을 클릭해 보세요.\n핵을 클릭하면 DNA로 확대됩니다.' % (c[0], c[1]))

dna_rods = {}
def build_dna():
    r = S['dna']; clear(r); r.rotation = (0, 0, 0); dna_rods.clear()
    for sgn in (0, 1):
        P = [(.9*math.cos(i*.55/4+sgn*math.pi), (i/4-15)*.24, .9*math.sin(i*.55/4+sgn*math.pi)) for i in range(120)]
        Entity(parent=r, model=tube(P, [(.05, .05)]*120, 8), color=C(190, 190, 220), shader=LIT)
    for i in range(30):
        y = (i-15)*.24+.06; a = i*.55
        L = Vec3(.9*math.cos(a), y, .9*math.sin(a)); Rr = Vec3(-L.x, y, -L.z); M = Vec3(0, y, 0); pair = []
        for end in (L, Rr):
            e = Entity(parent=r, model='cube', position=(M+end)/2, scale=(.09, .09, .9*.5+.05), shader=LIT, collider='box'); e.kind = ('base', i)
            e.look_at(end); pair.append(e)
        dna_rods[i] = pair; recolor(i)
    say('[핵 속 DNA]\n염기쌍(막대)을 클릭하면 A→T→G→C로 바뀌고 반대 가닥은 상보적(A-T, G-C)으로 따라옵니다.\n\n6개 염기쌍 = 1개 유전자.\n서열이 바뀌면 오른쪽 아래 형질이 바뀌고, [인체에서 확인]으로 3D 인체에 반영된 모습을 볼 수 있어요.')
def recolor(i):
    g, k = divmod(i, 6); b = SEQ[g][k]; dna_rods[i][0].color = BCOL[b]; dna_rods[i][1].color = BCOL[b ^ 1]
def flip(i):
    g, k = divmod(i, 6); SEQ[g][k] = (SEQ[g][k]+1) % 4; recolor(i); apply_traits()
    say('유전자 [%s] 염기 변경: %s-%s\n→ 형질: %s' % (GENES[g][0], BASES[SEQ[g][k]], BASES[SEQ[g][k] ^ 1], GENES[g][1][traits()[g]]))
def to_body():
    G.stack = []; G.sel = None; go('body')

def click(e):
    if not e or not hasattr(e, 'kind'): return
    k = e.kind
    if G.level == 'body' and k in ORG: select(k)
    elif G.level == 'tissue' and isinstance(k, int): G.cell = k; go('cell')
    elif G.level == 'cell' and k == 'nucleus': go('dna')
    elif G.level == 'cell' and k in ORGL: say('[%s]\n%s' % ORGL[k])
    elif G.level == 'dna' and isinstance(k, tuple): flip(k[1])

# ───────── 약물 패널 ─────────
drug_btns = []
def give(d):
    G.act.append([d, DOSE[G.dose]]); lv = {1: '소량', 2: '보통', 3: '과량'}[G.dose]
    say('[%s 투여 - %s]\n분류: %s\n작용: %s\n위험: %s\n\n※ V키(시야 버튼)로 투여자의 시야를 확인하세요.' % (d[0], lv, d[1], d[2], d[3]))
def toggle_drugs():
    for b in drug_btns: b.enabled = not b.enabled
for i, d in enumerate(DRUGS):
    b = btn(d[0].split('(')[0], -.78+(i//7)*.2, .36-(i % 7)*.05, (lambda d=d: give(d)), w=.19, h=.042, col=C(90, 40, 60)); b.enabled = False; drug_btns.append(b)
for n, lab in ((1, '소량'), (2, '보통'), (3, '과량')):
    b = btn(lab, -.82+(n-1)*.12, .0, (lambda n=n: setattr(G, 'dose', n)), w=.11, h=.04); b.enabled = False; drug_btns.append(b)
b = btn('약물 제거', -.7, -.05, lambda: G.act.clear(), w=.15, h=.04); b.enabled = False; drug_btns.append(b)

def toggle_pov():
    if G.level != 'body': return
    G.pov = not G.pov
    if G.pov:
        h = HT[traits()[1]]; pivot.position = Vec3(0, 1.7*h, -.05); pivot.rotation = (0, 180, 0); camera.z = 0
        for p in skin_parts: p.enabled = False
        hair.enabled = False; say('투여자의 시야 모드 (마우스 드래그로 고개 돌리기, V로 종료)')
    else:
        for p in skin_parts: p.enabled = True
        hair.enabled = True; torso.enabled = not G.open
        pivot.position = Vec3(0, 1, 0); pivot.rotation = (0, 180, 0); camera.z = -3.2

btn('메스', -.78, .45, toggle_scalpel); btn('시야(V)', -.62, .45, toggle_pov); btn('약물', -.46, .45, toggle_drugs)
btn('인체에서 확인', -.26, .45, to_body, w=.2); btn('◀ 뒤로', -.06, .45, back)
act_btns = [btn('적출', .46, -.43, remove_sel, col=C(150, 40, 40)), btn('복원', .62, -.43, restore_sel), btn('세포 확대', .78, -.43, zoom_tissue, w=.17, col=C(40, 110, 70))]
class _A:
    def __init__(s): s._e = True
    @property
    def enabled(s): return s._e
    @enabled.setter
    def enabled(s, v):
        s._e = v
        for b in act_btns: b.enabled = v
b_act = _A(); b_act.enabled = False

# ───────── POV 셰이더 ─────────
try:
    POVS = Shader(language=Shader.GLSL, vertex='''#version 140
uniform mat4 p3d_ModelViewProjectionMatrix; in vec4 p3d_Vertex; in vec2 p3d_MultiTexCoord0; out vec2 uv;
void main(){ gl_Position = p3d_ModelViewProjectionMatrix*p3d_Vertex; uv = p3d_MultiTexCoord0; }''', fragment='''#version 140
uniform sampler2D tex; uniform float t,blur,dbl,warp,sat,vig,bright; uniform vec4 tint; in vec2 uv; out vec4 fragColor;
vec3 smp(vec2 p){ vec3 c=vec3(0.); for(int i=-2;i<=2;i++){ for(int j=-2;j<=2;j++){ c+=texture(tex,p+vec2(i,j)*blur*0.004).rgb; } } return c/25.; }
void main(){
 vec2 p=uv+warp*0.012*vec2(sin(uv.y*14.+t*2.),cos(uv.x*12.+t*1.7));
 vec2 o=vec2(dbl*0.025*(1.+0.4*sin(t*.8)),dbl*0.008);
 vec3 c=0.5*(smp(p+o)+smp(p-o));
 float g=dot(c,vec3(.3,.59,.11)); c=mix(vec3(g),c,sat); c=mix(c,tint.rgb,tint.a);
 c*=1.-vig*smoothstep(.2,.75,length(uv-.5)); c*=bright; fragColor=vec4(c,1.); }''',
        default_input={'t': 0., 'blur': 0., 'dbl': 0., 'warp': 0., 'sat': 1., 'vig': 0., 'bright': 1., 'tint': Vec4(0, 0, 0, 0)})
    camera.shader = POVS; HAS_FX = True
except Exception as ex:
    print('POV 셰이더를 사용할 수 없습니다:', ex); HAS_FX = False

def fx_update():
    if not HAS_FX: return
    p = dict(blur=0., dbl=0., warp=0., vig=0.); sat = 1.; br = 1.; tn = [0., 0., 0., 0.]; pulse = 0
    if G.pov:
        for d, I in G.act:
            p['blur'] += d[8]*I; p['dbl'] += d[9]*I; p['warp'] += d[10]*I; p['vig'] += d[12]*I
            sat += (d[11]-1)*I; br += (d[13]-1)*I; pulse |= d[15]
            for j in range(3): tn[j] += d[14][j]*d[14][3]*I
            tn[3] += d[14][3]*I
        if G.v['co'] < 60: p['vig'] += (60-G.v['co'])/50; p['blur'] += (60-G.v['co'])/40
        if pulse: br *= 1+.12*math.sin(G.t*G.v['hr']/60*6.283)
    a = min(tn[3], .5); rgb = [min(1, tn[j]/max(tn[3], 1e-3)) for j in range(3)]
    camera.set_shader_input('t', G.t); camera.set_shader_input('blur', min(p['blur'], 4)); camera.set_shader_input('dbl', min(p['dbl'], 3))
    camera.set_shader_input('warp', min(p['warp'], 3)); camera.set_shader_input('sat', max(0, min(sat, 2.5)))
    camera.set_shader_input('vig', min(p['vig'], 1.2)); camera.set_shader_input('bright', max(.1, min(br, 1.6)))
    camera.set_shader_input('tint', Vec4(rgb[0], rgb[1], rgb[2], a))

# ───────── 메인 루프 ─────────
def update():
    dt = time.dt; G.t += dt
    if mouse.left and not G.scalpel and not G.busy and not isinstance(mouse.hovered_entity, Button):
        pivot.rotation_y += mouse.velocity[0]*150
        pivot.rotation_x = max(-70, min(70, pivot.rotation_x - mouse.velocity[1]*100))
    if G.level == 'dna': S['dna'].rotation_y += 12*dt
    if G.level == 'tissue':
        for i, c in enumerate(S['tissue'].children): c.y = .15*math.sin(G.t+i)
    if G.scalpel and mouse.left and G.level == 'body' and not G.open:
        e = mouse.hovered_entity
        if e and getattr(e, 'kind', None) == 'skin' and mouse.world_point:
            if not G.cut or (G.cut[-1].position-mouse.world_point).length() > .02:
                G.cut.append(Entity(parent=S['body'], model='sphere', scale=.014, color=C(200, 20, 20), position=mouse.world_point))
    for a in G.act: a[1] -= dt*.02
    G.act = [a for a in G.act if a[1] > 0]
    tg = targets(); dead = tg[4] or tg[2] < 20 or tg[3] < 3
    for k, v in zip(('hr', 'sb', 'sp', 'co'), (0 if dead else tg[0], 0 if dead else tg[1], 0 if tg[4] else tg[2], 0 if dead else tg[3])):
        G.v[k] += (v-G.v[k])*min(1, dt*.5)
    hr = G.v['hr']; st = '사망' if dead and G.v['hr'] < 5 else ('위독' if tg[2] < 70 or tg[3] < 30 or tg[0] > 150 else '주의' if tg[3] < 80 or abs(tg[0]-72) > 25 else '정상')
    vit.text = '심박수 %d bpm\n혈압 %d/%d\nSpO₂ %d%%\n의식 %d%%\n상태: %s%s' % (G.v['hr'], G.v['sb'], G.v['sb']*.65, G.v['sp'], G.v['co'], st, '\n활성 약물: ' + ', '.join(a[0][0].split('(')[0] for a in G.act) if G.act else '')
    if hr > 5:
        beat = max(0, math.sin(G.t*hr/60*6.283))**3; organs['heart'].scale = 1+.08*beat
        organs['lung'].scale = 1+.03*math.sin(G.t*(1.2 if hr < 100 else 2.4))
    e = mouse.hovered_entity; k = getattr(e, 'kind', None) if e else None
    if G.level == 'body' and k in ORG: tip.text = ORG[k][0]
    elif G.level == 'cell' and k in ORGL: tip.text = ORGL[k][0]
    elif G.level == 'tissue' and isinstance(k, int): tip.text = ORG[G.sel][5][k][0]
    elif G.level == 'dna' and isinstance(k, tuple): tip.text = '%s · 염기쌍 #%d' % (GENES[k[1]//6][0], k[1] % 6+1)
    else: tip.text = ''
    tip.position = (mouse.x+.02, mouse.y+.03)
    fx_update()

def input(key):
    if key == 'left mouse down': G.md = (mouse.x, mouse.y)
    elif key == 'left mouse up':
        if G.scalpel:
            if len(G.cut) >= 10: open_skin()
            else:
                for c in G.cut: destroy(c)
                G.cut = []
        elif abs(mouse.x-G.md[0])+abs(mouse.y-G.md[1]) < .012 and not G.pov: click(mouse.hovered_entity)
    elif key == 'scroll up' and not G.pov: camera.z = min(camera.z+.3, -.3)
    elif key == 'scroll down' and not G.pov: camera.z -= .3
    elif key == 'v': toggle_pov()
    elif key == 'backspace': back()

pivot.position = Vec3(0, 1, 0); pivot.rotation_y = 180; camera.z = -3.2; crumb.text = '인체'
say('Bio3D 인체 탐험\n\n1) [메스] → 몸통을 드래그해 절개\n2) 장기 클릭 → 설명 / 적출 / 세포 확대\n3) 세포 → 소기관 → 핵 → DNA 조작\n4) [약물]로 약물 투여 후 [시야(V)]로 체험\n\n※ 교육용 시뮬레이션입니다.')
app.run()
