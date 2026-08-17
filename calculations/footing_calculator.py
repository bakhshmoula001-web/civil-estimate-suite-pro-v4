"""
Civil Estimate Suite Pro v4.0
Footing / Foundation Detailed Estimator
"""
from __future__ import annotations
from calculations.base_calculator import BaseCalculator


class FootingCalculator(BaseCalculator):
    DRY_FACTOR = 1.54
    CEMENT_BAG_VOLUME_M3 = 0.0347
    DENSITY = 7850.0

    def __init__(
        self,
        footing_length,
        footing_width,
        footing_thickness,
        footing_count=1,
        length_unit="m",
        mix_ratio="1:2:4",
        steel_dia_mm=12,
        steel_spacing_mm=150,
        distribution_dia_mm=10,
        distribution_spacing_mm=200,
        cover_mm=50,
        steel_cutting_percent=2,
        binding_wire_percent=2,
        concrete_skilled_productivity=1.0,
        concrete_skilled_rate=2500,
        concrete_unskilled_productivity=2.0,
        concrete_unskilled_rate=1250,
        cement_rate=1650,
        sand_rate=800,
        aggregate_rate=1000,
        steel_rate=280,
        include_pcc=False,
        pcc_thickness=0.075,
        pcc_mix_ratio="1:4:8",
        pcc_cement_rate=1650,
        pcc_sand_rate=800,
        pcc_aggregate_rate=1000,
    ):
        super().__init__()
        self.unit=self._unit(length_unit)
        if self.unit not in {"m","ft"}:
            raise ValueError("Length unit must be m or ft.")

        self.L=self.positive(footing_length,"Footing length")
        self.W=self.positive(footing_width,"Footing width")
        self.T=self.positive(footing_thickness,"Footing thickness")
        self.count=self.non_negative_int(footing_count,"Footing count")
        if self.count < 1: raise ValueError("Footing count must be at least 1.")

        self.mix=self._ratio(mix_ratio,"Concrete mix ratio")
        self.cover=self.non_negative(cover_mm,"Clear cover")
        self.steel_dia=self.positive(steel_dia_mm,"Main steel diameter")
        self.steel_spacing=self.positive(steel_spacing_mm,"Main steel spacing")
        self.dist_dia=self.positive(distribution_dia_mm,"Distribution steel diameter")
        self.dist_spacing=self.positive(distribution_spacing_mm,"Distribution steel spacing")
        self.cutting=self.non_negative(steel_cutting_percent,"Steel cutting allowance")
        self.binding=self.non_negative(binding_wire_percent,"Binding wire")

        self.sp=self.positive(concrete_skilled_productivity,"Skilled productivity")
        self.sr=self.non_negative(concrete_skilled_rate,"Skilled labour rate")
        self.up=self.positive(concrete_unskilled_productivity,"Unskilled productivity")
        self.ur=self.non_negative(concrete_unskilled_rate,"Unskilled labour rate")

        self.cement_rate=self.non_negative(cement_rate,"Cement rate")
        self.sand_rate=self.non_negative(sand_rate,"Sand rate")
        self.agg_rate=self.non_negative(aggregate_rate,"Aggregate rate")
        self.steel_rate=self.non_negative(steel_rate,"Steel rate")

        self.include_pcc=bool(include_pcc)
        self.pcc_t=self.non_negative(pcc_thickness,"PCC thickness")
        self.pcc_mix=self._ratio(pcc_mix_ratio,"PCC mix ratio")
        self.pcc_cement_rate=self.non_negative(pcc_cement_rate,"PCC cement rate")
        self.pcc_sand_rate=self.non_negative(pcc_sand_rate,"PCC sand rate")
        self.pcc_agg_rate=self.non_negative(pcc_aggregate_rate,"PCC aggregate rate")

    @staticmethod
    def _unit(unit):
        v=str(unit or "m").strip().lower()
        return {"m":"m","meter":"m","metre":"m","ft":"ft","feet":"ft"}.get(v,str(unit).strip())

    @staticmethod
    def _ratio(value,label):
        try:
            parts=[float(x.strip()) for x in str(value).split(":")]
        except Exception as exc:
            raise ValueError(f"{label} must be like 1:2:4.") from exc
        if len(parts)!=3 or any(x<=0 for x in parts):
            raise ValueError(f"{label} must contain three positive values.")
        return tuple(parts)

    @staticmethod
    def non_negative_int(value,label):
        try:n=int(float(value))
        except (TypeError,ValueError) as exc:raise ValueError(f"{label} must be a whole number.") from exc
        if n<0:raise ValueError(f"{label} cannot be negative.")
        return n

    @staticmethod
    def _kg_per_m(dia):
        d=dia/1000
        return 3.141592653589793*d*d/4*7850

    def _m(self,v):
        return v if self.unit=="m" else v*0.3048

    def _concrete_materials(self,wet,ratio):
        dry=wet*self.DRY_FACTOR
        total=sum(ratio)
        cement_bags=(dry*ratio[0]/total)/self.CEMENT_BAG_VOLUME_M3
        sand_m3=dry*ratio[1]/total
        agg_m3=dry*ratio[2]/total
        return dry,cement_bags,sand_m3,agg_m3

    def calculate(self):
        L=self._m(self.L); W=self._m(self.W); T=self._m(self.T)
        total_concrete=L*W*T*self.count
        dry,cement_bags,sand_m3,agg_m3=self._concrete_materials(total_concrete,self.mix)

        cover=self.cover/1000
        clear_L=max(0,L-2*cover); clear_W=max(0,W-2*cover)

        main_count=max(1,int(clear_W*1000/self.steel_spacing)+1)
        main_len=clear_L
        main_total=main_count*main_len*self.count
        main_kg=main_total*self._kg_per_m(self.steel_dia)

        dist_count=max(1,int(clear_L*1000/self.dist_spacing)+1)
        dist_len=clear_W
        dist_total=dist_count*dist_len*self.count
        dist_kg=dist_total*self._kg_per_m(self.dist_dia)

        base_steel=main_kg+dist_kg
        cutting_kg=base_steel*self.cutting/100
        total_steel=base_steel+cutting_kg
        binding_kg=total_steel*self.binding/100

        skilled_days=total_concrete/self.sp
        unskilled_days=total_concrete/self.up
        skilled_cost=skilled_days*self.sr
        unskilled_cost=unskilled_days*self.ur

        material_cost=(
            cement_bags*self.cement_rate+
            sand_m3*self.sand_rate+
            agg_m3*self.agg_rate+
            total_steel*self.steel_rate
        )
        labour_cost=skilled_cost+unskilled_cost

        pcc={}
        if self.include_pcc and self.pcc_t>0:
            pcc_wet=L*W*self.pcc_t*self.count
            pcc_dry,pcc_cement,pcc_sand,pcc_agg=self._concrete_materials(pcc_wet,self.pcc_mix)
            pcc={
                "wet_volume_m3":pcc_wet,"dry_volume_m3":pcc_dry,
                "cement_bags":pcc_cement,"sand_m3":pcc_sand,"aggregate_m3":pcc_agg,
                "cement_amount":pcc_cement*self.pcc_cement_rate,
                "sand_amount":pcc_sand*self.pcc_sand_rate,
                "aggregate_amount":pcc_agg*self.pcc_agg_rate,
                "material_cost":(
                    pcc_cement*self.pcc_cement_rate+
                    pcc_sand*self.pcc_sand_rate+
                    pcc_agg*self.pcc_agg_rate
                )
            }
            material_cost += pcc["material_cost"]

        total_cost=material_cost+labour_cost

        r=self.result
        r.calculator="Footing"
        r.description="Footing / Foundation Detailed Estimate"
        r.unit="m³"
        r.quantity=total_concrete
        vals={
            "footing_length":self.L,"footing_width":self.W,"footing_thickness":self.T,
            "footing_count":self.count,"length_unit":self.unit,
            "mix_ratio":":".join(str(int(x)) if x.is_integer() else str(x) for x in self.mix),
            "wet_volume_m3":total_concrete,"dry_volume_m3":dry,
            "cement_bags":cement_bags,"sand_m3":sand_m3,"aggregate_m3":agg_m3,
            "cement_rate":self.cement_rate,"sand_rate":self.sand_rate,"aggregate_rate":self.agg_rate,
            "steel_dia_mm":self.steel_dia,"steel_spacing_mm":self.steel_spacing,
            "main_bar_count":main_count,"main_bar_length_m":main_len,"main_total_length_m":main_total,"main_steel_kg":main_kg,
            "distribution_dia_mm":self.dist_dia,"distribution_spacing_mm":self.dist_spacing,
            "distribution_bar_count":dist_count,"distribution_bar_length_m":dist_len,"distribution_total_length_m":dist_total,"distribution_steel_kg":dist_kg,
            "base_steel_kg":base_steel,"cutting_allowance_percent":self.cutting,"cutting_kg":cutting_kg,
            "steel_kg":total_steel,"binding_wire_percent":self.binding,"binding_wire_kg":binding_kg,
            "steel_rate":self.steel_rate,
            "skilled_productivity":self.sp,"skilled_days":skilled_days,"skilled_rate":self.sr,"skilled_cost":skilled_cost,
            "unskilled_productivity":self.up,"unskilled_days":unskilled_days,"unskilled_rate":self.ur,"unskilled_cost":unskilled_cost,
            "material_cost":material_cost,"labour_cost":labour_cost,"total_cost":total_cost,
            "include_pcc":self.include_pcc,"pcc":pcc,
        }
        for k,v in vals.items():r.add_value(k,v)
        return r

__all__=["FootingCalculator"]
