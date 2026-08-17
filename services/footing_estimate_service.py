"""
Civil Estimate Suite Pro v4.0
Footing / Foundation Estimate Service
"""
from __future__ import annotations


class FootingEstimateService:
    @staticmethod
    def build_analysis(result):
        def material(name,unit,qty,rate):
            return {"name":name,"unit":unit,"quantity":round(float(qty),3),
                    "rate":round(float(rate),2),
                    "amount":round(float(qty)*float(rate),2)}
        materials=[
            material("Cement","bag",result.get_value("cement_bags",0),result.get_value("cement_rate",0)),
            material("Sand","m³",result.get_value("sand_m3",0),result.get_value("sand_rate",0)),
            material("Coarse Aggregate","m³",result.get_value("aggregate_m3",0),result.get_value("aggregate_rate",0)),
            material("Reinforcement Steel","kg",result.get_value("steel_kg",0),result.get_value("steel_rate",0)),
        ]
        pcc=result.get_value("pcc",{})
        if pcc:
            materials += [
                material("PCC Cement","bag",pcc.get("cement_bags",0),0),
                material("PCC Sand","m³",pcc.get("sand_m3",0),0),
                material("PCC Aggregate","m³",pcc.get("aggregate_m3",0),0),
            ]
        labour=[
            {"name":"Skilled Labour","unit":"day","quantity":round(float(result.get_value("skilled_days",0)),3),
             "rate":round(float(result.get_value("skilled_rate",0)),2),
             "amount":round(float(result.get_value("skilled_cost",0)),2)},
            {"name":"Unskilled Labour","unit":"day","quantity":round(float(result.get_value("unskilled_days",0)),3),
             "rate":round(float(result.get_value("unskilled_rate",0)),2),
             "amount":round(float(result.get_value("unskilled_cost",0)),2)},
        ]
        return {
            "version":1,"calculator":"Footing","description":result.description,
            "unit":"m³","quantity":round(float(result.get_value("wet_volume_m3",0)),3),
            "dimensions":{
                "length":float(result.get_value("footing_length",0)),
                "width":float(result.get_value("footing_width",0)),
                "thickness":float(result.get_value("footing_thickness",0)),
                "count":int(result.get_value("footing_count",1)),
                "unit":result.get_value("length_unit","m"),
            },
            "concrete":{
                "mix_ratio":result.get_value("mix_ratio","1:2:4"),
                "wet_volume_m3":float(result.get_value("wet_volume_m3",0)),
                "dry_volume_m3":float(result.get_value("dry_volume_m3",0)),
            },
            "reinforcement":{
                "main_dia_mm":float(result.get_value("steel_dia_mm",0)),
                "main_spacing_mm":float(result.get_value("steel_spacing_mm",0)),
                "main_bar_count":int(result.get_value("main_bar_count",0)),
                "main_bar_length_m":float(result.get_value("main_bar_length_m",0)),
                "main_total_length_m":float(result.get_value("main_total_length_m",0)),
                "main_weight_kg":float(result.get_value("main_steel_kg",0)),
                "distribution_dia_mm":float(result.get_value("distribution_dia_mm",0)),
                "distribution_spacing_mm":float(result.get_value("distribution_spacing_mm",0)),
                "distribution_bar_count":int(result.get_value("distribution_bar_count",0)),
                "distribution_bar_length_m":float(result.get_value("distribution_bar_length_m",0)),
                "distribution_total_length_m":float(result.get_value("distribution_total_length_m",0)),
                "distribution_weight_kg":float(result.get_value("distribution_steel_kg",0)),
                "total_steel_kg":float(result.get_value("steel_kg",0)),
                "binding_wire_kg":float(result.get_value("binding_wire_kg",0)),
            },
            "materials":materials,
            "material_total":round(float(result.get_value("material_cost",0)),2),
            "labour":labour,
            "labour_total":round(float(result.get_value("labour_cost",0)),2),
            "total_cost":round(float(result.get_value("total_cost",0)),2),
            "unit_rate":round(float(result.get_value("total_cost",0))/float(result.get_value("wet_volume_m3",1)),2),
            "pcc":pcc,
        }

__all__=["FootingEstimateService"]
