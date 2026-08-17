from __future__ import annotations
import math
from calculations.base_calculator import BaseCalculator

class StaircaseCalculator(BaseCalculator):
    DRY_FACTOR=1.54
    BAG_VOL=0.0347
    def __init__(self,floor_height,stair_width,riser_height,tread_width,waist_thickness,
                 landing_length=1.2,landing_thickness=.15,flights=1,length_unit="m",
                 mix_ratio="1:2:4",main_dia_mm=12,main_spacing_mm=150,
                 distribution_dia_mm=10,distribution_spacing_mm=200,cover_mm=25,
                 cutting_percent=2,binding_percent=2,cement_rate=1650,sand_rate=800,
                 aggregate_rate=1000,steel_rate=280,skilled_productivity=1,
                 skilled_rate=2500,unskilled_productivity=2,unskilled_rate=1250):
        super().__init__(); self.unit=self._unit(length_unit)
        if self.unit not in ("m","ft"): raise ValueError("Length unit must be m or ft.")
        self.floor=self.positive(floor_height,"Floor height"); self.width=self.positive(stair_width,"Stair width")
        self.riser=self.positive(riser_height,"Riser height"); self.tread=self.positive(tread_width,"Tread width")
        self.waist=self.positive(waist_thickness,"Waist thickness"); self.landing=self.positive(landing_length,"Landing length")
        self.landing_t=self.positive(landing_thickness,"Landing thickness"); self.flights=int(flights)
        if self.flights<1: raise ValueError("Flights must be at least 1.")
        self.mix=self._ratio(mix_ratio); self.md=self.positive(main_dia_mm,"Main diameter"); self.ms=self.positive(main_spacing_mm,"Main spacing")
        self.dd=self.positive(distribution_dia_mm,"Distribution diameter"); self.ds=self.positive(distribution_spacing_mm,"Distribution spacing")
        self.cover=self.non_negative(cover_mm,"Cover"); self.cut=self.non_negative(cutting_percent,"Cutting allowance")
        self.bind=self.non_negative(binding_percent,"Binding wire")
        for n,v in [("Cement rate",cement_rate),("Sand rate",sand_rate),("Aggregate rate",aggregate_rate),("Steel rate",steel_rate),("Skilled rate",skilled_rate),("Unskilled rate",unskilled_rate)]: self.non_negative(v,n)
        self.cr=float(cement_rate); self.sr=float(sand_rate); self.ar=float(aggregate_rate); self.str=float(steel_rate)
        self.skp=self.positive(skilled_productivity,"Skilled productivity"); self.skr=float(skilled_rate)
        self.up=self.positive(unskilled_productivity,"Unskilled productivity"); self.ur=float(unskilled_rate)
    @staticmethod
    def _unit(v):
        v=str(v or "m").lower().strip()
        return {"meter":"m","metre":"m","feet":"ft"}.get(v,v)
    @staticmethod
    def _ratio(v):
        try:p=[float(x) for x in str(v).split(":")]
        except Exception as e: raise ValueError("Mix ratio must be like 1:2:4.") from e
        if len(p)!=3 or min(p)<=0: raise ValueError("Mix ratio must contain three positive values.")
        return p
    @staticmethod
    def _kg(d):
        x=d/1000; return math.pi*x*x/4*7850
    def _m(self,v): return float(v) if self.unit=="m" else float(v)*.3048
    def calculate(self):
        H=self._m(self.floor); W=self._m(self.width); R=self._m(self.riser); T=self._m(self.tread)
        nr=max(1,round(H/R)); actual=H/nr; nt=max(1,nr-1); run=nt*T; slope=math.hypot(H,run)
        wet=(slope*W*self._m(self.waist)+W*self._m(self.landing)*self._m(self.landing_t))*self.flights
        dry=wet*self.DRY_FACTOR; total=sum(self.mix)
        cement=dry*self.mix[0]/total/self.BAG_VOL; sand=dry*self.mix[1]/total; agg=dry*self.mix[2]/total
        c=self.cover/1000; mc=max(1,int(W*1000/self.ms)+1); ml=max(0,slope-2*c)+self._m(self.landing)
        mt=mc*ml*self.flights; mw=mt*self._kg(self.md)
        dc=max(1,int(max(0,slope-2*c)*1000/self.ds)+1); dl=max(0,W-2*c); dt=dc*dl*self.flights; dw=dt*self._kg(self.dd)
        base=mw+dw; cut=base*self.cut/100; steel=base+cut; binding=steel*self.bind/100
        sk=wet/self.skp; un=wet/self.up; labour=sk*self.skr+un*self.ur
        material=cement*self.cr+sand*self.sr+agg*self.ar+steel*self.str; total_cost=material+labour
        r=self.result; r.calculator="Staircase"; r.description="Staircase Detailed Estimate"; r.unit="m³"; r.quantity=wet
        vals={"floor_height":self.floor,"stair_width":self.width,"riser_height":self.riser,"actual_riser_m":actual,"tread_width":self.tread,
        "risers":nr,"treads":nt,"horizontal_run_m":run,"slope_length_m":slope,"waist_thickness":self.waist,"landing_length":self.landing,
        "landing_thickness":self.landing_t,"flights":self.flights,"length_unit":self.unit,"mix_ratio":":".join(str(int(x)) if x.is_integer() else str(x) for x in self.mix),
        "wet_volume_m3":wet,"dry_volume_m3":dry,"cement_bags":cement,"sand_m3":sand,"aggregate_m3":agg,"main_dia_mm":self.md,
        "main_spacing_mm":self.ms,"main_bar_count":mc,"main_bar_length_m":ml,"main_total_length_m":mt,"main_steel_kg":mw,
        "distribution_dia_mm":self.dd,"distribution_spacing_mm":self.ds,"distribution_bar_count":dc,"distribution_bar_length_m":dl,
        "distribution_total_length_m":dt,"distribution_steel_kg":dw,"base_steel_kg":base,"cutting_kg":cut,"steel_kg":steel,
        "binding_wire_kg":binding,"cement_rate":self.cr,"sand_rate":self.sr,"aggregate_rate":self.ar,"steel_rate":self.str,
        "skilled_days":sk,"skilled_rate":self.skr,"skilled_cost":sk*self.skr,"unskilled_days":un,"unskilled_rate":self.ur,
        "unskilled_cost":un*self.ur,"material_cost":material,"labour_cost":labour,"total_cost":total_cost}
        for k,v in vals.items(): r.add_value(k,v)
        return r
