"""
Civil Estimate Suite Pro v4.0
Slab Steel Estimate Service
"""
from __future__ import annotations

class SlabSteelEstimateService:
    @staticmethod
    def build_analysis(result, steel_rate=0.0):
        rate=float(steel_rate)
        sets=result.get_value("bar_sets",[])
        materials=[]
        for s in sets:
            materials.append({
                "name":s["name"],"unit":"kg",
                "quantity":round(s["weight_kg"],3),
                "rate":round(rate,2),
                "amount":round(s["weight_kg"]*rate,2),
                "diameter_mm":s["diameter_mm"],
                "spacing_mm":s["spacing_mm"],
                "bar_count":s["bar_count"],
                "bar_length_m":s["bar_length_m"],
                "total_length_m":s["total_length_m"],
            })
        total=round(float(result.quantity)*rate,2)
        return {
            "version":1,"calculator":"Slab Steel",
            "description":result.description,"unit":"kg",
            "quantity":round(float(result.quantity),3),
            "slab_length":float(result.get_value("slab_length",0)),
            "slab_width":float(result.get_value("slab_width",0)),
            "length_unit":result.get_value("length_unit","m"),
            "cover_mm":float(result.get_value("cover_mm",0)),
            "cutting_allowance_percent":float(result.get_value("cutting_allowance_percent",0)),
            "binding_wire_percent":float(result.get_value("binding_wire_percent",0)),
            "base_steel_kg":round(float(result.get_value("base_steel_kg",0)),3),
            "cutting_kg":round(float(result.get_value("cutting_kg",0)),3),
            "binding_wire_kg":round(float(result.get_value("binding_wire_kg",0)),3),
            "materials":materials,
            "material_total":total,
            "labour":[],"labour_total":0.0,
            "total_cost":total,"unit_rate":round(rate,2),
        }
