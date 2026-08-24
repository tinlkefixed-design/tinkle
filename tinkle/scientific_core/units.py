from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class UnitDef:
    factor: float
    dimension: tuple[int,int,int,int,int,int,int]
    name: str

# SI base order: length, mass, time, current, temperature, amount, luminous intensity.
UNITS = {
    'm': UnitDef(1,(1,0,0,0,0,0,0),'length'), 'km': UnitDef(1000,(1,0,0,0,0,0,0),'length'),
    'cm': UnitDef(.01,(1,0,0,0,0,0,0),'length'), 'mm': UnitDef(.001,(1,0,0,0,0,0,0),'length'),
    'kg': UnitDef(1,(0,1,0,0,0,0,0),'mass'), 'g': UnitDef(.001,(0,1,0,0,0,0,0),'mass'),
    's': UnitDef(1,(0,0,1,0,0,0,0),'time'), 'min': UnitDef(60,(0,0,1,0,0,0,0),'time'), 'h': UnitDef(3600,(0,0,1,0,0,0,0),'time'),
    'A': UnitDef(1,(0,0,0,1,0,0,0),'current'), 'K': UnitDef(1,(0,0,0,0,1,0,0),'temperature'),
    'mol': UnitDef(1,(0,0,0,0,0,1,0),'amount'), 'N': UnitDef(1,(1,1,-2,0,0,0,0),'force'),
    'Pa': UnitDef(1,(-1,1,-2,0,0,0,0),'pressure'), 'J': UnitDef(1,(2,1,-2,0,0,0,0),'energy'),
    'W': UnitDef(1,(2,1,-3,0,0,0,0),'power'), 'C': UnitDef(1,(0,0,1,1,0,0,0),'charge'),
    'V': UnitDef(1,(2,1,-3,-1,0,0,0),'voltage'), 'Hz': UnitDef(1,(0,0,-1,0,0,0,0),'frequency'),
    'rad': UnitDef(1,(0,0,0,0,0,0,0),'dimensionless'), '1': UnitDef(1,(0,0,0,0,0,0,0),'dimensionless'),
}

class UnitDimensionEngine:
    def parse(self, unit: str) -> UnitDef:
        unit = unit.strip()
        if unit not in UNITS: raise ValueError(f'Unsupported unit: {unit}')
        return UNITS[unit]
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        a,b=self.parse(from_unit),self.parse(to_unit)
        if a.dimension != b.dimension: raise ValueError(f'Incompatible dimensions: {from_unit} -> {to_unit}')
        return value*a.factor/b.factor
    def dimension(self, unit: str) -> tuple[int,...]: return self.parse(unit).dimension
    def compatible(self, left: str, right: str) -> bool: return self.dimension(left)==self.dimension(right)
    def check_equation(self, terms: list[str]) -> bool:
        dims=[self.dimension(t) for t in terms]
        return bool(dims) and all(d==dims[0] for d in dims[1:])
    @staticmethod
    def finite(value: float) -> bool: return math.isfinite(float(value))
