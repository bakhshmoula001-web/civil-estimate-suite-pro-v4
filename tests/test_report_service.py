
from pathlib import Path
import tempfile
from reports.material_report_service import MaterialReportService

class Project:
    project_code="QA-001"; project_name="Report Integration Test"
    client_name="Test Client"; location="Jacobabad"

class Item:
    id=101; item_no="PCC-01"; description="PCC 1:2:4"
    unit="Cft"; quantity=112.5

def main():
    analyses={101:{
        "_calculator_type":"PCC",
        "dimensions":{"length":10,"width":15,"height":0.75,"dimension_unit":"ft"},
        "materials":[
            {"name":"Cement","quantity":20.03,"unit":"Bags","rate":1750,"amount":35052.50},
            {"name":"Sand","quantity":49.511,"unit":"Cft","rate":22.65,"amount":1121.42},
            {"name":"Coarse Aggregate","quantity":98.987,"unit":"Cft","rate":28.32,"amount":2803.31}],
        "labour":[
            {"name":"Skilled Labour","quantity":3.19,"unit":"day","rate":2500,"amount":7975},
            {"name":"Unskilled Labour","quantity":1.59,"unit":"day","rate":1250,"amount":1987.50}],
        "material_total":38977.23,"labour_total":9962.50,"total_cost":48939.73}}

    with tempfile.TemporaryDirectory() as tmp:
        service=MaterialReportService(tmp)
        excel,pdf=service.export_both(Project(),[Item()],analyses)
        assert Path(excel).exists() and Path(excel).stat().st_size > 1000
        assert Path(pdf).exists() and Path(pdf).stat().st_size > 1000

        from openpyxl import load_workbook
        wb=load_workbook(excel,data_only=False)
        assert {"Detailed Estimate","Material Summary","Labour Summary","Cost Summary"}.issubset(wb.sheetnames)

        ws=wb["Detailed Estimate"]
        rows=list(ws.iter_rows(min_row=8,max_row=9,values_only=True))
        assert rows[1][1]=="PCC-01"
        assert "Cement: 20.030 Bags" in rows[1][6]
        assert "Sand: 49.511 Cft" in rows[1][6]
        assert "Coarse Aggregate: 98.987 Cft" in rows[1][6]
        assert rows[1][7].startswith("3.19 day")
        assert rows[1][8].startswith("1.59 day")
        assert abs(rows[1][9]-38977.23)<0.01
        assert abs(rows[1][10]-9962.50)<0.01
        assert abs(rows[1][11]-48939.73)<0.01

        ms=wb["Material Summary"]
        material_names={r[1] for r in ms.iter_rows(min_row=2,values_only=True)}
        assert {"Cement","Sand","Coarse Aggregate"} <= material_names

    print("REPORT QA: PASS")
    print("Excel non-blank: PASS")
    print("PDF non-blank: PASS")
    print("Detailed dimensions and quantity: PASS")
    print("Material quantities: PASS")
    print("Skilled/Unskilled labour: PASS")
    print("Material/Labour/Grand totals: PASS")
    print("Material Summary: PASS")

if __name__=="__main__":
    main()
