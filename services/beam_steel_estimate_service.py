"""
Civil Estimate Suite Pro v4.0
Beam Steel Estimate Service
"""
from __future__ import annotations


class BeamSteelEstimateService:
    @staticmethod
    def build_analysis(result, steel_rate=0.0):
        rate=float(steel_rate)
        bottom=float(result.get_value("bottom_kg",0))
        top=float(result.get_value("top_kg",0))
        stirrup=float(result.get_value("stirrup_kg",0))
        total=float(result.quantity)
        return {
            "version":1,
            "calculator":"Beam Steel",
            "description":result.description,
            "unit":"kg",
            "quantity":round(total,3),
            "dimensions":{
                "length":float(result.get_value("beam_length",0)),
                "width":float(result.get_value("beam_width",0)),
                "depth":float(result.get_value("beam_depth",0)),
                "count":int(result.get_value("beam_count",1)),
                "unit":result.get_value("length_unit","m"),
                "cover_mm":float(result.get_value("cover_mm",0)),
            },
            "bottom":{
                "diameter_mm":float(result.get_value("bottom_dia_mm",0)),
                "bars":int(result.get_value("bottom_bars",0)),
                "length_each_m":float(result.get_value("bottom_length_each_m",0)),
                "total_length_m":float(result.get_value("bottom_total_length_m",0)),
                "weight_kg":round(bottom,3),
            },
            "top":{
                "diameter_mm":float(result.get_value("top_dia_mm",0)),
                "bars":int(result.get_value("top_bars",0)),
                "length_each_m":float(result.get_value("top_length_each_m",0)),
                "total_length_m":float(result.get_value("top_total_length_m",0)),
                "weight_kg":round(top,3),
            },
            "stirrups":{
                "diameter_mm":float(result.get_value("stirrup_dia_mm",0)),
                "spacing_mm":float(result.get_value("stirrup_spacing_mm",0)),
                "count_one":int(result.get_value("stirrup_count_one",0)),
                "total_count":int(result.get_value("stirrup_total_count",0)),
                "cutting_length_m":float(result.get_value("stirrup_cutting_length_m",0)),
                "total_length_m":float(result.get_value("stirrup_total_length_m",0)),
                "weight_kg":round(stirrup,3),
            },
            "base_steel_kg":round(float(result.get_value("base_steel_kg",0)),3),
            "cutting_kg":round(float(result.get_value("cutting_kg",0)),3),
            "binding_wire_kg":round(float(result.get_value("binding_wire_kg",0)),3),
            "materials":[
                {"name":"Bottom Reinforcement","unit":"kg","quantity":round(bottom,3),"rate":rate,"amount":round(bottom*rate,2)},
                {"name":"Top Reinforcement","unit":"kg","quantity":round(top,3),"rate":rate,"amount":round(top*rate,2)},
                {"name":"Stirrups / Ties","unit":"kg","quantity":round(stirrup,3),"rate":rate,"amount":round(stirrup*rate,2)},
            ],
            "material_total":round(total*rate,2),
            "labour":[],"labour_total":0.0,
            "total_cost":round(total*rate,2),
            "unit_rate":round(rate,2),
        }

__all__=["BeamSteelEstimateService"]
