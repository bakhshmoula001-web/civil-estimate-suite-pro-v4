"""
Civil Estimate Suite Pro v4.0
Beam Steel / Reinforcement Calculator
"""
from __future__ import annotations
from calculations.base_calculator import BaseCalculator


class BeamSteelCalculator(BaseCalculator):
    STEEL_DENSITY_KG_M3 = 7850.0

    def __init__(
        self,
        beam_length,
        beam_width,
        beam_depth,
        cover_mm,
        bottom_dia_mm,
        bottom_bars,
        top_dia_mm,
        top_bars,
        lap_length_m=0.0,
        laps=0,
        anchorage_extra_m=0.0,
        stirrup_dia_mm=8.0,
        stirrup_spacing_mm=150.0,
        stirrup_hook_extra_mm=200.0,
        cutting_allowance_percent=2.0,
        binding_wire_percent=2.0,
        steel_rate=0.0,
        beam_count=1,
        length_unit="m",
    ):
        super().__init__()
        self.unit=self._unit(length_unit)
        if self.unit not in {"m","ft"}:
            raise ValueError("Length unit must be m or ft.")

        self.L=self.positive(beam_length,"Beam length")
        self.W=self.positive(beam_width,"Beam width")
        self.D=self.positive(beam_depth,"Beam depth")
        self.cover=self.non_negative(cover_mm,"Clear cover")

        self.bottom_dia=self.positive(bottom_dia_mm,"Bottom bar diameter")
        self.bottom_bars=self.non_negative_int(bottom_bars,"Bottom bars")
        if self.bottom_bars < 1:
            raise ValueError("Bottom bars must be at least 1.")

        self.top_dia=self.positive(top_dia_mm,"Top bar diameter")
        self.top_bars=self.non_negative_int(top_bars,"Top bars")
        if self.top_bars < 1:
            raise ValueError("Top bars must be at least 1.")

        self.lap=self.non_negative(lap_length_m,"Lap length")
        self.laps=self.non_negative_int(laps,"Laps")
        self.anchorage=self.non_negative(anchorage_extra_m,"Anchorage / extra length")

        self.stirrup_dia=self.positive(stirrup_dia_mm,"Stirrup diameter")
        self.spacing=self.positive(stirrup_spacing_mm,"Stirrup spacing")
        self.hook=self.non_negative(stirrup_hook_extra_mm,"Stirrup hook allowance")

        self.cutting=self.non_negative(cutting_allowance_percent,"Cutting allowance")
        self.binding=self.non_negative(binding_wire_percent,"Binding wire")
        self.rate=self.non_negative(steel_rate,"Steel rate")
        self.count=self.non_negative_int(beam_count,"Beam count")
        if self.count < 1:
            raise ValueError("Beam count must be at least 1.")

    @staticmethod
    def _unit(unit):
        v=str(unit or "m").strip().lower()
        return {"m":"m","meter":"m","metre":"m","ft":"ft","feet":"ft"}.get(v,str(unit).strip())

    @staticmethod
    def non_negative_int(value,label):
        try:n=int(float(value))
        except (TypeError,ValueError) as exc:
            raise ValueError(f"{label} must be a whole number.") from exc
        if n < 0: raise ValueError(f"{label} cannot be negative.")
        return n

    def _m(self,v):
        return v if self.unit=="m" else v*0.3048

    @staticmethod
    def _kg_per_m(dia):
        d=dia/1000.0
        return 3.141592653589793*d*d/4.0*7850.0

    def calculate(self):
        L=self._m(self.L)
        W=self._m(self.W)
        D=self._m(self.D)
        cover=self.cover/1000.0
        stirrup_r=(self.stirrup_dia/1000.0)/2.0

        main_length_each=L + self.lap*self.laps + self.anchorage
        bottom_length=main_length_each*self.bottom_bars*self.count
        top_length=main_length_each*self.top_bars*self.count
        bottom_kg=bottom_length*self._kg_per_m(self.bottom_dia)
        top_kg=top_length*self._kg_per_m(self.top_dia)

        # Stirrup centerline dimensions, allowing for clear cover and stirrup radius.
        center_W=max(0.0,W-2*(cover+stirrup_r))
        center_D=max(0.0,D-2*(cover+stirrup_r))
        stirrup_cut=2*center_W+2*center_D+(self.hook/1000.0)
        stirrup_count_one=max(1,int((L*1000.0)/self.spacing)+1)
        stirrup_count=stirrup_count_one*self.count
        stirrup_length=stirrup_cut*stirrup_count
        stirrup_kg=stirrup_length*self._kg_per_m(self.stirrup_dia)

        base=bottom_kg+top_kg+stirrup_kg
        cutting=base*self.cutting/100.0
        total=base+cutting
        binding=total*self.binding/100.0
        amount=total*self.rate

        r=self.result
        r.calculator="Beam Steel"
        r.description="Beam Reinforcement Steel"
        r.unit="kg"
        r.quantity=total
        values={
            "beam_length":self.L,"beam_width":self.W,"beam_depth":self.D,
            "beam_count":self.count,"length_unit":self.unit,"cover_mm":self.cover,
            "bottom_dia_mm":self.bottom_dia,"bottom_bars":self.bottom_bars,
            "bottom_length_each_m":main_length_each,"bottom_total_length_m":bottom_length,
            "bottom_kg":bottom_kg,
            "top_dia_mm":self.top_dia,"top_bars":self.top_bars,
            "top_length_each_m":main_length_each,"top_total_length_m":top_length,
            "top_kg":top_kg,
            "lap_length_m":self.lap,"laps":self.laps,
            "anchorage_extra_m":self.anchorage,
            "stirrup_dia_mm":self.stirrup_dia,"stirrup_spacing_mm":self.spacing,
            "stirrup_count_one":stirrup_count_one,"stirrup_total_count":stirrup_count,
            "stirrup_cutting_length_m":stirrup_cut,"stirrup_total_length_m":stirrup_length,
            "stirrup_kg":stirrup_kg,"base_steel_kg":base,
            "cutting_allowance_percent":self.cutting,"cutting_kg":cutting,
            "steel_kg":total,"binding_wire_percent":self.binding,
            "binding_wire_kg":binding,"steel_rate":self.rate,"steel_amount":amount,
        }
        for k,v in values.items(): r.add_value(k,v)
        return r

__all__=["BeamSteelCalculator"]
