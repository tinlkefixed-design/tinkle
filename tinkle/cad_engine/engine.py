from __future__ import annotations
import math
from typing import Any
from .schemas import CADAssemblyRequest,CADPart,CADResult
class CADEngine:
    def build(self, req:CADAssemblyRequest)->CADResult:
        parts=[]; all_v=[]; all_f=[]
        for part in req.parts:
            v,f=self._primitive(part)
            v=[self._transform(p,part.position,part.rotation_deg) for p in v]
            offset=len(all_v); all_v.extend(v); all_f.extend([[i+offset for i in face] for face in f])
            parts.append({'name':part.name,'primitive':part.primitive,'parameters':part.parameters,'position':part.position,'rotation_deg':part.rotation_deg,'vertex_count':len(v)})
        assembly={'name':req.name,'parts':parts,'mesh':{'vertices':all_v,'faces':all_f}}
        data=None
        if req.export=='obj': data=self._obj(all_v,all_f)
        elif req.export=='stl': data=self._stl(all_v,all_f)
        else: data=''
        return CADResult(status='CAD_ASSEMBLY_READY',assembly=assembly,export_format=req.export,export_data=data,
            provenance={'engine':'tinkle.cad_engine','parts':len(parts),'format':req.export},
            limitations=['Mesh-based parametric export; STEP/IGES B-rep kernels are not claimed.','Geometry must be dimensionally and manufacturability validated before fabrication.'])
    def _primitive(self,p:CADPart):
        if p.primitive=='box':
            x=p.parameters.get('width',1)/2;y=p.parameters.get('height',1)/2;z=p.parameters.get('depth',1)/2
            v=[[-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],[-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]]
            f=[[0,1,2,3],[4,7,6,5],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2]]
        elif p.primitive=='sphere':
            r=p.parameters.get('radius',.5); seg=24; rings=12; v=[];f=[]
            for i in range(rings+1):
                t=math.pi*i/rings
                for j in range(seg):
                    a=2*math.pi*j/seg;v.append([r*math.sin(t)*math.cos(a),r*math.cos(t),r*math.sin(t)*math.sin(a)])
            for i in range(rings):
                for j in range(seg):
                    a=i*seg+j;b=i*seg+(j+1)%seg;c=(i+1)*seg+(j+1)%seg;d=(i+1)*seg+j;f.append([a,b,c,d])
        else:
            r=p.parameters.get('radius',.3);h=p.parameters.get('height',1);seg=24;v=[];f=[]
            for y in (-h/2,h/2):
                for j in range(seg):
                    a=2*math.pi*j/seg;v.append([r*math.cos(a),y,r*math.sin(a)])
            f += [[j,(j+1)%seg,seg+(j+1)%seg,seg+j] for j in range(seg)]
            f += [list(range(seg-1,-1,-1)),list(range(seg,2*seg))]
        return v,f
    def _transform(self,p,pos,rot):
        x,y,z=p;rx,ry,rz=[math.radians(a) for a in rot]
        x,y,z=x,y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
        x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
        x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
        return [x+pos[0],y+pos[1],z+pos[2]]
    def _obj(self,v,f):
        return '\n'.join([*(f'v {x:.9g} {y:.9g} {z:.9g}' for x,y,z in v),*(f'f {" ".join(str(i+1) for i in face)}' for face in f)])+'\n'
    def _stl(self,v,f):
        out=['solid tinkle_assembly']
        for face in f:
            if len(face)<3: continue
            for tri in ([face[0],face[1],face[2]],*[ [face[0],face[i],face[i+1]] for i in range(2,len(face)-1)]):
                a,b,c=[v[i] for i in tri]; n=self._normal(a,b,c);out += [f' facet normal {n[0]:.9g} {n[1]:.9g} {n[2]:.9g}','  outer loop',*(f'   vertex {p[0]:.9g} {p[1]:.9g} {p[2]:.9g}' for p in (a,b,c)),'  endloop',' endfacet']
        out.append('endsolid tinkle_assembly');return '\n'.join(out)+'\n'
    def _normal(self,a,b,c):
        u=[b[i]-a[i] for i in range(3)];w=[c[i]-a[i] for i in range(3)];n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];m=math.sqrt(sum(x*x for x in n)) or 1;return [x/m for x in n]
