class StaircaseEstimateService:
    @staticmethod
    def build_analysis(result):
        def item(name,unit,q,rate):
            return {"name":name,"unit":unit,"quantity":round(float(q),3),"rate":round(float(rate),2),"amount":round(float(q)*float(rate),2)}
        mats=[item("Cement","bag",result.get_value("cement_bags",0),result.get_value("cement_rate",0)),
              item("Sand","m³",result.get_value("sand_m3",0),result.get_value("sand_rate",0)),
              item("Coarse Aggregate","m³",result.get_value("aggregate_m3",0),result.get_value("aggregate_rate",0)),
              item("Reinforcement Steel","kg",result.get_value("steel_kg",0),result.get_value("steel_rate",0))]
        lab=[item("Skilled Labour","day",result.get_value("skilled_days",0),result.get_value("skilled_rate",0)),
             item("Unskilled Labour","day",result.get_value("unskilled_days",0),result.get_value("unskilled_rate",0))]
        return {"version":1,"calculator":"Staircase","description":result.description,"unit":"m³","quantity":round(float(result.quantity),3),
        "geometry":{k:result.get_value(k) for k in ["floor_height","stair_width","actual_riser_m","risers","treads","tread_width","horizontal_run_m","slope_length_m","flights","length_unit"]},
        "concrete":{"mix_ratio":result.get_value("mix_ratio"),"wet_volume_m3":result.get_value("wet_volume_m3"),"dry_volume_m3":result.get_value("dry_volume_m3")},
        "reinforcement":{k:result.get_value(k) for k in ["main_dia_mm","main_spacing_mm","main_bar_count","main_bar_length_m","main_total_length_m","main_steel_kg","distribution_dia_mm","distribution_spacing_mm","distribution_bar_count","distribution_bar_length_m","distribution_total_length_m","distribution_steel_kg","steel_kg","binding_wire_kg"]},
        "materials":mats,"material_total":round(float(result.get_value("material_cost",0)),2),"labour":lab,
        "labour_total":round(float(result.get_value("labour_cost",0)),2),"total_cost":round(float(result.get_value("total_cost",0)),2)}
__all__=["StaircaseEstimateService"]
