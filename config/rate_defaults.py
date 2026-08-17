"""Central rate defaults read from Settings for all calculators."""
from __future__ import annotations
from config.setting import Settings

def get_estimation_rates() -> dict:
    data = Settings().get("estimation", {})
    if not isinstance(data, dict):
        data = {}
    return {
        "cement_rate": data.get("cement_rate", 1650.0),
        "sand_rate": data.get("sand_rate", 800.0),
        "aggregate_rate": data.get("aggregate_rate", 1000.0),
        "steel_rate": data.get("steel_rate", 280.0),
        "skilled_rate": data.get("skilled_labour_rate", 2500.0),
        "unskilled_rate": data.get("unskilled_labour_rate", 1250.0),
        "pcc_skilled_productivity": data.get("pcc_skilled_productivity", 1.0),
        "pcc_unskilled_productivity": data.get("pcc_unskilled_productivity", 2.0),
        "rcc_skilled_productivity": data.get("rcc_skilled_productivity", 1.0),
        "rcc_unskilled_productivity": data.get("rcc_unskilled_productivity", 2.0),
        "brickwork_skilled_productivity": data.get("brickwork_skilled_productivity", 10.0),
        "brickwork_unskilled_productivity": data.get("brickwork_unskilled_productivity", 15.0),
        "plaster_skilled_productivity": data.get("plaster_skilled_productivity", 10.0),
        "plaster_unskilled_productivity": data.get("plaster_unskilled_productivity", 15.0),
        "excavation_skilled_productivity": data.get("excavation_skilled_productivity", 8.0),
        "excavation_unskilled_productivity": data.get("excavation_unskilled_productivity", 6.0),
        "footing_skilled_productivity": data.get("footing_skilled_productivity", 1.0),
        "footing_unskilled_productivity": data.get("footing_unskilled_productivity", 2.0),
        "staircase_skilled_productivity": data.get("staircase_skilled_productivity", 1.0),
        "staircase_unskilled_productivity": data.get("staircase_unskilled_productivity", 2.0),
    }

def apply_rate_defaults(vars_dict: dict) -> None:
    rates = get_estimation_rates()
    aliases = {
        "cement_rate": ("cement_rate", "cement_bag_rate", "pcc_cement_rate"),
        "sand_rate": ("sand_rate", "pcc_sand_rate"),
        "aggregate_rate": ("aggregate_rate", "agg_rate", "pcc_agg_rate"),
        "steel_rate": ("steel_rate", "rate"),
        "skilled_rate": ("skilled_rate",),
        "unskilled_rate": ("unskilled_rate", "un_rate"),
        "pcc_skilled_productivity": ("pcc_skilled_productivity",),
        "pcc_unskilled_productivity": ("pcc_unskilled_productivity",),
        "rcc_skilled_productivity": ("rcc_skilled_productivity",),
        "rcc_unskilled_productivity": ("rcc_unskilled_productivity",),
        "brickwork_skilled_productivity": ("brickwork_skilled_productivity",),
        "brickwork_unskilled_productivity": ("brickwork_unskilled_productivity",),
        "plaster_skilled_productivity": ("plaster_skilled_productivity",),
        "plaster_unskilled_productivity": ("plaster_unskilled_productivity",),
        "excavation_skilled_productivity": ("excavation_skilled_productivity",),
        "excavation_unskilled_productivity": ("excavation_unskilled_productivity",),
        "footing_skilled_productivity": ("footing_skilled_productivity", "sk_prod"),
        "footing_unskilled_productivity": ("footing_unskilled_productivity", "un_prod"),
        "staircase_skilled_productivity": ("staircase_skilled_productivity", "sk_prod"),
        "staircase_unskilled_productivity": ("staircase_unskilled_productivity", "un_prod"),
    }
    for source, targets in aliases.items():
        for target in targets:
            var = vars_dict.get(target)
            if var is not None:
                var.set(str(rates[source]))
