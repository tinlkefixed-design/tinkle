from __future__ import annotations
import html,re
from html.parser import HTMLParser
from urllib.parse import quote
from urllib.request import Request,urlopen
from tinkle.research_engine.schemas import ResearchSource
from tinkle.knowledge.schemas import SourceProfile
class _ResultParser(HTMLParser):
    def __init__(self): super().__init__(); self.in_link=False; self.href=''; self.text=[]; self.results=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            href=dict(attrs).get('href','')
            if href.startswith('http'): self.in_link=True; self.href=href; self.text=[]
    def handle_data(self,data):
        if self.in_link:self.text.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.in_link:
            title=' '.join(''.join(self.text).split())
            if title:self.results.append((title,html.unescape(self.href)))
            self.in_link=False
class DuckDuckGoSearchProvider:
    """External discovery adapter. Search hits are leads; fetched text is still unverified evidence."""
    def __init__(self,timeout=8.0,user_agent='TinkleResearch/2.0'): self.timeout=timeout; self.user_agent=user_agent
    def __call__(self,question,top_k):
        url='https://html.duckduckgo.com/html/?q='+quote(question)
        req=Request(url,headers={'User-Agent':self.user_agent})
        with urlopen(req,timeout=self.timeout) as response: body=response.read().decode('utf-8','replace')
        parser=_ResultParser(); parser.feed(body); seen=set(); out=[]
        for title,href in parser.results:
            clean=re.sub(r'[&?]uddg=.*','',href)
            if clean in seen: continue
            seen.add(clean)
            profile=self._profile(clean)
            out.append(ResearchSource(source=clean,title=title,metadata={'provider':'duckduckgo','external':True},profile=profile))
            if len(out)>=top_k: break
        return out
    def fetch(self,source: ResearchSource, max_chars=12000) -> str:
        req=Request(source.source,headers={'User-Agent':self.user_agent})
        with urlopen(req,timeout=self.timeout) as response: raw=response.read(max_chars*2).decode('utf-8','replace')
        text=re.sub(r'<script.*?</script>|<style.*?</style>',' ',raw,flags=re.I|re.S)
        text=re.sub(r'<[^>]+>',' ',text); return ' '.join(html.unescape(text).split())[:max_chars]
    @staticmethod
    def _profile(url):
        host=url.casefold()
        if any(x in host for x in ['doi.org','nature.com','science.org','pubmed','arxiv.org','ncbi.nlm.nih.gov']): return SourceProfile(authority=.9,reproducibility=.8,evidence_quality=.85,relevance=.7,independence=.8,rationale=['Recognized scholarly/persistent domain heuristic.'])
        if any(x in host for x in ['patents.google','patentscope','epo.org','uspto.gov']): return SourceProfile(authority=.85,reproducibility=.5,evidence_quality=.75,relevance=.7,independence=.7,rationale=['Patent/public-office domain heuristic.'])
        return SourceProfile(relevance=.5,rationale=['Unclassified web source; conservative default.'])
