"""
Civil Estimate Suite Pro v4.0
Engineer-friendly Slab Steel / Rebar Schedule Form
"""
from __future__ import annotations
from config.rate_defaults import apply_rate_defaults
import customtkinter as ctk
from tkinter import messagebox
from calculations.slab_steel_calculator import SlabSteelCalculator
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.slab_steel_estimate_service import SlabSteelEstimateService

FT_PER_M = 3.280839895013123
M_PER_FT = 0.3048
CFT_PER_M3 = 35.31466672148859
M3_PER_CFT = 0.028316846592

class SlabSteelCalculatorForm(BaseForm):
    def __init__(self,parent):
        super().__init__(parent,title="Slab Steel / Rebar Schedule",width=1180,height=800)
        self.result=None; self.analysis=None
        self.vars={k:ctk.StringVar(value=v) for k,v in {
            "unit":"m","length":"","width":"","cover":"20",
            "main_dia":"12","main_spacing":"150",
            "dist_dia":"10","dist_spacing":"200",
            "main_extra":"0","dist_extra":"0",
            "top":"No","top_main_dia":"10","top_main_spacing":"200",
            "top_dist_dia":"10","top_dist_spacing":"200",
            "cutting":"2","binding":"2","rate":"0"
        }.items()}
        apply_rate_defaults(self.vars)
        self._build()

    def _build(self):
        bar=ctk.CTkFrame(self.content_frame,fg_color="transparent");bar.pack(fill="x",padx=5,pady=(0,8))
        for text,cmd,w in [("Calculate",self.calculate,140),("Reset",self.reset_form,120),("Generate BOQ",self.generate_boq,160),("Generate Material",self.generate_material,175)]:
            ctk.CTkButton(bar,text=text,width=w,command=cmd).pack(side="left",padx=6)
        self.status=ctk.CTkLabel(bar,text="Ready",anchor="w");self.status.pack(side="left",padx=15)

        ws=ctk.CTkFrame(self.content_frame,fg_color="transparent");ws.pack(fill="both",expand=True)
        ws.grid_columnconfigure(0,weight=0,minsize=500);ws.grid_columnconfigure(1,weight=1);ws.grid_rowconfigure(0,weight=1)
        left=ctk.CTkScrollableFrame(ws,corner_radius=10);left.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        left.grid_columnconfigure(0,minsize=255);left.grid_columnconfigure(1,weight=1)
        r=0
        self._section(left,"1. Slab Dimensions",r);r+=1
        self._label(left,"Length Unit",r);ctk.CTkComboBox(left,variable=self.vars["unit"],values=["m","ft"],command=self._unit_changed).grid(row=r,column=1,padx=10,pady=7,sticky="ew");r+=1
        self._label(left,"Slab Length",r);self._entry(left,"length",r);r+=1
        self._label(left,"Slab Width",r);self._entry(left,"width",r);r+=1
        self._label(left,"Clear Cover (mm)",r);self._entry(left,"cover",r);r+=1

        self._section(left,"2. Bottom Reinforcement",r);r+=1
        for key,label in [("main_dia","Main Bar Diameter (mm)"),("main_spacing","Main Bar Spacing (mm)"),
                          ("dist_dia","Distribution Diameter (mm)"),("dist_spacing","Distribution Spacing (mm)"),
                          ("main_extra","Main Extra / Anchorage (m)"),("dist_extra","Distribution Extra / Anchorage (m)")]:
            self._label(left,label,r);self._entry(left,key,r);r+=1

        self._section(left,"3. Top Reinforcement (Optional)",r);r+=1
        self._label(left,"Top Steel?",r);ctk.CTkComboBox(left,variable=self.vars["top"],values=["No","Yes"]).grid(row=r,column=1,padx=10,pady=7,sticky="ew");r+=1
        for key,label in [("top_main_dia","Top Main Diameter (mm)"),("top_main_spacing","Top Main Spacing (mm)"),
                          ("top_dist_dia","Top Distribution Diameter (mm)"),("top_dist_spacing","Top Distribution Spacing (mm)")]:
            self._label(left,label,r);self._entry(left,key,r);r+=1

        self._section(left,"4. Allowance & Rate",r);r+=1
        self._label(left,"Cutting Allowance (%)",r);self._entry(left,"cutting",r);r+=1
        self._label(left,"Binding Wire (% Steel)",r);self._entry(left,"binding",r);r+=1
        self._label(left,"Steel Rate (PKR / kg)",r);self._entry(left,"rate",r)

        self.result_frame=ctk.CTkScrollableFrame(ws,corner_radius=10);self.result_frame.grid(row=0,column=1,sticky="nsew",padx=(8,0))
        self.result_frame.grid_columnconfigure(0,minsize=210);self.result_frame.grid_columnconfigure(1,weight=1)
        self._ready()

    def _label(self,p,t,r):
        x=ctk.CTkLabel(p,text=t,anchor="w");x.grid(row=r,column=0,padx=10,pady=7,sticky="w");return x
    def _entry(self,p,k,r):
        x=ctk.CTkEntry(p,textvariable=self.vars[k]);x.grid(row=r,column=1,padx=10,pady=7,sticky="ew");return x
    def _section(self,p,t,r):
        ctk.CTkLabel(p,text=t,font=ctk.CTkFont(size=18,weight="bold")).grid(row=r,column=0,columnspan=2,padx=10,pady=(15,8),sticky="w")
    def _unit_changed(self, _value=None):
        unit=self.vars["unit"].get()
        previous=getattr(self,"_last_unit","m")
        if unit != previous:
            try:
                factor=FT_PER_M if previous=="m" and unit=="ft" else M_PER_FT
                for key in ("length","width","main_extra","dist_extra"):
                    text=self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text)*factor:.6f}".rstrip("0").rstrip("."))
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
            top=self.vars["top"].get()=="Yes"
            self.result=SlabSteelCalculator(
                slab_length=self._num("length","Slab length",True),
                slab_width=self._num("width","Slab width",True),
                cover_mm=self._num("cover","Cover"),
                main_dia_mm=self._num("main_dia","Main diameter",True),
                main_spacing_mm=self._num("main_spacing","Main spacing",True),
                distribution_dia_mm=self._num("dist_dia","Distribution diameter",True),
                distribution_spacing_mm=self._num("dist_spacing","Distribution spacing",True),
                main_extra_length_m=self._num("main_extra","Main extra"),
                distribution_extra_length_m=self._num("dist_extra","Distribution extra"),
                top_steel=top,
                top_main_dia_mm=self._num("top_main_dia","Top main diameter") if top else 0,
                top_main_spacing_mm=self._num("top_main_spacing","Top main spacing") if top else 0,
                top_distribution_dia_mm=self._num("top_dist_dia","Top distribution diameter") if top else 0,
                top_distribution_spacing_mm=self._num("top_dist_spacing","Top distribution spacing") if top else 0,
                cutting_allowance_percent=self._num("cutting","Cutting allowance"),
                binding_wire_percent=self._num("binding","Binding wire"),
                steel_rate=self._num("rate","Steel rate"),
                length_unit=self.vars["unit"].get(),
            ).calculate()
            self.analysis=SlabSteelEstimateService.build_analysis(self.result,self._num("rate","Steel rate"))
            self._show();self.status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as e:messagebox.showerror("Slab Steel Error",str(e),parent=self)
    def _ready(self):
        for w in self.result_frame.winfo_children():w.destroy()
        self._section(self.result_frame,"Bar Schedule",0)
        ctk.CTkLabel(self.result_frame,text="Enter slab dimensions, cover, bottom reinforcement and optional top reinforcement, then Calculate.",wraplength=540,justify="left").grid(row=1,column=0,columnspan=2,padx=14,pady=12,sticky="ew")
    def _show(self):
        for w in self.result_frame.winfo_children():w.destroy()
        a=self.analysis;r=0
        self._section(self.result_frame,"Slab Steel Summary",r);r+=1
        rows=[("Slab",f"{a['slab_length']:.3f} × {a['slab_width']:.3f} {a['length_unit']}"),
              ("Clear Cover",f"{a['cover_mm']:.1f} mm"),
              ("Base Steel",f"{a['base_steel_kg']:.3f} kg"),
              ("Cutting Allowance",f"{a['cutting_kg']:.3f} kg"),
              ("Total Steel",f"{a['quantity']:.3f} kg"),
              ("Binding Wire",f"{a['binding_wire_kg']:.3f} kg")]
        r=self._rows(rows,r)
        self._section(self.result_frame,"Bar Schedule",r);r+=1
        schedule=[]
        for x in a["materials"]:
            schedule.append((x["name"],f"Ø{x['diameter_mm']:g} @ {x['spacing_mm']:g} mm | {x['bar_count']} bars × {x['bar_length_m']:.3f} m = {x['total_length_m']:.3f} m | {x['quantity']:.3f} kg"))
        r=self._rows(schedule,r)
        self._section(self.result_frame,"Cost",r);r+=1
        self._rows([("Steel Amount",f"PKR {a['total_cost']:,.2f}"),("Unit Rate",f"PKR {a['unit_rate']:,.2f} / kg")],r,True)
    def _rows(self,rows,start,bold=False):
        f=ctk.CTkFont(weight="bold") if bold else None
        for label,value in rows:
            ctk.CTkLabel(self.result_frame,text=label,anchor="w",font=f).grid(row=start,column=0,padx=(14,10),pady=5,sticky="w")
            ctk.CTkLabel(self.result_frame,text=value,anchor="w",font=f,justify="left",wraplength=600).grid(row=start,column=1,padx=(10,14),pady=5,sticky="ew");start+=1
        return start
    def generate_boq(self):
        if self.result is None:messagebox.showwarning("Slab Steel → BOQ","Please calculate slab steel first.",parent=self);return
        try:
            project=CurrentProject.get()
            if project is None or getattr(project,"id",None) is None:raise ValueError("Please select/open a project before generating BOQ.")
            context=self.application_context
            if context is None:raise ValueError("Application context is not available.")
            items=context.boq_controller.get_by_project(project.id) or [];highest=0
            for item in items:
                no=str(getattr(item,"item_no","")).upper()
                if no.startswith("SLAB-STEEL-"):
                    try:highest=max(highest,int(no.split("-",2)[2]))
                    except (ValueError,IndexError):pass
            no=f"SLAB-STEEL-{highest+1:02d}"
            boq=BOQ(project_id=project.id,item_no=no,description="Slab Reinforcement Steel",unit="kg",quantity=self.result.quantity,rate=self.analysis["unit_rate"],amount=self.analysis["total_cost"],remarks=f"Slab={self.analysis['slab_length']:.3f}×{self.analysis['slab_width']:.3f} {self.analysis['length_unit']} | Cover={self.analysis['cover_mm']:.1f} mm | Bar sets={len(self.analysis['materials'])}")
            bid=context.boq_controller.create(boq)
            context.estimate_analysis_service.save(project_id=project.id,boq_id=int(bid),calculator_type="Slab Steel",analysis=self.analysis)
            self.status.configure(text=f"BOQ {no} added successfully")
            messagebox.showinfo("Slab Steel → BOQ",f"BOQ item {no} created successfully.\n\nTotal Steel: {self.result.quantity:,.3f} kg\nBinding Wire: {self.analysis['binding_wire_kg']:,.3f} kg",parent=self)
        except Exception as e:messagebox.showerror("Slab Steel → BOQ Error",str(e),parent=self)
    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("SLAB STEEL Material", "Please calculate slab steel first.", parent=self)
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
                "SLAB STEEL Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("SLAB STEEL Material Error", str(ex), parent=self)
    def reset_form(self):
        vals={"unit":"m","length":"","width":"","cover":"20","main_dia":"12","main_spacing":"150","dist_dia":"10","dist_spacing":"200","main_extra":"0","dist_extra":"0","top":"No","top_main_dia":"10","top_main_spacing":"200","top_dist_dia":"10","top_dist_spacing":"200","cutting":"2","binding":"2","rate":"0"}
        for k,v in vals.items():self.vars[k].set(v)
        self.result=None;self.analysis=None;self.status.configure(text="Ready");self._ready()
    def has_result(self):return self.result is not None
