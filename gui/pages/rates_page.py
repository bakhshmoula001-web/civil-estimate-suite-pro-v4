from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox
from core.current_project import CurrentProject

class RatesPage(ctk.CTkFrame):
    DEFAULTS=[
        ("Material","Cement","Bag",1650.0),
        ("Material","Sand","Cft",80.0),
        ("Material","Coarse Aggregate","Cft",90.0),
        ("Material","Steel","kg",280.0),
        ("Labour","Skilled Labour","day",2500.0),
        ("Labour","Unskilled Labour","day",1250.0),
    ]
    def __init__(self,master,context,**kwargs):
        super().__init__(master,corner_radius=0,**kwargs)
        self.context=context; self.controller=context.rate_controller; self.rows=[]
        self._build(); self.refresh()
    def _build(self):
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(2,weight=1)
        h=ctk.CTkFrame(self,fg_color="transparent"); h.grid(row=0,column=0,sticky="ew",padx=20,pady=(18,8)); h.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(h,text="Project Rate Database",font=ctk.CTkFont(size=26,weight="bold")).grid(row=0,column=0,sticky="w")
        ctk.CTkLabel(h,text="Manage project-wise material and labour rates used by estimation.",font=ctk.CTkFont(size=13)).grid(row=1,column=0,sticky="w",pady=(3,0))
        bar=ctk.CTkFrame(self); bar.grid(row=1,column=0,sticky="ew",padx=20,pady=(0,8))
        self.project_label=ctk.CTkLabel(bar,text="Project: —"); self.project_label.pack(side="left",padx=12)
        ctk.CTkButton(bar,text="Seed Defaults",width=120,command=self.seed_defaults).pack(side="right",padx=5,pady=6)
        ctk.CTkButton(bar,text="Save Rates",width=120,command=self.save_rates).pack(side="right",padx=5,pady=6)
        ctk.CTkButton(bar,text="Refresh",width=100,command=self.refresh).pack(side="right",padx=5,pady=6)
        self.table=ctk.CTkScrollableFrame(self,corner_radius=10); self.table.grid(row=2,column=0,sticky="nsew",padx=20,pady=(0,12))
        for col,w in enumerate((1,2,1,1,1)): self.table.grid_columnconfigure(col,weight=w)
        for col,title in enumerate(("Category","Item","Unit","Rate","Source")):
            ctk.CTkLabel(self.table,text=title,font=ctk.CTkFont(size=13,weight="bold")).grid(row=0,column=col,sticky="ew",padx=8,pady=8)
        self.status=ctk.CTkLabel(self,text="Ready",anchor="w"); self.status.grid(row=3,column=0,sticky="ew",padx=20,pady=(0,12))
    def _project(self):
        p=CurrentProject.get()
        if p is None: messagebox.showwarning("Rates","Please select a project first.",parent=self)
        return p
    def _clear(self):
        for widgets,_,_ in self.rows:
            for w in widgets: w.destroy()
        self.rows=[]
    def refresh(self):
        self._clear(); p=CurrentProject.get()
        if p is None: self.project_label.configure(text="Project: —"); self.status.configure(text="Select a project first."); return
        self.project_label.configure(text=f"Project: {p.project_code} — {p.project_name}")
        items=self.controller.get_by_project(p.id)
        for r,item in enumerate(items,1): self._add_row(r,item.category,item.item_name,item.unit,item.rate,item.source,item.id)
        self.status.configure(text=f"{len(items)} rate item(s) loaded.")
    def _add_row(self,row,category,name,unit,rate,source,item_id=None):
        vars_=[ctk.StringVar(master=self.table, value=str(x)) for x in (category,name,unit,rate,source)]; widgets=[]
        for col,var in enumerate(vars_):
            w=ctk.CTkEntry(self.table,textvariable=var); w.grid(row=row,column=col,sticky="ew",padx=6,pady=4); widgets.append(w)
        self.rows.append((widgets,vars_,item_id))
    def seed_defaults(self):
        p=self._project()
        if p is None:return
        try:
            self.controller.seed_defaults(p.id,[{"category":c,"item_name":n,"unit":u,"rate":r} for c,n,u,r in self.DEFAULTS])
            self.refresh(); self.status.configure(text="Default project rates created/updated.")
        except Exception as ex: messagebox.showerror("Rates",str(ex),parent=self)
    def save_rates(self):
        p=self._project()
        if p is None:return
        try:
            for _,vars_,_ in self.rows:
                category,name,unit,rate,source=[v.get().strip() for v in vars_]
                if not name or not unit: raise ValueError("Item name and unit are required.")
                rate=float(rate)
                if rate<0: raise ValueError(f"Rate cannot be negative: {name}")
                self.controller.save(p.id,category,name,unit,rate,source or "Project")
            self.refresh(); self.status.configure(text="Rates saved successfully.")
        except Exception as ex: messagebox.showerror("Rate Save Error",str(ex),parent=self)

__all__=["RatesPage"]
