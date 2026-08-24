from __future__ import annotations
import math, re
from typing import Any
from .schemas import SceneRequest, SceneResult, Simulation3DRequest, Simulation3DResult, CADRequest

class Visual3DEngine:
    """Procedural scientific/CAD/physics 3D scene engine.

    Produces deterministic mesh/line/point geometry and bounded numerical
    simulation frames. It deliberately labels conceptual models and does not
    claim experimental validation or industrial CAE certification.
    """
    def __init__(self):
        self.library = {
            'atom': ('ATOM', 'Atomic structure', 'atom'),
            'molecule': ('MOLECULE', 'Ball-and-stick molecule', 'molecule'),
            'dna': ('DNA', 'Double helix', 'dna'),
            'cell': ('CELL', 'Conceptual biological cell', 'cell'),
            'heart': ('HEART', 'Conceptual cardiac anatomy', 'heart'),
            'solar_system': ('SOLAR SYSTEM', 'Orbital planetary system', 'solar'),
            'planet': ('PLANET', 'Planetary body with atmosphere layers', 'planet'),
            'turbine': ('TURBINE', 'Rotating turbine assembly', 'turbine'),
            'gearbox': ('GEARBOX', 'Two-gear mechanical transmission', 'gearbox'),
            'bridge': ('BRIDGE', 'Truss bridge structure', 'bridge'),
            'circuit': ('CIRCUIT', 'Circuit topology', 'circuit'),
            'robot_arm': ('ROBOT ARM', 'Planar articulated arm', 'robot_arm'),
        }

    def scene(self, req: SceneRequest) -> SceneResult:
        if req.kind == 'library':
            key = req.name.lower().strip().replace(' ', '_')
            if key not in self.library:
                raise ValueError(f'Unknown 3D library model: {req.name}')
            title, desc, builder = self.library[key]
            data = self._build(builder, req.parameters)
            return self._result(title, desc, data, 'LIBRARY_MODEL')
        if req.kind == 'cad':
            data = self._cad(req.name, req.parameters)
            return self._result(f'CAD / {req.name.upper()}', 'Parametric CAD primitive', data, 'PARAMETRIC_CAD')
        builder = self._classify(req.prompt or req.name)
        data = self._build(builder, req.parameters)
        return self._result(f'GENERATED / {builder.upper()}', 'Procedural text-directed 3D scene', data, 'PROCEDURAL_GENERATOR')

    def simulate(self, req: Simulation3DRequest) -> Simulation3DResult:
        p = {k: float(v) for k, v in req.parameters.items()}
        frames=[]
        if req.kind == 'gravity':
            pos=[p.get('x',0),p.get('y',1),p.get('z',0)]; vel=[p.get('vx',1),p.get('vy',0),p.get('vz',0)]; g=p.get('g',-9.81)
            for i in range(req.steps+1):
                frames.append({'t':i*req.dt,'objects':[{'id':'body','position':pos.copy(),'velocity':vel.copy()}]})
                vel[1]+=g*req.dt
                for j in range(3): pos[j]+=vel[j]*req.dt
        elif req.kind == 'projectile':
            pos=[0,p.get('height',0),0]; v=[p.get('speed',10)*math.cos(p.get('angle_deg',45)*math.pi/180),p.get('speed',10)*math.sin(p.get('angle_deg',45)*math.pi/180),0]; g=p.get('g',-9.81)
            for i in range(req.steps+1):
                frames.append({'t':i*req.dt,'objects':[{'id':'projectile','position':pos.copy(),'velocity':v.copy()}]})
                v[1]+=g*req.dt
                for j in range(3): pos[j]+=v[j]*req.dt
        elif req.kind == 'spring':
            x=p.get('x',0.5); v=p.get('v',0); k=p.get('k',10); m=max(p.get('mass',1),1e-9); damping=p.get('damping',0.1)
            for i in range(req.steps+1):
                frames.append({'t':i*req.dt,'objects':[{'id':'mass','position':[x,0,0],'velocity':[v,0,0]}]})
                a=(-k*x-damping*v)/m; v+=a*req.dt; x+=v*req.dt
        elif req.kind == 'orbit':
            r=max(p.get('radius',1),1e-6); mu=p.get('mu',1); w=math.sqrt(mu/r**3)
            for i in range(req.steps+1):
                t=i*req.dt; a=w*t; frames.append({'t':t,'objects':[{'id':'orbiter','position':[r*math.cos(a),0,r*math.sin(a)],'velocity':[-r*w*math.sin(a),0,r*w*math.cos(a)]},{'id':'primary','position':[0,0,0]}]})
        elif req.kind == 'heat':
            n=int(max(4,min(32,p.get('grid',12)))); alpha=p.get('diffusivity',0.15); grid=[[0.0]*n for _ in range(n)]; grid[n//2][n//2]=1.0
            for i in range(req.steps+1):
                frames.append({'t':i*req.dt,'field':grid})
                nxt=[[grid[y][x] for x in range(n)] for y in range(n)]
                for y in range(1,n-1):
                    for x in range(1,n-1): nxt[y][x]=grid[y][x]+alpha*req.dt*(grid[y+1][x]+grid[y-1][x]+grid[y][x+1]+grid[y][x-1]-4*grid[y][x])
                grid=nxt
        else:
            # Stable, bounded 2D advection-like particle field for visualization.
            count=int(max(4,min(200,p.get('particles',40)))); speed=p.get('speed',0.35)
            for i in range(req.steps+1):
                objs=[]
                for j in range(count):
                    a=2*math.pi*j/count + i*req.dt*speed
                    r=0.25+0.55*((j*37)%count)/count
                    objs.append({'id':f'p{j}','position':[r*math.cos(a),0.12*math.sin(a*3+i*.1),r*math.sin(a)]})
                frames.append({'t':i*req.dt,'objects':objs})
        return Simulation3DResult(status='SIMULATION_COMPLETE',kind=req.kind,frames=frames,visualization={'type':'3d_scene','animation':'time_indexed'},provenance={'engine':'tinkle.visual3d','solver':req.kind,'steps':req.steps,'dt':req.dt},limitations=['Numerical demonstration models; not a validated domain-specific CFD/FEA/CAE solver.','Simulation results are computational outputs and not experimental evidence.'])

    def catalog(self):
        return [{'id':k,'title':v[0],'description':v[1]} for k,v in self.library.items()]

    def _result(self,title,desc,data,status):
        data.update({'title':title,'description':desc})
        return SceneResult(status='SCENE_READY',scene=data,provenance={'engine':'tinkle.visual3d','mode':status},limitations=['Procedural/conceptual geometry unless explicitly marked CAD.','Scientific library models are explanatory representations, not measurement-grade anatomical/atomic reconstructions.'])

    def _classify(self,text):
        s=text.lower()
        rules=[('dna',r'dna|double helix|حمض نووي'),('heart',r'heart|قلب'),('cell',r'cell|خلية'),('molecule',r'molecule|جزيء'),('solar',r'solar|planet|كوكب|نظام شمسي'),('turbine',r'turbine|توربين'),('gearbox',r'gear|ترس|gearbox'),('bridge',r'bridge|جسر'),('circuit',r'circuit|دائرة كهرب'),('robot_arm',r'robot arm|ذراع روبوت'),('atom',r'atom|ذرة|electron|إلكترون')]
        for name,pat in rules:
            if re.search(pat,s): return name
        return 'concept'

    def _build(self,builder,p):
        b=getattr(self,f'_build_{builder}',None)
        return b(p) if b else self._build_concept(p)

    def _mesh(self,vertices,indices,material='solid'):
        return {'geometry':'mesh','vertices':vertices,'indices':indices,'material':material}
    def _lines(self,segments,material='line'):
        return {'geometry':'lines','segments':segments,'material':material}
    def _points(self,points,material='points'):
        return {'geometry':'points','points':points,'material':material}
    def _sphere(self,r=1,lat=12,lon=20,center=(0,0,0)):
        v=[]; idx=[]
        for i in range(lat+1):
            t=math.pi*i/lat; st,ct=math.sin(t),math.cos(t)
            for j in range(lon):
                a=2*math.pi*j/lon; v += [center[0]+r*st*math.cos(a),center[1]+r*ct,center[2]+r*st*math.sin(a)]
        for i in range(lat):
            for j in range(lon):
                a=i*lon+j;b=i*lon+(j+1)%lon;c=(i+1)*lon+(j+1)%lon;d=(i+1)*lon+j;idx += [a,b,c,a,c,d]
        return self._mesh(v,idx,'solid')
    def _cylinder(self,r=0.3,h=1,n=20):
        v=[];idx=[]
        for y in (-h/2,h/2):
            for i in range(n): a=2*math.pi*i/n;v += [r*math.cos(a),y,r*math.sin(a)]
        for i in range(n): j=(i+1)%n;idx += [i,j,n+j,i,n+j,n+i]
        return self._mesh(v,idx,'metal')
    def _build_atom(self,p): return {'objects':[self._sphere(.45),'electrons'], 'annotations':['nucleus','electron shells','conceptual probability visualization'], 'extras':{'electrons':[[.9,0,0],[-.9,0,0],[0,0,.9],[0,0,-.9]]}}
    def _build_molecule(self,p): return {'objects':[self._sphere(.38,10,16,(0,0,0)),self._sphere(.24,10,16,(.65,.05,0)),self._sphere(.24,10,16,(-.65,.05,0))], 'annotations':['atom','bond','atom']}
    def _build_dna(self,p):
        pts=[]; seg=[]; n=160
        for i in range(n-1):
            a=i*.18; x1=.55*math.cos(a);z1=.55*math.sin(a);x2=-x1;z2=-z1;y=i*.035-2.8; yn=(i+1)*.035-2.8
            seg += [[[x1,y,z1],[.0,y,0]],[[.0,y,0],[x2,y,z2]]];pts += [[x1,y,z1],[x2,y,z2]]
            if i%4==0: seg += [[[x1,y,z1],[.55*math.cos(a+.35),yn,.55*math.sin(a+.35)]],[[x2,y,z2],[-.55*math.cos(a+.35),yn,-.55*math.sin(a+.35)]]]
        return {'objects':[self._lines(seg,'helix')], 'points':pts, 'annotations':['strand A','base-pair ladder','strand B']}
    def _build_cell(self,p): return {'objects':[self._sphere(1.0,18,28),self._sphere(.38,14,20,(.2,.15,.05))], 'annotations':['cell membrane','nucleus','organelles (conceptual)']}
    def _build_heart(self,p): return {'objects':[self._sphere(.75,18,24,(0,.1,0)),self._cylinder(.22,.9,18)], 'annotations':['ventricular mass','outflow vessel','conceptual anatomy']}
    def _build_solar(self,p): return {'objects':[self._sphere(.35),self._sphere(.12,10,16,(.8,0,0)),self._sphere(.16,10,16,(1.35,0,0)),self._lines([[[.8,0,0],[.8,0,0]],[[0,0,0],[1.35,0,0]]])], 'annotations':['star','inner planet','outer planet','orbital relationship']}
    def _build_planet(self,p): return {'objects':[self._sphere(.8),self._sphere(.86,18,28)], 'annotations':['planet surface','atmospheric shell']}
    def _build_turbine(self,p):
        objs=[self._cylinder(.28,1.4),self._sphere(.18)]
        seg=[]
        for i in range(8):
            a=i*math.pi/4;seg.append([[0,0,0],[1.0*math.cos(a),.18*math.sin(a*2),1.0*math.sin(a)]])
        objs.append(self._lines(seg,'blades'));return {'objects':objs,'annotations':['shaft','hub','blade set']}
    def _build_gearbox(self,p): return {'objects':[self._gear(1,24,.18,(0,0,0)),self._gear(.55,14,.18,(1.1,0,0))],'annotations':['drive gear','driven gear','mesh interface']}
    def _gear(self,r,teeth,h,center):
        seg=[]; pts=[]
        for i in range(teeth):
            a=2*math.pi*i/teeth; b=2*math.pi*(i+1)/teeth; rr=r*(1.12 if i%2==0 else .92)
            pts.append([center[0]+rr*math.cos(a),center[1],center[2]+rr*math.sin(a)])
            seg.append([[center[0]+rr*math.cos(a),center[1],center[2]+rr*math.sin(a)],[center[0]+rr*math.cos(b),center[1],center[2]+rr*math.sin(b)]])
        return self._lines(seg,'gear')
    def _build_bridge(self,p):
        seg=[]
        for x in range(-5,6): seg.append([[x*.35,0,-.6],[x*.35,0,.6]])
        for x in range(-5,5): seg += [[[x*.35,0,-.6],[(x+1)*.35,0,.6]],[[x*.35,0,.6],[(x+1)*.35,0,-.6]]]
        return {'objects':[self._lines(seg,'truss')],'annotations':['truss members','load path','supports']}
    def _build_circuit(self,p):
        seg=[[[ -1,0,0],[1,0,0]],[[0,-.8,0],[0,.8,0]]]
        return {'objects':[self._lines(seg,'conductors'),self._sphere(.12,10,16,(-1,0,0)),self._sphere(.12,10,16,(1,0,0))],'annotations':['input','node','output']}
    def _build_robot_arm(self,p):
        return {'objects':[self._cylinder(.16,.5),self._cylinder(.12,.9)],'annotations':['base joint','link','end effector']}
    def _build_concept(self,p): return {'objects':[self._sphere(.5)],'annotations':['concept','relationship','unknown / unverified']}
    def _cad(self,name,p):
        if name=='box':
            x,y,z=[max(p.get(k,1),1e-6) for k in ('width','height','depth')];v=[[-x/2,-y/2,-z/2],[x/2,-y/2,-z/2],[x/2,y/2,-z/2],[-x/2,y/2,-z/2],[-x/2,-y/2,z/2],[x/2,-y/2,z/2],[x/2,y/2,z/2],[-x/2,y/2,z/2]];idx=[0,1,2,0,2,3,4,6,5,4,7,6,0,4,5,0,5,1,3,2,6,3,6,7,0,3,7,0,7,4,1,5,6,1,6,2];return {'objects':[self._mesh([c for q in v for c in q],idx,'cad')],'parameters':{'width':x,'height':y,'depth':z},'annotations':['parametric box','dimensions in model units']}
        if name=='cylinder': return {'objects':[self._cylinder(p.get('radius',.5),p.get('height',1),32)],'parameters':p,'annotations':['parametric cylinder','axis','radius','height']}
        if name=='sphere': return {'objects':[self._sphere(p.get('radius',.5),20,32)],'parameters':p,'annotations':['parametric sphere','radius']}
        if name=='gear': return {'objects':[self._gear(p.get('radius',1),int(max(4,p.get('teeth',20))),p.get('thickness',.2),(0,0,0))],'parameters':p,'annotations':['parametric gear','teeth','pitch radius']}
        if name=='shaft': return {'objects':[self._cylinder(p.get('radius',.15),p.get('length',1.5),24)],'parameters':p,'annotations':['shaft','diameter','length']}
        if name=='beam': return self._cad('box',{'width':p.get('length',2),'height':p.get('height',.2),'depth':p.get('width',.2)})
        if name=='pipe': return {'objects':[self._cylinder(p.get('radius',.35),p.get('length',1.5),32)],'parameters':p,'annotations':['pipe','inner/outer radius represented conceptually']}
        return {'objects':[self._cad('box',{'width':1,'height':1,'depth':.5})['objects'][0]],'parameters':p,'annotations':['bracket placeholder geometry; validate before manufacture']}
