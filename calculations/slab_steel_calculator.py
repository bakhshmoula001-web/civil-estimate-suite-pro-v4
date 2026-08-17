"""
Civil Estimate Suite Pro v4.0
Slab Steel / Rebar Schedule Calculator
"""
from __future__ import annotations
from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class SlabSteelCalculator(BaseCalculator):
    STEEL_DENSITY_KG_M3 = 7850.0

    def __init__(
        self,
        slab_length: float,
        slab_width: float,
        cover_mm: float,
        main_dia_mm: float,
        main_spacing_mm: float,
        distribution_dia_mm: float,
        distribution_spacing_mm: float,
        main_extra_length_m: float = 0.0,
        distribution_extra_length_m: float = 0.0,
        top_steel: bool = False,
        top_main_dia_mm: float = 0.0,
        top_main_spacing_mm: float = 0.0,
        top_distribution_dia_mm: float = 0.0,
        top_distribution_spacing_mm: float = 0.0,
        cutting_allowance_percent: float = 2.0,
        binding_wire_percent: float = 2.0,
        steel_rate: float = 0.0,
        length_unit: str = "m",
    ):
        super().__init__()
        self.unit=self._unit(length_unit)
        if self.unit not in {"m","ft"}: raise ValueError("Length unit must be m or ft.")
        self.slab_length=self.positive(slab_length,"Slab length")
        self.slab_width=self.positive(slab_width,"Slab width")
        self.cover_mm=self.non_negative(cover_mm,"Cover")
        self.main_dia_mm=self.positive(main_dia_mm,"Main bar diameter")
        self.main_spacing_mm=self.positive(main_spacing_mm,"Main spacing")
        self.dist_dia_mm=self.positive(distribution_dia_mm,"Distribution bar diameter")
        self.dist_spacing_mm=self.positive(distribution_spacing_mm,"Distribution spacing")
        self.main_extra=self.non_negative(main_extra_length_m,"Main extra length")
        self.dist_extra=self.non_negative(distribution_extra_length_m,"Distribution extra length")
        self.top_steel=bool(top_steel)
        self.top_main_dia=self.non_negative(top_main_dia_mm,"Top main diameter")
        self.top_main_spacing=self.non_negative(top_main_spacing_mm,"Top main spacing")
        self.top_dist_dia=self.non_negative(top_distribution_dia_mm,"Top distribution diameter")
        self.top_dist_spacing=self.non_negative(top_distribution_spacing_mm,"Top distribution spacing")
        self.cutting=self.non_negative(cutting_allowance_percent,"Cutting allowance")
        self.binding=self.non_negative(binding_wire_percent,"Binding wire")
        self.steel_rate=self.non_negative(steel_rate,"Steel rate")
        if self.top_steel and (self.top_main_dia<=0 or self.top_main_spacing<=0 or self.top_dist_dia<=0 or self.top_dist_spacing<=0):
            raise ValueError("Enter top main/distribution diameter and spacing.")

    @staticmethod
    def _unit(unit):
        v=str(unit or "m").strip().lower()
        return {"m":"m","meter":"m","metre":"m","ft":"ft","feet":"ft"}.get(v,str(unit).strip())

    def _m(self,v): return v if self.unit=="m" else v*.3048
    @staticmethod
    def _count(clear_length_m, spacing_mm):
        return max(1,int((clear_length_m*1000)/spacing_mm)+1)
    @staticmethod
    def _kg_per_m(d):
        dm=d/1000
        return 3.141592653589793*dm*dm/4*7850

    def _set(self,name,orientation,dia,spacing,bar_length_m,count,extra):
        total_length=(bar_length_m+extra)*count
        kg=total_length*self._kg_per_m(dia)
        return {
            "name":name,"orientation":orientation,"diameter_mm":dia,
            "spacing_mm":spacing,"bar_count":count,
            "bar_length_m":bar_length_m+extra,
            "base_bar_length_m":bar_length_m,
            "extra_length_m":extra,
            "total_length_m":total_length,
            "unit_weight_kg_m":self._kg_per_m(dia),
            "weight_kg":kg,
        }

    def calculate(self)->CalculationResult:
        L=self._m(self.slab_length); W=self._m(self.slab_width)
        cover=self.cover_mm/1000
        clear_L=max(0,L-2*cover); clear_W=max(0,W-2*cover)

        # Main bars run along slab length; their number is based on width.
        main=self._set("Bottom Main","Length",self.main_dia_mm,self.main_spacing_mm,
                       clear_L,self._count(clear_W,self.main_spacing_mm),self.main_extra)
        # Distribution bars run across slab width; their number is based on length.
        dist=self._set("Bottom Distribution","Width",self.dist_dia_mm,self.dist_spacing_mm,
                       clear_W,self._count(clear_L,self.dist_spacing_mm),self.dist_extra)

        sets=[main,dist]
        if self.top_steel:
            top_main=self._set("Top Main","Length",self.top_main_dia,self.top_main_spacing,
                               clear_L,self._count(clear_W,self.top_main_spacing),self.main_extra)
            top_dist=self._set("Top Distribution","Width",self.top_dist_dia,self.top_dist_spacing,
                               clear_W,self._count(clear_L,self.top_dist_spacing),self.dist_extra)
            sets += [top_main,top_dist]

        base_kg=sum(x["weight_kg"] for x in sets)
        cutting_kg=base_kg*self.cutting/100
        total_kg=base_kg+cutting_kg
        binding_kg=total_kg*self.binding/100
        amount=total_kg*self.steel_rate

        r=self.result
        r.calculator="Slab Steel"
        r.description="Slab Reinforcement Steel"
        r.unit="kg"
        r.quantity=total_kg
        for k,v in {
            "slab_length":self.slab_length,"slab_width":self.slab_width,
            "length_unit":self.unit,"cover_mm":self.cover_mm,
            "clear_length_m":clear_L,"clear_width_m":clear_W,
            "cutting_allowance_percent":self.cutting,
            "binding_wire_percent":self.binding,
            "base_steel_kg":base_kg,"cutting_kg":cutting_kg,
            "steel_kg":total_kg,"binding_wire_kg":binding_kg,
            "steel_rate":self.steel_rate,"steel_amount":amount,
            "top_steel":self.top_steel,
        }.items(): r.add_value(k,v)
        r.add_value("bar_sets",sets)
        return r

__all__=["SlabSteelCalculator"]
