"""
Civil Estimate Suite Pro v4.0
RCC Detailed Calculator Form
"""
from __future__ import annotations
from config.rate_defaults import apply_rate_defaults
import customtkinter as ctk
from tkinter import messagebox
from calculations.calculator_factory import CalculatorFactory
from calculations.calculation_result import CalculationResult
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.rcc_estimate_service import RCCEstimateService
from services.unit_quantity_service import UnitQuantityService

class RCCCalculatorForm(BaseForm):
    def __init__(self,parent):
        super().__init__(parent,title="RCC Calculator",width=1120,height=760)
        self.result:CalculationResult|None=None
        self.analysis=None
        self._last_unit="m³"
        defaults={
            "volume_unit":"m³","length":"","width":"","height":"",
            "mix_ratio":"1:2:4","steel_kg":"0","binding_wire_percent":"2",
            "formwork":"0","cement_rate":"0","sand_rate":"0",
            "aggregate_rate":"0","steel_rate":"0","binding_rate":"0",
            "formwork_rate":"0","skilled_productivity":"1",
            "skilled_rate":"0","unskilled_productivity":"2","unskilled_rate":"0"}
        self.vars={k:ctk.StringVar(value=v) for k,v in defaults.items()}
        apply_rate_defaults(self.vars)
        self._build()
    def _build(self):
        bar=ctk.CTkFrame(self.content_frame,fg_color="transparent");bar.pack(fill="x",padx=5,pady=(0,8))
        for text,cmd,w in [("Calculate",self.calculate,140),("Reset",self.reset_form,120),
                           ("Generate BOQ",self.generate_boq,160),("Generate Material",self.generate_material,175)]:
            ctk.CTkButton(bar,text=text,width=w,command=cmd).pack(side="left",padx=6)
        self.status=ctk.CTkLabel(bar,text="Ready",anchor="w");self.status.pack(side="left",padx=15)
        ws=ctk.CTkFrame(self.content_frame,fg_color="transparent");ws.pack(fill="both",expand=True)
        ws.grid_columnconfigure(0,weight=0,minsize=475);ws.grid_columnconfigure(1,weight=1);ws.grid_rowconfigure(0,weight=1)
        left=ctk.CTkScrollableFrame(ws,corner_radius=10);left.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        left.grid_columnconfigure(0,minsize=225);left.grid_columnconfigure(1,weight=1)
        r=0
        self._section(left,"1. RCC Quantity",r);r+=1
        self._label(left,"Quantity Unit",r);ctk.CTkComboBox(left,variable=self.vars["volume_unit"],values=["m³","Cft"],command=self._unit).grid(row=r,column=1,padx=10,pady=7,sticky="ew");r+=1
        self.l_lbl=self._label(left,"Length (m)",r);self._entry(left,"length",r);r+=1
        self.w_lbl=self._label(left,"Width (m)",r);self._entry(left,"width",r);r+=1
        self.h_lbl=self._label(left,"Thickness / Height (m)",r);self._entry(left,"height",r);r+=1
        self._label(left,"Mix Ratio",r);ctk.CTkComboBox(left,variable=self.vars["mix_ratio"],values=["1:2:4","1:3:6","1:1.5:3","1:4:8"]).grid(row=r,column=1,padx=10,pady=7,sticky="ew");r+=1
        self._section(left,"2. Reinforcement & Formwork",r);r+=1
        self._label(left,"Steel (kg)",r);self._entry(left,"steel_kg",r);r+=1
        self._label(left,"Binding Wire (% of steel)",r);self._entry(left,"binding_wire_percent",r);r+=1
        self._label(left,"Formwork Area (m²)",r);self._entry(left,"formwork",r);r+=1
        self._section(left,"3. Material Rates",r);r+=1
        self._label(left,"Cement (PKR / Bag)",r)
        self._entry(left,"cement_rate",r)
        r += 1

        self.sand_rate_label = self._label(
            left, "Sand (PKR / m³)", r
        )
        self._entry(left,"sand_rate",r)
        r += 1

        self.aggregate_rate_label = self._label(
            left, "Aggregate (PKR / m³)", r
        )
        self._entry(left,"aggregate_rate",r)
        r += 1

        for key,label in [
            ("steel_rate","Steel (PKR / kg)"),
            ("binding_rate","Binding Wire (PKR / kg)"),
            ("formwork_rate","Formwork (PKR / m²)"),
        ]:
            self._label(left,label,r)
            self._entry(left,key,r)
            r += 1
        self._section(left,"4. Labour Norms & Rates",r);r+=1
        self.sp_lbl=self._label(left,"Skilled productivity (m³ / day)",r);self._entry(left,"skilled_productivity",r);r+=1
        self._label(left,"Skilled labour (PKR / day)",r);self._entry(left,"skilled_rate",r);r+=1
        self.up_lbl=self._label(left,"Unskilled productivity (m³ / day)",r);self._entry(left,"unskilled_productivity",r);r+=1
        self._label(left,"Unskilled labour (PKR / day)",r);self._entry(left,"unskilled_rate",r)
        self.result_frame=ctk.CTkScrollableFrame(ws,corner_radius=10);self.result_frame.grid(row=0,column=1,sticky="nsew",padx=(8,0))
        self.result_frame.grid_columnconfigure(0,minsize=205);self.result_frame.grid_columnconfigure(1,weight=1);self._ready()
    def _label(self,p,t,r):
        x=ctk.CTkLabel(p,text=t,anchor="w");x.grid(row=r,column=0,padx=10,pady=7,sticky="w");return x
    def _entry(self,p,k,r):
        x=ctk.CTkEntry(p,textvariable=self.vars[k]);x.grid(row=r,column=1,padx=10,pady=7,sticky="ew");return x
    def _section(self,p,t,r):
        ctk.CTkLabel(p,text=t,font=ctk.CTkFont(size=18,weight="bold")).grid(row=r,column=0,columnspan=2,padx=10,pady=(15,8),sticky="w")
    def _unit(self, _=None):
        """
        Switch the engineer's working volume unit without changing the
        physical quantity.

        Dimensions are converted together (m <-> ft).
        Volume material rates and productivity are converted so the
        resulting cost remains unchanged.
        """
        unit = self.vars["volume_unit"].get()
        previous = self._last_unit

        if unit != previous:
            try:
                # Length dimensions: m <-> ft.
                length_factor = (
                    3.280839895 if previous == "m³" and unit == "Cft"
                    else 0.3048
                )

                for key in ("length", "width", "height"):
                    text = self.vars[key].get().strip()
                    if text:
                        value = float(text) * length_factor
                        self.vars[key].set(
                            f"{value:.6f}".rstrip("0").rstrip(".")
                        )

                # Unit-rate conversion:
                # PKR/m³ -> PKR/Cft uses m³ per Cft.
                for key in ("sand_rate", "aggregate_rate"):
                    text = self.vars[key].get().strip()
                    if text:
                        value = float(text)
                        if previous == "m³" and unit == "Cft":
                            value = UnitQuantityService.rate_for_quantity_unit(
                                value, "m³", "Cft"
                            )
                        elif previous == "Cft" and unit == "m³":
                            value = UnitQuantityService.rate_for_quantity_unit(
                                value, "Cft", "m³"
                            )
                        self.vars[key].set(
                            f"{value:.4f}".rstrip("0").rstrip(".")
                        )

                # Productivity is quantity/day, therefore it follows
                # the quantity conversion direction.
                productivity_factor = (
                    35.3146667215 if unit == "Cft"
                    else 0.028316846592
                )
                for key in ("skilled_productivity", "unskilled_productivity"):
                    text = self.vars[key].get().strip()
                    if text:
                        value = float(text) * productivity_factor
                        self.vars[key].set(
                            f"{value:.4f}".rstrip("0").rstrip(".")
                        )

            except (ValueError, TypeError):
                # Empty fields are valid while editing the form.
                pass

        self._last_unit = unit
        dimension_unit = "m" if unit == "m³" else "ft"

        self.l_lbl.configure(text=f"Length ({dimension_unit})")
        self.w_lbl.configure(text=f"Width ({dimension_unit})")
        self.h_lbl.configure(
            text=f"Thickness / Height ({dimension_unit})"
        )
        self.sp_lbl.configure(
            text=f"Skilled productivity ({unit} / day)"
        )
        self.up_lbl.configure(
            text=f"Unskilled productivity ({unit} / day)"
        )

        # Keep the rate labels synchronized with the selected denominator.
        # This avoids a hidden PKR/m³ vs PKR/Cft mismatch.
        # Locate labels through the existing form structure only when
        # available; no new widgets are required.
        if hasattr(self, "sand_rate_label"):
            self.sand_rate_label.configure(
                text=f"Sand (PKR / {unit})"
            )
        if hasattr(self, "aggregate_rate_label"):
            self.aggregate_rate_label.configure(
                text=f"Aggregate (PKR / {unit})"
            )

    def _num(self,k,label,pos=False):
        try:v=float(self.vars[k].get())
        except ValueError as e: raise ValueError(f"{label} must be a valid number.") from e
        if pos and v<=0: raise ValueError(f"{label} must be greater than zero.")
        if not pos and v<0: raise ValueError(f"{label} cannot be negative.")
        return v
    def calculate(self):
        try:
            self.result=CalculatorFactory.create("RCC",length=self._num("length","Length",True),width=self._num("width","Width",True),height=self._num("height","Height",True),mix_ratio=self.vars["mix_ratio"].get(),steel_kg=self._num("steel_kg","Steel"),binding_wire_percent=self._num("binding_wire_percent","Binding wire"),formwork=self._num("formwork","Formwork"),volume_unit=self.vars["volume_unit"].get()).calculate()
            self.analysis=self._analysis();self._show();self.status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as e: messagebox.showerror("RCC Calculation Error",str(e),parent=self)
    def _analysis(self):
        q=float(self.result.quantity);u=self.vars["volume_unit"].get()
        sp=self._num("skilled_productivity","Skilled productivity",True);up=self._num("unskilled_productivity","Unskilled productivity",True)
        def rate(k,l): return self._num(k,l)
        return RCCEstimateService.build_analysis(self.result,{
            "cement_bag":rate("cement_rate","Cement rate"),"sand":rate("sand_rate","Sand rate"),
            "aggregate":rate("aggregate_rate","Aggregate rate"),"steel_kg":rate("steel_rate","Steel rate"),
            "binding_wire_kg":rate("binding_rate","Binding wire rate"),"formwork":rate("formwork_rate","Formwork rate")},
            q/sp,self._num("skilled_rate","Skilled labour rate"),q/up,self._num("unskilled_rate","Unskilled labour rate"))
    def _ready(self):
        for w in self.result_frame.winfo_children():w.destroy()
        self._section(self.result_frame,"Calculation Result",0)
        ctk.CTkLabel(self.result_frame,text="Enter RCC dimensions, reinforcement, formwork, material rates and labour norms, then Calculate.",wraplength=520,justify="left").grid(row=1,column=0,columnspan=2,padx=14,pady=12,sticky="ew")
    def _show(self):
        for w in self.result_frame.winfo_children():w.destroy()
        a=self.analysis;r=0
        self._section(self.result_frame,"Concrete Quantity",r);r+=1
        rows=[("Working Unit", a["unit"]),
              ("Dimensions",f"L={a['dimensions']['length']:.3f} × W={a['dimensions']['width']:.3f} × T={a['dimensions']['height']:.3f} {a['dimensions']['dimension_unit']}"),
              ("Mix Ratio",a["mix_ratio"]),("Wet Concrete",f"{a['quantity']:.3f} {a['unit']}"),("Dry Volume",f"{a['dry_volume']:.3f} m³"),
              ("Cement",f"{self.result.cement_bags:.3f} Bags"),("Sand",f"{self.result.sand_volume:.3f} {a['unit']}"),("Aggregate",f"{self.result.aggregate_volume:.3f} {a['unit']}"),
              ("Steel",f"{a['steel_kg']:.2f} kg"),("Binding Wire",f"{a['binding_wire_kg']:.2f} kg"),("Formwork",f"{a['formwork']['quantity']:.3f} m²")]
        r=self._rows(rows,r)
        self._section(self.result_frame,"Material / Formwork Cost",r);r+=1
        r=self._rows([(x["name"],f"{x['quantity']:,.3f} {x['unit']} × PKR {x['rate']:,.2f} = PKR {x['amount']:,.2f}") for x in a["materials"]]+[(a["formwork"]["name"],f"{a['formwork']['quantity']:,.3f} m² × PKR {a['formwork']['rate']:,.2f} = PKR {a['formwork']['amount']:,.2f}")],r)
        r=self._rows([("Material/Formwork Total",f"PKR {a['material_total']:,.2f}")],r,True)
        self._section(self.result_frame,"Labour Cost",r);r+=1
        r=self._rows([(x["name"],f"{x['quantity']:,.2f} day × PKR {x['rate']:,.2f} = PKR {x['amount']:,.2f}") for x in a["labour"]],r)
        r=self._rows([("Labour Total",f"PKR {a['labour_total']:,.2f}")],r,True)
        self._section(self.result_frame,"Final Cost",r);r+=1
        self._rows([("Total Cost",f"PKR {a['total_cost']:,.2f}"),("Unit Rate",f"PKR {a['unit_rate']:,.2f} / {a['unit']}")],r,True)
    def _rows(self,rows,start,bold=False):
        f=ctk.CTkFont(weight="bold") if bold else None
        for label,value in rows:
            ctk.CTkLabel(self.result_frame,text=label,anchor="w",font=f).grid(row=start,column=0,padx=(14,10),pady=5,sticky="w")
            ctk.CTkLabel(self.result_frame,text=value,anchor="w",font=f).grid(row=start,column=1,padx=(10,14),pady=5,sticky="ew");start+=1
        return start
    def generate_boq(self):
        if self.result is None: messagebox.showwarning("RCC → BOQ","Please calculate RCC first.",parent=self);return
        try:
            self.analysis=self._analysis();project=CurrentProject.get()
            if project is None or getattr(project,"id",None) is None: raise ValueError("Please select/open a project before generating BOQ.")
            context=self.application_context
            if context is None: raise ValueError("Application context is not available.")
            items=context.boq_controller.get_by_project(project.id) or [];highest=0
            for item in items:
                no=str(getattr(item,"item_no","")).upper()
                if no.startswith("RCC-"):
                    try: highest=max(highest,int(no.split("-",1)[1]))
                    except (ValueError,IndexError): pass
            no=f"RCC-{highest+1:02d}";d=self.analysis["dimensions"]
            remarks=(f"Detailed RCC analysis | L={d['length']:.3f} {d['dimension_unit']}, W={d['width']:.3f} {d['dimension_unit']}, T={d['height']:.3f} {d['dimension_unit']} | Mix={self.analysis['mix_ratio']} | Steel={self.analysis['steel_kg']:.2f} kg | Formwork={self.analysis['formwork']['quantity']:.3f} m²")
            boq=BOQ(project_id=project.id,item_no=no,description=f"RCC ({self.analysis['mix_ratio']})",unit=self.analysis["unit"],quantity=self.analysis["quantity"],rate=self.analysis["unit_rate"],amount=self.analysis["total_cost"],remarks=remarks)
            bid=context.boq_controller.create(boq)
            context.estimate_analysis_service.save(project_id=project.id,boq_id=int(bid),calculator_type="RCC",analysis=self.analysis)
            self.status.configure(text=f"BOQ {no} added successfully")
            messagebox.showinfo("RCC → BOQ",f"BOQ item {no} created successfully.\n\nConcrete: {self.analysis['quantity']:,.3f} {self.analysis['unit']}\nCement: {self.result.cement_bags:,.2f} Bags\nSand: {self.result.sand_volume:,.3f} {self.analysis['unit']}\nAggregate: {self.result.aggregate_volume:,.3f} {self.analysis['unit']}\nSteel: {self.analysis['steel_kg']:,.2f} kg",parent=self)
        except Exception as e: messagebox.showerror("RCC → BOQ Error",str(e),parent=self)
    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("RCC Material", "Please calculate rcc first.", parent=self)
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
                "RCC Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("RCC Material Error", str(ex), parent=self)
    def reset_form(self):
        vals={"volume_unit":"m³","length":"","width":"","height":"","mix_ratio":"1:2:4","steel_kg":"0","binding_wire_percent":"2","formwork":"0","cement_rate":"0","sand_rate":"0","aggregate_rate":"0","steel_rate":"0","binding_rate":"0","formwork_rate":"0","skilled_productivity":"1","skilled_rate":"0","unskilled_productivity":"2","unskilled_rate":"0"}
        for k,v in vals.items():self.vars[k].set(v)
        self._last_unit="m³";self._unit();self.result=None;self.analysis=None;self.status.configure(text="Ready");self._ready()
    def has_result(self): return self.result is not None
