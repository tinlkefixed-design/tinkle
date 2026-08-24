from __future__ import annotations
import hashlib,re,math
from collections import Counter
from tinkle.knowledge.retrieval import BM25Index
from tinkle.knowledge.schemas import *

def _embed(text:str,dim:int=64)->list[float]:
    vec=[0.0]*dim
    for token in re.findall(r"[\w'-]+",text.casefold()):
        h=int(hashlib.sha256(token.encode()).hexdigest()[:8],16); vec[h%dim]+=1.0
    n=math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x/n for x in vec]

class KnowledgeEngine:
    """Evidence-first local knowledge layer. External search leads never become facts by themselves."""
    def __init__(self):
        self.documents={}; self.chunks={}; self.index=BM25Index(); self.vectors={}
    @staticmethod
    def _split(content,max_chars=1800,overlap=250):
        paragraphs=[p.strip() for p in re.split(r"\n\s*\n",content) if p.strip()]; parts=[]
        for paragraph in paragraphs:
            if len(paragraph)<=max_chars: parts.append(paragraph); continue
            start=0
            while start<len(paragraph):
                end=min(start+max_chars,len(paragraph)); parts.append(paragraph[start:end].strip())
                if end==len(paragraph): break
                start=max(end-overlap,start+1)
        return parts
    def ingest(self,doc):
        self.documents[str(doc.id)]=doc; chunks=[]
        for i,text in enumerate(self._split(doc.content)):
            chunk=KnowledgeChunk(document_id=doc.id,text=text,index=i,metadata=dict(doc.metadata)); self.chunks[str(chunk.id)]=chunk; self.index.upsert(str(chunk.id),text); self.vectors[str(chunk.id)]=_embed(text); chunks.append(chunk)
        return chunks
    def source_profile(self, source: str) -> SourceProfile:
        for doc in self.documents.values():
            if doc.source == source: return doc.source_profile
        return SourceProfile(rationale=['External or unclassified source; conservative default profile.'])
    def search(self,request):
        lexical=self.index.search(request.query,max(request.top_k*8,request.top_k)); qv=_embed(request.query); ranked=[]
        for hit in lexical:
            chunk=self.chunks[hit.item_id]; doc=self.documents[str(chunk.document_id)]
            if request.project_id and doc.metadata.get("project_id")!=request.project_id: continue
            semantic=sum(a*b for a,b in zip(qv,self.vectors[hit.item_id])); profile=doc.source_profile
            score=.35*min(hit.score/8.0,1.0)+.25*semantic+.40*self._mode_score(chunk.text,request.mode)*profile.relevance
            ranked.append((score,chunk,doc))
        ranked.sort(key=lambda x:x[0],reverse=True)
        evidence=[Evidence(chunk_id=c.id,document_id=d.id,source=d.source,text=c.text,score=round(min(s,1),4),source_profile=d.source_profile,metadata=c.metadata) for s,c,d in ranked[:request.top_k]]
        claims=self._claims(evidence); conflicts=self._conflicts(evidence,request.mode)
        conf=round(self._confidence(evidence,claims,conflicts),4)
        status='CONFLICTED' if conflicts else ('SUPPORTED' if evidence else 'UNKNOWN')
        gaps=[] if evidence else [f'No indexed evidence matched: {request.query}']
        return KnowledgeAnswer(query=request.query,mode=request.mode,evidence=evidence,claims=claims,conflicts=conflicts,confidence=conf,status=status,gaps=gaps,limitations=['Local index retrieval is not exhaustive.','Source quality is ranked heuristically unless explicit metadata is provided.'])
    @staticmethod
    def _mode_score(text, mode):
        t=text.casefold()
        terms={SearchMode.contradiction:['however','contradict','conflict','inconsistent','disagree'],SearchMode.failure:['failed','failure','unsuccessful','did not work','limitation'],SearchMode.prior_art:['patent','prior art','existing design','prototype'],SearchMode.negative:['negative result','null result','did not work','failed'],SearchMode.deep:[],SearchMode.broad:[]}[mode]
        return 1.0 if not terms else (1.0 if any(x in t for x in terms) else .25)
    @staticmethod
    def _claims(evidence):
        out=[]
        for e in evidence:
            out.append(ScientificClaim(claim=e.text[:1000],evidence_refs=[e.id],confidence=e.score,status='SUPPORTED'))
        return out
    @staticmethod
    def _conflicts(evidence, mode):
        if mode not in {SearchMode.contradiction,SearchMode.deep}: return []
        positives=[e for e in evidence if any(x in e.text.casefold() for x in ['supports','increases','improves','positive'])]
        negatives=[e for e in evidence if any(x in e.text.casefold() for x in ['fails','decreases','no effect','negative','contradict'])]
        if positives and negatives:
            return [KnowledgeConflict(claim_a=positives[0].text[:500],claim_b=negatives[0].text[:500],evidence_a=[positives[0].id],evidence_b=[negatives[0].id])]
        return []
    @staticmethod
    def _confidence(evidence,claims,conflicts):
        if not evidence:return 0.0
        scores=[]
        for e in evidence:
            p=e.source_profile; quality=(p.authority+p.reproducibility+p.independence+p.evidence_quality+p.recency)/5
            scores.append(.6*e.score+.4*quality)
        value=max(scores)
        if conflicts:value*=.5
        return min(1,max(0,value))
