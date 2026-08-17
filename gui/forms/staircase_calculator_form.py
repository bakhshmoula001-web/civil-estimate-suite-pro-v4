from config.rate_defaults import apply_rate_defaults
import customtkinter as ctk
from tkinter import messagebox
from calculations.staircase_calculator import StaircaseCalculator
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.staircase_estimate_service import StaircaseEstimateService

FT_PER_M = 3.280839895013123
M_PER_FT = 0.3048
CFT_PER_M3 = 35.31466672148859
M3_PER_CFT = 0.028316846592

class StaircaseCalculatorForm(BaseForm):
    def __init__(self,parent):
        super().__init__(parent,title="Staircase Calculator",width=1200,height=820); self.result=None; self.analysis=None
        defaults={"unit":"m","floor":"3.0","width":"1.2","riser":"0.17","tread":"0.28","waist":"0.15","landing":"1.2","landing_t":"0.15","flights":"1","mix":"1:2:4","main_dia":"12","main_spacing":"150","dist_dia":"10","dist_spacing":"200","cover":"25","cutting":"2","binding":"2","cement_rate":"1650","sand_rate":"800","agg_rate":"1000","steel_rate":"280","sk_prod":"1","sk_rate":"2500","un_prod":"2","un_rate":"1250"}
        self.vars={k:ctk.StringVar(value=v) for k,v in defaults.items()}
        apply_rate_defaults(self.vars)
        self._build()
    def _build(self):
        top=ctk.CTkFrame(self.content_frame,fg_color="transparent"); top.pack(fill="x",padx=5,pady=8)
        for t,c,w in [("Calculate",self.calculate,140),("Reset",self.reset_form,120),("Generate BOQ",self.generate_boq,160),("Generate Material",self.generate_material,175)]: ctk.CTkButton(top,text=t,width=w,command=c).pack(side="left",padx=6)
        self.status=ctk.CTkLabel(top,text="Ready",anchor="w"); self.status.pack(side="left",padx=15)
        ws=ctk.CTkFrame(self.content_frame,fg_color="transparent"); ws.pack(fill="both",expand=True); ws.grid_columnconfigure(0,minsize=520); ws.grid_columnconfigure(1,weight=1); ws.grid_rowconfigure(0,weight=1)
        left=ctk.CTkScrollableFrame(ws); left.grid(row=0,column=0,sticky="nsew",padx=(0,8)); left.grid_columnconfigure(0,minsize=270); left.grid_columnconfigure(1,weight=1)
        r=0
        self._section(left,"1. Stair Geometry",r); r+=1
        self._combo(left,"unit","Length Unit",["m","ft"],r); r+=1
        for k,l in [("floor","Floor-to-Floor Height"),("width","Stair Width"),("riser","Riser Height"),("tread","Tread Width"),("waist","Waist Slab Thickness"),("landing","Landing Length"),("landing_t","Landing Thickness"),("flights","Number of Flights")]: self._label_entry(left,k,l,r); r+=1
        self._section(left,"2. Concrete",r); r+=1
        self._combo(left,"mix","Concrete Mix Ratio",["1:2:4","1:1.5:3","1:3:6"],r); r+=1
        for k,l in [("cement_rate","Cement Rate (PKR/bag)"),("sand_rate","Sand Rate (PKR/m³)"),("agg_rate","Aggregate Rate (PKR/m³)")]: self._label_entry(left,k,l,r); r+=1
        self._section(left,"3. Reinforcement",r); r+=1
        for k,l in [("main_dia","Main Bar Diameter (mm)"),("main_spacing","Main Bar Spacing (mm)"),("dist_dia","Distribution Diameter (mm)"),("dist_spacing","Distribution Spacing (mm)"),("cover","Clear Cover (mm)")]: self._label_entry(left,k,l,r); r+=1
        self._section(left,"4. Labour & Cost",r); r+=1
        for k,l in [("steel_rate","Steel Rate (PKR/kg)"),("cutting","Cutting Allowance (%)"),("binding","Binding Wire (% Steel)"),("sk_prod","Skilled Productivity (m³/day)"),("sk_rate","Skilled Labour (PKR/day)"),("un_prod","Unskilled Productivity (m³/day)"),("un_rate","Unskilled Labour (PKR/day)")]: self._label_entry(left,k,l,r); r+=1
        self.result_frame=ctk.CTkScrollableFrame(ws); self.result_frame.grid(row=0,column=1,sticky="nsew",padx=(8,0)); self.result_frame.grid_columnconfigure(0,minsize=220); self.result_frame.grid_columnconfigure(1,weight=1); self._ready()
    def _combo(self,p,k,l,vals,r):
        self._label(p,l,r)
        command=self._unit_changed if k=="unit" else None
        ctk.CTkComboBox(
            p,variable=self.vars[k],values=vals,command=command
        ).grid(row=r,column=1,padx=10,pady=7,sticky="ew")
    def _label_entry(self,p,k,l,r): self._label(p,l,r); ctk.CTkEntry(p,textvariable=self.vars[k]).grid(row=r,column=1,padx=10,pady=7,sticky="ew")
    def _label(self,p,t,r): ctk.CTkLabel(p,text=t,anchor="w").grid(row=r,column=0,padx=10,pady=7,sticky="w")
    def _section(self,p,t,r): ctk.CTkLabel(p,text=t,font=ctk.CTkFont(size=18,weight="bold")).grid(row=r,column=0,columnspan=2,padx=10,pady=(15,8),sticky="w")
    def _unit_changed(self, _value=None):
        unit=self.vars["unit"].get()
        previous=getattr(self,"_last_unit","m")
        if unit != previous:
            try:
                factor=FT_PER_M if previous=="m" and unit=="ft" else M_PER_FT
                for key in ("floor","width","riser","tread","waist","landing","landing_t"):
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

    def _n(self,k,l,pos=False):
        try:v=float(self.vars[k].get())
        except ValueError as e: raise ValueError(f"{l} must be a valid number.") from e
        if pos and v<=0: raise ValueError(f"{l} must be greater than zero.")
        if not pos and v<0: raise ValueError(f"{l} cannot be negative.")
        return v
    def calculate(self):
        try:
            self.result=StaircaseCalculator(floor_height=self._n("floor","Floor height",1),stair_width=self._n("width","Stair width",1),riser_height=self._n("riser","Riser",1),tread_width=self._n("tread","Tread",1),waist_thickness=self._n("waist","Waist",1),landing_length=self._n("landing","Landing",1),landing_thickness=self._n("landing_t","Landing thickness",1),flights=int(self._n("flights","Flights",1)),length_unit=self.vars["unit"].get(),mix_ratio=self.vars["mix"].get(),main_dia_mm=self._n("main_dia","Main diameter",1),main_spacing_mm=self._n("main_spacing","Main spacing",1),distribution_dia_mm=self._n("dist_dia","Distribution diameter",1),distribution_spacing_mm=self._n("dist_spacing","Distribution spacing",1),cover_mm=self._n("cover","Cover"),cutting_percent=self._n("cutting","Cutting"),binding_percent=self._n("binding","Binding"),cement_rate=self._n("cement_rate","Cement rate"),sand_rate=self._n("sand_rate","Sand rate"),aggregate_rate=self._n("agg_rate","Aggregate rate"),steel_rate=self._n("steel_rate","Steel rate"),skilled_productivity=self._n("sk_prod","Skilled productivity",1),skilled_rate=self._n("sk_rate","Skilled rate"),unskilled_productivity=self._n("un_prod","Unskilled productivity",1),unskilled_rate=self._n("un_rate","Unskilled rate")).calculate()
            self.analysis=StaircaseEstimateService.build_analysis(self.result); self._show(); self.status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as e: messagebox.showerror("Staircase Error",str(e),parent=self)
    def _ready(self):
        for w in self.result_frame.winfo_children(): w.destroy()
        self._section(self.result_frame,"Staircase Estimate",0)
        ctk.CTkLabel(self.result_frame,text="Enter stair geometry, concrete and reinforcement inputs, then Calculate.",wraplength=600).grid(row=1,column=0,columnspan=2,padx=14,pady=12,sticky="ew")
    def _rows(self,rows,r,bold=False):
        f=ctk.CTkFont(weight="bold") if bold else None
        for a,b in rows:
            ctk.CTkLabel(self.result_frame,text=a,anchor="w",font=f).grid(row=r,column=0,padx=14,pady=5,sticky="w"); ctk.CTkLabel(self.result_frame,text=b,anchor="w",font=f,wraplength=650).grid(row=r,column=1,padx=14,pady=5,sticky="ew"); r+=1
        return r
    def _show(self):
        for w in self.result_frame.winfo_children(): w.destroy()
        a=self.analysis; g=a["geometry"]; q=a["reinforcement"]; r=0
        self._section(self.result_frame,"1. Stair Geometry",r); r+=1
        r=self._rows([("Risers",f'{g["risers"]} @ {g["actual_riser_m"]*1000:.1f} mm'),("Treads",f'{g["treads"]} @ {g["tread_width"]:.3f}'),("Horizontal Run",f'{g["horizontal_run_m"]:.3f} m'),("Sloping Length",f'{g["slope_length_m"]:.3f} m'),("Concrete",f'{a["quantity"]:.3f} m³')],r)
        self._section(self.result_frame,"2. Materials",r); r+=1
        r=self._rows([(m["name"],f'{m["quantity"]:.3f} {m["unit"]} @ PKR {m["rate"]:.2f} = PKR {m["amount"]:,.2f}') for m in a["materials"]],r)
        self._section(self.result_frame,"3. Reinforcement",r); r+=1
        r=self._rows([("Main",f'Ø{q["main_dia_mm"]:g} @ {q["main_spacing_mm"]:g} mm | {q["main_bar_count"]} bars'),("Main Steel",f'{q["main_total_length_m"]:.3f} m | {q["main_steel_kg"]:.3f} kg'),("Distribution",f'Ø{q["distribution_dia_mm"]:g} @ {q["distribution_spacing_mm"]:g} mm | {q["distribution_bar_count"]} bars'),("Distribution Steel",f'{q["distribution_total_length_m"]:.3f} m | {q["distribution_steel_kg"]:.3f} kg'),("Total Steel",f'{q["steel_kg"]:.3f} kg'),("Binding Wire",f'{q["binding_wire_kg"]:.3f} kg')],r)
        self._section(self.result_frame,"4. Labour & Cost",r); r+=1
        r=self._rows([(x["name"],f'{x["quantity"]:.3f} {x["unit"]} × PKR {x["rate"]:,.2f} = PKR {x["amount"]:,.2f}') for x in a["labour"]],r)
        self._rows([("Material Cost",f'PKR {a["material_total"]:,.2f}'),("Labour Cost",f'PKR {a["labour_total"]:,.2f}'),("Total Cost",f'PKR {a["total_cost"]:,.2f}')],r,True)
    def generate_boq(self):
        if not self.result: messagebox.showwarning("Staircase → BOQ","Please calculate first.",parent=self); return
        try:
            project=CurrentProject.get()
            if project is None or getattr(project,"id",None) is None: raise ValueError("Please select/open a project before generating BOQ.")
            context=self.application_context
            if context is None: raise ValueError("Application context is not available.")
            items=context.boq_controller.get_by_project(project.id) or []; highest=0
            for item in items:
                no=str(getattr(item,"item_no","")).upper()
                if no.startswith("STAIRCASE-"):
                    try: highest=max(highest,int(no.split("-",1)[1]))
                    except (ValueError,IndexError): pass
            no=f"STAIRCASE-{highest+1:02d}"; g=self.analysis["geometry"]
            boq=BOQ(project_id=project.id,item_no=no,description="Staircase Concrete, Reinforcement & Labour",unit="m³",quantity=self.result.quantity,rate=self.analysis["total_cost"]/self.result.quantity,amount=self.analysis["total_cost"],remarks=f'{g["risers"]} risers | {g["treads"]} treads | {g["slope_length_m"]:.3f}m slope | Steel {self.analysis["reinforcement"]["steel_kg"]:.3f}kg')
            bid=context.boq_controller.create(boq); context.estimate_analysis_service.save(project_id=project.id,boq_id=int(bid),calculator_type="Staircase",analysis=self.analysis)
            messagebox.showinfo("Staircase → BOQ",f"{no} created successfully.",parent=self); self.status.configure(text=f"BOQ {no} added successfully")
        except Exception as e: messagebox.showerror("Staircase → BOQ Error",str(e),parent=self)
    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("STAIRCASE Material", "Please calculate staircase first.", parent=self)
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
                "STAIRCASE Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("STAIRCASE Material Error", str(ex), parent=self)
    def reset_form(self): self.__init__(self.master)
    def has_result(self): return self.result is not None

__all__=["StaircaseCalculatorForm"]
