from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox

class SettingsPage(ctk.CTkFrame):
    """Professional application and estimation settings."""

    def __init__(self, master, context, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.context=context
        self.settings=getattr(context,"settings",None)
        if self.settings is None:
            from config.setting import Settings
            self.settings=Settings()
            context.settings=self.settings
        self.vars={}
        self._build()
        self.refresh()

    def _build(self):
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(1,weight=1)
        header=ctk.CTkFrame(self,fg_color="transparent")
        header.grid(row=0,column=0,sticky="ew",padx=20,pady=(18,8)); header.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(header,text="Settings",font=ctk.CTkFont(size=26,weight="bold")).grid(row=0,column=0,sticky="w")
        ctk.CTkLabel(header,text="Configure application, estimation defaults, units and reports.",font=ctk.CTkFont(size=13)).grid(row=1,column=0,sticky="w",pady=(3,0))
        self.body=ctk.CTkScrollableFrame(self,corner_radius=10)
        self.body.grid(row=1,column=0,sticky="nsew",padx=20,pady=(0,10))
        self.body.grid_columnconfigure((0,1),weight=1)
        self._application(); self._estimation(); self._labour_norms(); self._reports(); self._database(); self._actions()

    def _section(self,title,row):
        f=ctk.CTkFrame(self.body); f.grid(row=row,column=0,columnspan=2,sticky="ew",padx=5,pady=(8,5))
        f.grid_columnconfigure((1,3),weight=1)
        ctk.CTkLabel(f,text=title,font=ctk.CTkFont(size=18,weight="bold")).grid(row=0,column=0,columnspan=4,sticky="w",padx=14,pady=(10,8))
        return f

    def _field(self,parent,row,col,label,key,values=None):
        box=ctk.CTkFrame(parent,fg_color="transparent"); box.grid(row=row,column=col,sticky="ew",padx=10,pady=6); box.grid_columnconfigure(1,weight=1)
        ctk.CTkLabel(box,text=label,anchor="w").grid(row=0,column=0,sticky="w",padx=(0,8))
        var=ctk.StringVar(); self.vars[key]=var
        widget=ctk.CTkComboBox(box,variable=var,values=values) if values else ctk.CTkEntry(box,textvariable=var)
        widget.grid(row=0,column=1,sticky="ew"); return var

    def _application(self):
        f=self._section("1. Application",0)
        self._field(f,1,0,"Software Name","app_name"); self._field(f,1,1,"Version","version")
        self._field(f,2,0,"Appearance","appearance",["System","Light","Dark"]); self._field(f,2,1,"Theme","theme",["blue","green","dark-blue"])
        self._field(f,3,0,"Window Width","window_width"); self._field(f,3,1,"Window Height","window_height")
        self._field(f,4,0,"Remember Window Size","remember_window_size",["Yes","No"])

    def _estimation(self):
        f=self._section("2. Estimation Defaults",1)
        fields=[
            ("Currency","currency",["PKR","USD","AED"]),
            ("Decimal Places","decimal_places",None),
            ("Length Unit","length_unit",["m","ft"]),
            ("Area Unit","area_unit",["m²","sqft"]),
            ("Volume Unit","volume_unit",["m³","Cft"]),
            ("Steel Unit","steel_unit",["kg","ton"]),
            ("Default Concrete Mix","default_concrete_mix",["1:2:4","1:1.5:3","1:3:6"]),
            ("Cement Rate (PKR/bag)","cement_rate",None),
            ("Sand Rate (PKR/m³)","sand_rate",None),
            ("Aggregate Rate (PKR/m³)","aggregate_rate",None),
            ("Steel Rate (PKR/kg)","steel_rate",None),
            ("Skilled Labour (PKR/day)","skilled_labour_rate",None),
            ("Unskilled Labour (PKR/day)","unskilled_labour_rate",None),
        ]
        for i,(label,key,vals) in enumerate(fields):
            self._field(f,1+i//2,i%2,label,key,vals)

    def _labour_norms(self):
        f=self._section("3. Labour Productivity Norms",2)
        fields=[
            ("PCC Skilled (m³/day)","pcc_skilled_productivity"),
            ("PCC Unskilled (m³/day)","pcc_unskilled_productivity"),
            ("RCC Skilled (m³/day)","rcc_skilled_productivity"),
            ("RCC Unskilled (m³/day)","rcc_unskilled_productivity"),
            ("Brickwork Skilled (m³/day)","brickwork_skilled_productivity"),
            ("Brickwork Unskilled (m³/day)","brickwork_unskilled_productivity"),
            ("Plaster Skilled (m²/day)","plaster_skilled_productivity"),
            ("Plaster Unskilled (m²/day)","plaster_unskilled_productivity"),
            ("Excavation Skilled (m³/day)","excavation_skilled_productivity"),
            ("Excavation Unskilled (m³/day)","excavation_unskilled_productivity"),
            ("Footing Skilled (m³/day)","footing_skilled_productivity"),
            ("Footing Unskilled (m³/day)","footing_unskilled_productivity"),
            ("Staircase Skilled (m³/day)","staircase_skilled_productivity"),
            ("Staircase Unskilled (m³/day)","staircase_unskilled_productivity"),
        ]
        for i,(label,key) in enumerate(fields):
            self._field(f,1+i//2,i%2,label,key)

        ctk.CTkLabel(
            f,
            text="Productivity = completed quantity per labour day. "
                 "Steel productivity remains calculator/company specific.",
            anchor="w",
            wraplength=900,
        ).grid(row=8,column=0,columnspan=4,sticky="w",padx=14,pady=(6,12))

    def _reports(self):
        f=self._section("4. Reports & BOQ",3)
        fields=[
            ("Default Export Format","default_export_format",["xlsx","pdf","both"]),
            ("Export Folder","export_folder",None),
            ("Include Remarks","include_remarks",["Yes","No"]),
            ("Material Breakdown","include_material_breakdown",["Yes","No"]),
            ("Labour Breakdown","include_labour_breakdown",["Yes","No"]),
        ]
        for i,(label,key,vals) in enumerate(fields): self._field(f,1+i//2,i%2,label,key,vals)

    def _database(self):
        f=self._section("5. Database & Backup",4)
        self._field(f,1,0,"Automatic Backup","auto_backup",["Yes","No"])
        self._field(f,1,1,"Backup Interval (days)","backup_interval_days")

    def _actions(self):
        f=ctk.CTkFrame(self,fg_color="transparent"); f.grid(row=2,column=0,sticky="ew",padx=20,pady=(0,18))
        ctk.CTkButton(f,text="Save Settings",width=150,height=40,command=self.save_settings).pack(side="left",padx=(0,8))
        ctk.CTkButton(f,text="Reset Defaults",width=150,height=40,command=self.reset_settings).pack(side="left",padx=8)
        self.status=ctk.CTkLabel(f,text="Ready",anchor="w"); self.status.pack(side="left",padx=15)

    @staticmethod
    def _yn(v): return "Yes" if bool(v) else "No"

    def refresh(self):
        a=self.settings.get("application",{}); e=self.settings.get("estimation",{}); r=self.settings.get("reports",{}); d=self.settings.get("database",{})
        vals={
            "app_name":getattr(self.context,"application_name","Civil Estimate Suite Pro"),
            "version":getattr(self.context,"version","4.0"),
            "appearance":str(a.get("appearance","light")).title(),
            "theme":str(a.get("theme","blue")),
            "window_width":str(a.get("window_width",1400)),
            "window_height":str(a.get("window_height",850)),
            "remember_window_size":self._yn(a.get("remember_window_size",True)),
            "currency":str(e.get("currency","PKR")),
            "decimal_places":str(e.get("decimal_places",2)),
            "length_unit":str(e.get("length_unit","m")),
            "area_unit":str(e.get("area_unit","m²")),
            "volume_unit":str(e.get("volume_unit","m³")),
            "steel_unit":str(e.get("steel_unit","kg")),
            "default_concrete_mix":str(e.get("default_concrete_mix","1:2:4")),
            "cement_rate":str(e.get("cement_rate",1650)),
            "sand_rate":str(e.get("sand_rate",800)),
            "aggregate_rate":str(e.get("aggregate_rate",1000)),
            "steel_rate":str(e.get("steel_rate",280)),
            "skilled_labour_rate":str(e.get("skilled_labour_rate",2500)),
            "unskilled_labour_rate":str(e.get("unskilled_labour_rate",1250)),
            "pcc_skilled_productivity":str(e.get("pcc_skilled_productivity",1.0)),
            "pcc_unskilled_productivity":str(e.get("pcc_unskilled_productivity",2.0)),
            "rcc_skilled_productivity":str(e.get("rcc_skilled_productivity",1.0)),
            "rcc_unskilled_productivity":str(e.get("rcc_unskilled_productivity",2.0)),
            "brickwork_skilled_productivity":str(e.get("brickwork_skilled_productivity",10.0)),
            "brickwork_unskilled_productivity":str(e.get("brickwork_unskilled_productivity",15.0)),
            "plaster_skilled_productivity":str(e.get("plaster_skilled_productivity",10.0)),
            "plaster_unskilled_productivity":str(e.get("plaster_unskilled_productivity",15.0)),
            "excavation_skilled_productivity":str(e.get("excavation_skilled_productivity",8.0)),
            "excavation_unskilled_productivity":str(e.get("excavation_unskilled_productivity",6.0)),
            "footing_skilled_productivity":str(e.get("footing_skilled_productivity",1.0)),
            "footing_unskilled_productivity":str(e.get("footing_unskilled_productivity",2.0)),
            "staircase_skilled_productivity":str(e.get("staircase_skilled_productivity",1.0)),
            "staircase_unskilled_productivity":str(e.get("staircase_unskilled_productivity",2.0)),
            "default_export_format":str(r.get("default_export_format","xlsx")),
            "export_folder":str(r.get("export_folder","exports")),
            "include_remarks":self._yn(r.get("include_remarks",True)),
            "include_material_breakdown":self._yn(r.get("include_material_breakdown",True)),
            "include_labour_breakdown":self._yn(r.get("include_labour_breakdown",True)),
            "auto_backup":self._yn(d.get("auto_backup",True)),
            "backup_interval_days":str(d.get("backup_interval_days",7)),
        }
        for k,v in vals.items(): self.vars[k].set(v)
        self.status.configure(text="Settings loaded")

    @staticmethod
    def _num(v,label,minv=0,integer=False):
        try: x=int(v) if integer else float(v)
        except (TypeError,ValueError): raise ValueError(f"{label} must be a valid {'whole number' if integer else 'number'}.")
        if x<minv: raise ValueError(f"{label} must be at least {minv}.")
        return x

    def save_settings(self):
        try:
            self.settings.update("application",{
                "appearance":self.vars["appearance"].get().lower(),"theme":self.vars["theme"].get(),
                "window_width":self._num(self.vars["window_width"].get(),"Window width",800,True),
                "window_height":self._num(self.vars["window_height"].get(),"Window height",600,True),
                "remember_window_size":self.vars["remember_window_size"].get()=="Yes"})
            self.settings.update("estimation",{
                "currency":self.vars["currency"].get(),"decimal_places":self._num(self.vars["decimal_places"].get(),"Decimal places",0,True),
                "length_unit":self.vars["length_unit"].get(),"area_unit":self.vars["area_unit"].get(),"volume_unit":self.vars["volume_unit"].get(),"steel_unit":self.vars["steel_unit"].get(),
                "default_concrete_mix":self.vars["default_concrete_mix"].get(),
                "cement_rate":self._num(self.vars["cement_rate"].get(),"Cement rate"),"sand_rate":self._num(self.vars["sand_rate"].get(),"Sand rate"),
                "aggregate_rate":self._num(self.vars["aggregate_rate"].get(),"Aggregate rate"),"steel_rate":self._num(self.vars["steel_rate"].get(),"Steel rate"),
                "skilled_labour_rate":self._num(self.vars["skilled_labour_rate"].get(),"Skilled labour rate"),
                "unskilled_labour_rate":self._num(self.vars["unskilled_labour_rate"].get(),"Unskilled labour rate"),
                "pcc_skilled_productivity":self._num(self.vars["pcc_skilled_productivity"].get(),"PCC skilled productivity"),
                "pcc_unskilled_productivity":self._num(self.vars["pcc_unskilled_productivity"].get(),"PCC unskilled productivity"),
                "rcc_skilled_productivity":self._num(self.vars["rcc_skilled_productivity"].get(),"RCC skilled productivity"),
                "rcc_unskilled_productivity":self._num(self.vars["rcc_unskilled_productivity"].get(),"RCC unskilled productivity"),
                "brickwork_skilled_productivity":self._num(self.vars["brickwork_skilled_productivity"].get(),"Brickwork skilled productivity"),
                "brickwork_unskilled_productivity":self._num(self.vars["brickwork_unskilled_productivity"].get(),"Brickwork unskilled productivity"),
                "plaster_skilled_productivity":self._num(self.vars["plaster_skilled_productivity"].get(),"Plaster skilled productivity"),
                "plaster_unskilled_productivity":self._num(self.vars["plaster_unskilled_productivity"].get(),"Plaster unskilled productivity"),
                "excavation_skilled_productivity":self._num(self.vars["excavation_skilled_productivity"].get(),"Excavation skilled productivity"),
                "excavation_unskilled_productivity":self._num(self.vars["excavation_unskilled_productivity"].get(),"Excavation unskilled productivity"),
                "footing_skilled_productivity":self._num(self.vars["footing_skilled_productivity"].get(),"Footing skilled productivity"),
                "footing_unskilled_productivity":self._num(self.vars["footing_unskilled_productivity"].get(),"Footing unskilled productivity"),
                "staircase_skilled_productivity":self._num(self.vars["staircase_skilled_productivity"].get(),"Staircase skilled productivity"),
                "staircase_unskilled_productivity":self._num(self.vars["staircase_unskilled_productivity"].get(),"Staircase unskilled productivity")})
            self.settings.update("reports",{
                "default_export_format":self.vars["default_export_format"].get(),"export_folder":self.vars["export_folder"].get() or "exports",
                "include_remarks":self.vars["include_remarks"].get()=="Yes","include_material_breakdown":self.vars["include_material_breakdown"].get()=="Yes","include_labour_breakdown":self.vars["include_labour_breakdown"].get()=="Yes"})
            self.settings.update("database",{"auto_backup":self.vars["auto_backup"].get()=="Yes","backup_interval_days":self._num(self.vars["backup_interval_days"].get(),"Backup interval",1,True)})
            self.settings.save()
            try:
                ctk.set_appearance_mode(self.vars["appearance"].get())
                ctk.set_default_color_theme(self.vars["theme"].get())
            except Exception: pass
            self.status.configure(text="Settings saved successfully")
            messagebox.showinfo("Settings","Settings saved successfully.",parent=self)
        except Exception as ex: messagebox.showerror("Settings Error",str(ex),parent=self)

    def reset_settings(self):
        if not messagebox.askyesno("Reset Settings","Restore all settings to defaults?",parent=self): return
        self.settings.reset(); self.refresh(); self.status.configure(text="Default settings restored")

    def has_changes(self): return False

__all__=["SettingsPage"]
