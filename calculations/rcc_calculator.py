"""
Civil Estimate Suite Pro v4.0
RCC Detailed Calculator

Engineer workflow:
Dimensions -> Concrete -> Materials -> Reinforcement -> Formwork
-> Labour -> Cost -> BOQ
"""
from __future__ import annotations
from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class RCCCalculator(BaseCalculator):
    MIX_RATIOS = {
        "1:2:4": (1.0, 2.0, 4.0),
        "1:3:6": (1.0, 3.0, 6.0),
        "1:1.5:3": (1.0, 1.5, 3.0),
        "1:4:8": (1.0, 4.0, 8.0),
    }
    CFT_TO_M3 = 0.028316846592
    DRY_VOLUME_FACTOR = 1.54
    CEMENT_DENSITY_KG_M3 = 1440.0
    CEMENT_BAG_KG = 50.0

    def __init__(
        self,
        length: float,
        width: float,
        height: float,
        mix_ratio: str = "1:2:4",
        steel_kg: float = 0.0,
        binding_wire_percent: float = 2.0,
        formwork: float = 0.0,
        volume_unit: str = "m³",
    ):
        super().__init__()
        self.length=self.positive(length,"Length")
        self.width=self.positive(width,"Width")
        self.height=self.positive(height,"Thickness / Height")
        self.mix_ratio=str(mix_ratio).strip()
        if self.mix_ratio not in self.MIX_RATIOS:
            raise ValueError(f"Unsupported mix ratio: {self.mix_ratio}")
        self.steel_kg=self.non_negative(steel_kg,"Steel")
        self.binding_wire_percent=self.non_negative(
            binding_wire_percent,"Binding wire percentage"
        )
        self.formwork=self.non_negative(formwork,"Formwork")
        self.volume_unit=self.normalize_unit(volume_unit)
        if self.volume_unit not in {"m³","Cft"}:
            raise ValueError("Volume unit must be m³ or Cft.")

    @staticmethod
    def normalize_unit(unit:str)->str:
        v=str(unit or "m³").strip().lower()
        return {
            "m3":"m³","m^3":"m³","m³":"m³",
            "cft":"Cft","ft3":"Cft","ft³":"Cft",
            "cubic feet":"Cft","cubic foot":"Cft"
        }.get(v,str(unit).strip())

    def calculate(self)->CalculationResult:
        if self.volume_unit=="m³":
            lm,wm,hm=self.length,self.width,self.height
        else:
            lm,wm,hm=(self.length*.3048,self.width*.3048,self.height*.3048)

        wet_m3=lm*wm*hm
        dry_m3=wet_m3*self.DRY_VOLUME_FACTOR
        c,s,a=self.MIX_RATIOS[self.mix_ratio]
        parts=c+s+a
        cement_m3=dry_m3*c/parts
        sand_m3=dry_m3*s/parts
        agg_m3=dry_m3*a/parts
        cement_bags=(cement_m3*self.CEMENT_DENSITY_KG_M3)/self.CEMENT_BAG_KG
        factor=1.0 if self.volume_unit=="m³" else self.CFT_TO_M3

        r=self.result
        r.calculator="RCC"
        r.description=f"RCC ({self.mix_ratio})"
        r.unit=self.volume_unit
        r.quantity=wet_m3/factor
        r.wet_volume=wet_m3/factor
        r.dry_volume=dry_m3/factor
        r.cement_volume=cement_m3/factor
        r.cement_bags=cement_bags
        r.sand_volume=sand_m3/factor
        r.aggregate_volume=agg_m3/factor

        values={
            "length":self.length,"width":self.width,"height":self.height,
            "dimension_unit":"m" if self.volume_unit=="m³" else "ft",
            "volume_unit":self.volume_unit,"mix_ratio":self.mix_ratio,
            "metric_quantity_m3":wet_m3,"metric_dry_volume_m3":dry_m3,
            "cement_m3":cement_m3,"sand_m3":sand_m3,
            "aggregate_m3":agg_m3,"cement_bags":cement_bags,
            "steel_kg":self.steel_kg,
            "binding_wire_percent":self.binding_wire_percent,
            "binding_wire_kg":self.steel_kg*self.binding_wire_percent/100,
            "formwork":self.formwork,
        }
        for k,v in values.items(): r.add_value(k,v)
        return r


__all__=["RCCCalculator"]
