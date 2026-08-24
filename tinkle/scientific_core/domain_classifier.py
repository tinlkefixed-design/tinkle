from __future__ import annotations
import re
from collections import defaultdict

DOMAINS = {
    'Physics': {'force','mass','velocity','acceleration','gravity','quantum','particle','field','energy','momentum'},
    'Chemistry': {'molecule','reaction','chemical','catalyst','ph','molar','compound','solvent','atom'},
    'Biology': {'cell','gene','protein','organism','enzyme','microbe','biological','tissue','evolution'},
    'Materials Science': {'material','alloy','polymer','ceramic','composite','stress','strain','crystal','microstructure'},
    'Energy': {'battery','solar','energy','power','storage','fuel','efficiency','generator','electrolysis'},
    'Electronics': {'voltage','current','circuit','transistor','sensor','capacitor','resistor','semiconductor'},
    'Mechanical Engineering': {'mechanism','gear','bearing','shaft','machine','mechanical','torque','robot'},
    'Electrical Engineering': {'motor','generator','transformer','electromagnetic','circuit','voltage','current'},
    'Computer Science': {'algorithm','software','compute','program','code','machine learning','neural','data structure'},
    'Mathematics': {'equation','theorem','proof','function','matrix','optimization','probability','differential'},
    'Control': {'controller','feedback','stability','control','pid','state space','trajectory'},
    'Fluid Dynamics': {'fluid','flow','viscosity','turbulence','pressure','drag','hydrodynamic'},
    'Thermodynamics': {'entropy','heat','temperature','thermodynamic','enthalpy','cycle','thermal'},
    'Quantum': {'quantum','qubit','wavefunction','superposition','entanglement','hamiltonian'},
    'Astronomy': {'star','planet','galaxy','orbit','cosmology','astronomy','exoplanet'},
}

class DomainClassifier:
    def classify(self, text: str, *, min_score: float = 0.05) -> list[str]:
        tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", text.casefold()))
        lower = text.casefold()
        scores: dict[str, float] = defaultdict(float)
        for domain, terms in DOMAINS.items():
            for term in terms:
                if ' ' in term:
                    if term in lower: scores[domain] += 2.0
                elif term in tokens:
                    scores[domain] += 1.0
        if not scores: return ['Multidisciplinary']
        max_score = max(scores.values())
        selected = [d for d,s in scores.items() if s >= max(min_score*max_score, 1.0) and s >= max_score*0.35]
        return sorted(selected, key=lambda d: (-scores[d], d)) or [max(scores, key=scores.get)]
