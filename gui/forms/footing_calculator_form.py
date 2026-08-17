"""
Civil Estimate Suite Pro v4.0
Engineer-friendly Footing / Foundation Calculator
"""
from __future__ import annotations
from config.rate_defaults import apply_rate_defaults
import customtkinter as ctk
from tkinter import messagebox
from calculations.footing_calculator import FootingCalculator
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.footing_estimate_service import FootingEstimateService


FT_PER_M = 3.280839895013123
M_PER_FT = 0.3048
CFT_PER_M3 = 35.31466672148859
M3_PER_CFT = 0.028316846592

class FootingCalculatorForm(BaseForm):
    def __init__(self,parent):
        super().__init__(parent,title="Footing / Foundation Calculator",width=1200,height=820)
        self.result=None; self.analysis=None
        self.vars={k:ctk.StringVar(value=v) for k,v in {
            "unit":"m","count":"1","length":"2.0","width":"2.0","thickness":"0.45","cover":"50",
            "mix":"1:2:4","main_dia":"12","main_spacing":"150","dist_dia":"10","dist_spacing":"200",
            "cutting":"2","binding":"2","cement_rate":"1650","sand_rate":"800","agg_rate":"1000","steel_rate":"280",
            "sk_prod":"1.0","sk_rate":"2500","un_prod":"2.0","un_rate":"1250",
            "pcc":"No","pcc_t":"0.075","pcc_mix":"1:4:8","pcc_cement_rate":"1650","pcc_sand_rate":"800","pcc_agg_rate":"1000"
        }.items()}
        apply_rate_defaults(self.vars)
        self._build()

    def _build(self):
        bar=ctk.CTkFrame(self.content_frame,fg_color="transparent");bar.pack(fill="x",padx=5,pady=(0,8))
        for text,cmd,w in [("Calculate",self.calculate,140),("Reset",self.reset_form,120),("Generate BOQ",self.generate_boq,160),("Generate Material",self.generate_material,175)]:
            ctk.CTkButton(bar,text=text,width=w,command=cmd).pack(side="left",padx=6)
        self.status=ctk.CTkLabel(bar,text="Ready",anchor="w");self.status.pack(side="left",padx=15)

        ws=ctk.CTkFrame(self.content_frame,fg_color="transparent");ws.pack(fill="both",expand=True)
        ws.grid_columnconfigure(0,weight=0,minsize=520);ws.grid_columnconfigure(1,weight=1);ws.grid_rowconfigure(0,weight=1)
        left=ctk.CTkScrollableFrame(ws,corner_radius=10);left.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        left.grid_columnconfigure(0,minsize=270);left.grid_columnconfigure(1,weight=1)
        r=0
        self._section(left,"1. Footing Dimensions",r);r+=1
        self._combo(left,"unit","Length Unit",["m","ft"],r);r+=1
        for k,l in [("count","Number of Footings"),("length","Footing Length"),("width","Footing Width"),("thickness","Footing Thickness"),("cover","Clear Cover (mm)")]:
            self._label(left,l,r);self._entry(left,k,r);r+=1
        self._section(left,"2. Concrete",r);r+=1
        self._label(left,"Concrete Mix Ratio",r);ctk.CTkComboBox(left,variable=self.vars["mix"],values=["1:2:4","1:1.5:3","1:3:6"]).grid(row=r,column=1,padx=10,pady=7,sticky="ew");r+=1
        for k,l in [("cement_rate","Cement Rate (PKR / bag)"),("sand_rate","Sand Rate (PKR / m³)"),("agg_rate","Aggregate Rate (PKR / m³)")]:
            self._label(left,l,r);self._entry(left,k,r);r+=1
        self._section(left,"3. Bottom Reinforcement",r);r+=1
        for k,l in [("main_dia","Main Bar Diameter (mm)"),("main_spacing","Main Bar Spacing (mm)"),("dist_dia","Distribution Diameter (mm)"),("dist_spacing","Distribution Spacing (mm)")]:
            self._label(left,l,r);self._entry(left,k,r);r+=1
        self._section(left,"4. Steel & Labour",r);r+=1
        for k,l in [("steel_rate","Steel Rate (PKR / kg)"),("cutting","Steel Cutting (%)"),("binding","Binding Wire (% Steel)"),
                    ("sk_prod","Skilled Productivity (m³/day)"),("sk_rate","Skilled Labour (PKR/day)"),
                    ("un_prod","Unskilled Productivity (m³/day)"),("un_rate","Unskilled Labour (PKR/day)")]:
            self._label(left,l,r);self._entry(left,k,r);r+=1
        self._section(left,"5. PCC Blinding (Optional)",r);r+=1
        self._combo(left,"pcc","Include PCC?",["No","Yes"],r);r+=1
        for k,l in [("pcc_t","PCC Thickness (m)"),("pcc_mix","PCC Mix Ratio"),("pcc_cement_rate","PCC Cement Rate"),
                    ("pcc_sand_rate","PCC Sand Rate"),("pcc_agg_rate","PCC Aggregate Rate")]:
            self._label(left,l,r)
            if k=="pcc_mix":
                ctk.CTkComboBox(left,variable=self.vars[k],values=["1:4:8","1:3:6"]).grid(row=r,column=1,padx=10,pady=7,sticky="ew")
            else:self._entry(left,k,r)
            r+=1

        self.result_frame=ctk.CTkScrollableFrame(ws,corner_radius=10);self.result_frame.grid(row=0,column=1,sticky="nsew",padx=(8,0))
        self.result_frame.grid_columnconfigure(0,minsize=220);self.result_frame.grid_columnconfigure(1,weight=1)
        self._ready()

    def _combo(self,p,k,label,values,r):
        self._label(p,label,r)
        command = self._unit_changed if k == "unit" else None
        ctk.CTkComboBox(
            p, variable=self.vars[k], values=values, command=command
        ).grid(row=r,column=1,padx=10,pady=7,sticky="ew")
    def _label(self,p,t,r):ctk.CTkLabel(p,text=t,anchor="w").grid(row=r,column=0,padx=10,pady=7,sticky="w")
    def _entry(self,p,k,r):ctk.CTkEntry(p,textvariable=self.vars[k]).grid(row=r,column=1,padx=10,pady=7,sticky="ew")
    def _section(self,p,t,r):ctk.CTkLabel(p,text=t,font=ctk.CTkFont(size=18,weight="bold")).grid(row=r,column=0,columnspan=2,padx=10,pady=(15,8),sticky="w")
    def _unit_changed(self, _value=None):
        unit=self.vars["unit"].get()
        previous=getattr(self,"_last_unit","m")
        if unit != previous:
            try:
                factor=FT_PER_M if previous=="m" and unit=="ft" else M_PER_FT
                for key in ("length","width","thickness","pcc_t"):
                    text=self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text)*factor:.6f}".rstrip("0").rstrip("."))
                productivity_factor=CFT_PER_M3 if previous=="m" and unit=="ft" else M3_PER_CFT
                for key in ("sk_prod","un_prod"):
                    text=self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text)*productivity_factor:.4f}".rstrip("0").rstrip("."))
            except (ValueError,TypeError):
                pass
        self._last_unit=unit

    def _num(self,k,label,pos=False):
        try:v=float(self.vars[k].get())
        except ValueError as e:raise ValueError(f"{label} must be a valid number.") from e
        if pos and v<=0:raise ValueError(f"{label} must be greater than zero.")
        if not pos and v<0:raise ValueError(f"{label} cannot be negative.")
        return v

    def calculate(self):
        try:
            self.result=FootingCalculator(
                footing_length=self._num("length","Footing length",True),
                footing_width=self._num("width","Footing width",True),
                footing_thickness=self._num("thickness","Footing thickness",True),
                footing_count=int(self._num("count","Number of footings",True)),
                length_unit=self.vars["unit"].get(),mix_ratio=self.vars["mix"].get(),
                steel_dia_mm=self._num("main_dia","Main diameter",True),
                steel_spacing_mm=self._num("main_spacing","Main spacing",True),
                distribution_dia_mm=self._num("dist_dia","Distribution diameter",True),
                distribution_spacing_mm=self._num("dist_spacing","Distribution spacing",True),
                cover_mm=self._num("cover","Cover"),
                steel_cutting_percent=self._num("cutting","Cutting allowance"),
                binding_wire_percent=self._num("binding","Binding wire"),
                concrete_skilled_productivity=self._num("sk_prod","Skilled productivity",True),
                concrete_skilled_rate=self._num("sk_rate","Skilled labour rate"),
                concrete_unskilled_productivity=self._num("un_prod","Unskilled productivity",True),
                concrete_unskilled_rate=self._num("un_rate","Unskilled labour rate"),
                cement_rate=self._num("cement_rate","Cement rate"),
                sand_rate=self._num("sand_rate","Sand rate"),
                aggregate_rate=self._num("agg_rate","Aggregate rate"),
                steel_rate=self._num("steel_rate","Steel rate"),
                include_pcc=self.vars["pcc"].get()=="Yes",
                pcc_thickness=self._num("pcc_t","PCC thickness"),
                pcc_mix_ratio=self.vars["pcc_mix"].get(),
                pcc_cement_rate=self._num("pcc_cement_rate","PCC cement rate"),
                pcc_sand_rate=self._num("pcc_sand_rate","PCC sand rate"),
                pcc_aggregate_rate=self._num("pcc_agg_rate","PCC aggregate rate"),
            ).calculate()
            self.analysis=FootingEstimateService.build_analysis(self.result)
            self._show();self.status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as e:messagebox.showerror("Footing Error",str(e),parent=self)

    def _ready(self):
        for w in self.result_frame.winfo_children():w.destroy()
        self._section(self.result_frame,"Footing Estimate",0)
        ctk.CTkLabel(self.result_frame,text="Enter footing dimensions, concrete mix, reinforcement and labour inputs, then Calculate.",wraplength=600,justify="left").grid(row=1,column=0,columnspan=2,padx=14,pady=12,sticky="ew")

    def _show(self):
        for w in self.result_frame.winfo_children():w.destroy()
        a=self.analysis;r=0
        self._section(self.result_frame,"1. Quantity Summary",r);r+=1
        r=self._rows([("Footings",str(a["dimensions"]["count"])),("Size",f'{a["dimensions"]["length"]:.3f} × {a["dimensions"]["width"]:.3f} × {a["dimensions"]["thickness"]:.3f} {a["dimensions"]["unit"]}'),
                      ("Concrete",f'{a["quantity"]:,.3f} m³'),("Mix",a["concrete"]["mix_ratio"]),("Dry Volume",f'{a["concrete"]["dry_volume_m3"]:,.3f} m³')],r)
        self._section(self.result_frame,"2. Concrete Materials",r);r+=1
        mats=[m for m in a["materials"] if "Reinforcement" not in m["name"] and not m["name"].startswith("PCC")]
        r=self._rows([(m["name"],f'{m["quantity"]:,.3f} {m["unit"]} @ PKR {m["rate"]:,.2f} = PKR {m["amount"]:,.2f}') for m in mats],r)
        self._section(self.result_frame,"3. Reinforcement",r);r+=1
        r=self._rows([
            ("Main",f'Ø{a["reinforcement"]["main_dia_mm"]:g} @ {a["reinforcement"]["main_spacing_mm"]:g} mm | {a["reinforcement"]["main_bar_count"]} bars'),
            ("Main Steel",f'{a["reinforcement"]["main_total_length_m"]:,.3f} m | {a["reinforcement"]["main_weight_kg"]:,.3f} kg'),
            ("Distribution",f'Ø{a["reinforcement"]["distribution_dia_mm"]:g} @ {a["reinforcement"]["distribution_spacing_mm"]:g} mm | {a["reinforcement"]["distribution_bar_count"]} bars'),
            ("Distribution Steel",f'{a["reinforcement"]["distribution_total_length_m"]:,.3f} m | {a["reinforcement"]["distribution_weight_kg"]:,.3f} kg'),
            ("Total Steel",f'{a["reinforcement"]["total_steel_kg"]:,.3f} kg'),
            ("Binding Wire",f'{a["reinforcement"]["binding_wire_kg"]:,.3f} kg'),
        ],r)
        self._section(self.result_frame,"4. Labour",r);r+=1
        r=self._rows([(x["name"],f'{x["quantity"]:,.3f} {x["unit"]} × PKR {x["rate"]:,.2f} = PKR {x["amount"]:,.2f}') for x in a["labour"]],r)
        self._section(self.result_frame,"5. Cost Summary",r);r+=1
        self._rows([("Material Cost",f'PKR {a["material_total"]:,.2f}'),("Labour Cost",f'PKR {a["labour_total"]:,.2f}'),("Total Cost",f'PKR {a["total_cost"]:,.2f}'),("Unit Rate",f'PKR {a["unit_rate"]:,.2f} / m³')],r,True)

    def _rows(self,rows,start,bold=False):
        f=ctk.CTkFont(weight="bold") if bold else None
        for label,value in rows:
            ctk.CTkLabel(self.result_frame,text=label,anchor="w",font=f).grid(row=start,column=0,padx=(14,10),pady=5,sticky="w")
            ctk.CTkLabel(self.result_frame,text=value,anchor="w",font=f,justify="left",wraplength=650).grid(row=start,column=1,padx=(10,14),pady=5,sticky="ew");start+=1
        return start

    def generate_boq(self):
        if self.result is None:
            messagebox.showwarning("Footing → BOQ","Please calculate footing first.",parent=self);return
        try:
            project=CurrentProject.get()
            if project is None or getattr(project,"id",None) is None:raise ValueError("Please select/open a project before generating BOQ.")
            context=self.application_context
            if context is None:raise ValueError("Application context is not available.")
            items=context.boq_controller.get_by_project(project.id) or [];highest=0
            for item in items:
                no=str(getattr(item,"item_no","")).upper()
                if no.startswith("FOOTING-"):
                    try:highest=max(highest,int(no.split("-",1)[1]))
                    except (ValueError,IndexError):pass
            item_no=f"FOOTING-{highest+1:02d}"
            d=self.analysis["dimensions"]
            boq=BOQ(project_id=project.id,item_no=item_no,description="Footing / Foundation Concrete & Reinforcement",
                    unit="m³",quantity=self.result.quantity,rate=self.analysis["unit_rate"],amount=self.analysis["total_cost"],
                    remarks=f'{d["count"]} footing(s) | {d["length"]:.3f}×{d["width"]:.3f}×{d["thickness"]:.3f} {d["unit"]} | Mix {self.analysis["concrete"]["mix_ratio"]} | Steel {self.analysis["reinforcement"]["total_steel_kg"]:.3f} kg')
            bid=context.boq_controller.create(boq)
            context.estimate_analysis_service.save(project_id=project.id,boq_id=int(bid),calculator_type="Footing",analysis=self.analysis)
            self.status.configure(text=f"BOQ {item_no} added successfully")
            messagebox.showinfo("Footing → BOQ",f"BOQ item {item_no} created successfully.\n\nConcrete: {self.result.quantity:,.3f} m³\nSteel: {self.analysis['reinforcement']['total_steel_kg']:,.3f} kg\nMaterial: PKR {self.analysis['material_total']:,.2f}\nLabour: PKR {self.analysis['labour_total']:,.2f}",parent=self)
        except Exception as e:messagebox.showerror("Footing → BOQ Error",str(e),parent=self)

    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("FOOTING Material", "Please calculate footing first.", parent=self)
            return
        try:
            project = CurrentProject.get()
            if project is None or getattr(project, "id", None) is None:
                raise ValueError("Please select/open a project before generating material.")
            context = self.application_context
            controller = getattr(context, "material_controller", None) if context else None
            if controller is None:
                raise ValueError("Material Controller is not available.")

            # The calculator already builds a complete engineer-facing
            # analysis immediately after Calculate(). Use that analysis
            # as the single source for Material generation. Older code
            # tried to rebuild it through a generic "CALC" result path,
            # which cannot know the calculator-specific material schedule
            # for steel/slab/column/beam/footing/staircase.
            analysis = getattr(self, "analysis", None)

            # Compatibility for any older form that did not store
            # self.analysis but exposes one of the legacy builders.
            if not (isinstance(analysis, dict) and analysis.get("materials")):
                for method_name in (
                    "_analysis",
                    "_build_analysis",
                    "_try_build_analysis",
                ):
                    method = getattr(self, method_name, None)
                    if callable(method):
                        try:
                            candidate = method()
                        except TypeError:
                            candidate = None
                        if isinstance(candidate, dict):
                            analysis = candidate
                            if candidate.get("materials"):
                                break

            if isinstance(analysis, dict) and analysis.get("materials"):
                records = controller.generate_from_analysis(
                    analysis,
                    project.id,
                )
            else:
                raise ValueError(
                    "The calculator has no material analysis. "
                    "Please press Calculate first."
                )

            lines = []
            for record in records:
                lines.append(
                    f"• {record.material_name}: {float(record.quantity):,.3f} {record.unit}"
                )
            messagebox.showinfo(
                "FOOTING Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("FOOTING Material Error", str(ex), parent=self)
    def reset_form(self):
        defaults={"unit":"m","count":"1","length":"2.0","width":"2.0","thickness":"0.45","cover":"50","mix":"1:2:4","main_dia":"12","main_spacing":"150","dist_dia":"10","dist_spacing":"200","cutting":"2","binding":"2","cement_rate":"1650","sand_rate":"800","agg_rate":"1000","steel_rate":"280","sk_prod":"1.0","sk_rate":"2500","un_prod":"2.0","un_rate":"1250","pcc":"No","pcc_t":"0.075","pcc_mix":"1:4:8","pcc_cement_rate":"1650","pcc_sand_rate":"800","pcc_agg_rate":"1000"}
        for k,v in defaults.items():self.vars[k].set(v)
        self.result=None;self.analysis=None;self.status.configure(text="Ready");self._ready()
    def has_result(self):return self.result is not None

__all__=["FootingCalculatorForm"]
