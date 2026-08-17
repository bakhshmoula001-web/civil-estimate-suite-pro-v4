"""
Civil Estimate Suite Pro v4.0
RCC Detailed Estimate Service
"""
from __future__ import annotations

class RCCEstimateService:
    @staticmethod
    def build_analysis(result, material_rates, skilled_days, skilled_rate,
                       unskilled_days, unskilled_rate):
        def nn(v,label):
            try:x=float(v)
            except (TypeError,ValueError) as e: raise ValueError(f"{label} must be numeric.") from e
            if x<0: raise ValueError(f"{label} cannot be negative.")
            return x
        q=float(result.quantity)
        if q<=0: raise ValueError("RCC quantity must be greater than zero.")
        mats=[
            {"name":"Cement","unit":"Bags","quantity":round(float(result.cement_bags),3),
             "rate":nn(material_rates.get("cement_bag",0),"Cement rate")},
            {"name":"Sand","unit":("m³" if result.unit=="m³" else "Cft"),
             "quantity":round(float(result.sand_volume),3),
             "rate":nn(material_rates.get("sand",0),"Sand rate")},
            {"name":"Coarse Aggregate","unit":("m³" if result.unit=="m³" else "Cft"),
             "quantity":round(float(result.aggregate_volume),3),
             "rate":nn(material_rates.get("aggregate",0),"Aggregate rate")},
            {"name":"Reinforcement Steel","unit":"kg","quantity":round(nn(result.get_value("steel_kg",0),"Steel"),2),
             "rate":nn(material_rates.get("steel_kg",0),"Steel rate")},
            {"name":"Binding Wire","unit":"kg","quantity":round(nn(result.get_value("binding_wire_kg",0),"Binding wire"),2),
             "rate":nn(material_rates.get("binding_wire_kg",0),"Binding wire rate")},
        ]
        for x in mats:x["amount"]=round(x["quantity"]*x["rate"],2)
        form_area=nn(result.get_value("formwork",0),"Formwork")
        form_rate=nn(material_rates.get("formwork",0),"Formwork rate")
        form={"name":"Formwork","unit":"m²","quantity":round(form_area,3),
              "rate":form_rate,"amount":round(form_area*form_rate,2)}
        material_total=round(sum(x["amount"] for x in mats)+form["amount"],2)

        labour=[
            {"name":"Skilled Labour","unit":"day","quantity":round(nn(skilled_days,"Skilled days"),2),
             "rate":nn(skilled_rate,"Skilled rate")},
            {"name":"Unskilled Labour","unit":"day","quantity":round(nn(unskilled_days,"Unskilled days"),2),
             "rate":nn(unskilled_rate,"Unskilled rate")}
        ]
        for x in labour:x["amount"]=round(x["quantity"]*x["rate"],2)
        labour_total=round(sum(x["amount"] for x in labour),2)
        total=round(material_total+labour_total,2)
        return {
            "version":1,"calculator":"RCC","description":result.description,
            "unit":result.unit,
            "dimensions":{"length":float(result.get_value("length",0)),
                          "width":float(result.get_value("width",0)),
                          "height":float(result.get_value("height",0)),
                          "dimension_unit":result.get_value("dimension_unit","m")},
            "mix_ratio":result.get_value("mix_ratio",""),
            "quantity":round(q,3),
            "wet_volume":round(float(result.get_value("metric_quantity_m3",q)),3),
            "dry_volume":round(float(result.get_value("metric_dry_volume_m3",0)),3),
            "steel_kg":round(float(result.get_value("steel_kg",0)),2),
            "binding_wire_kg":round(float(result.get_value("binding_wire_kg",0)),2),
            "formwork":form,
            "materials":mats,"material_total":material_total,
            "labour":labour,"labour_total":labour_total,
            "total_cost":total,"unit_rate":round(total/q,2)
        }
__all__=["RCCEstimateService"]
