"""ResQGrid — Disaster Resource Allocator.
Run in Python IDLE with F5. Standard-library-only Tkinter prototype.
Demo data only; not connected to live emergency services or geographic data.
"""
import json, os, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from uuid import uuid4

FILE = "resqgrid_data.json"
AREAS = ["North Zone", "South Zone", "East Zone", "West Zone", "Central Zone"]
DISASTERS = ["Flood", "Cyclone", "Earthquake", "Fire", "Landslide", "Other"]
SEVERITIES = ["Critical", "High", "Medium", "Low"]
TYPES = ["Food", "Drinking Water", "Medicine", "First Aid Kits", "Blankets",
         "Rescue Boats", "Medical Teams", "Shelter Kits", "Power Generators", "Other"]
STATUSES = ["Open", "In Progress", "Fulfilled"]

def stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def ident():
    return str(uuid4())[:8]

def demo():
    return {
        "incidents": [
            dict(id=ident(), area="North Zone", disaster="Flood", severity="Critical", people=420,
                 notes="Water rising near homes", status="Open", created=stamp()),
            dict(id=ident(), area="East Zone", disaster="Cyclone", severity="High", people=180,
                 notes="Temporary shelter support", status="In Progress", created=stamp()),
            dict(id=ident(), area="South Zone", disaster="Fire", severity="Medium", people=65,
                 notes="Families need basic supplies", status="Open", created=stamp())],
        "resources": [
            dict(id=ident(), area="Central Zone", type="Drinking Water", quantity=600, available=600, unit="litres", notes="Warehouse A"),
            dict(id=ident(), area="West Zone", type="Food", quantity=350, available=350, unit="meal packs", notes="Community kitchen"),
            dict(id=ident(), area="North Zone", type="Blankets", quantity=120, available=120, unit="pieces", notes="Relief centre"),
            dict(id=ident(), area="South Zone", type="First Aid Kits", quantity=45, available=45, unit="kits", notes="Clinic store"),
            dict(id=ident(), area="East Zone", type="Medical Teams", quantity=8, available=8, unit="teams", notes="Regional hospital")],
        "allocations": [],
        "activity": [dict(time=stamp(), message="ResQGrid demo data initialized.")]
    }

class ResQGrid:
    def __init__(self, root):
        self.root = root
        root.title("ResQGrid — Disaster Resource Allocator")
        root.geometry("1160x740")
        root.minsize(950, 620)
        self.data = self.load()
        self.style = ttk.Style()
        try: self.style.theme_use("clam")
        except tk.TclError: pass
        root.configure(bg="#edf3f8")
        self.style.configure("TFrame", background="#edf3f8")
        self.style.configure("Panel.TFrame", background="white")
        self.style.configure("TLabel", background="#edf3f8", foreground="#183451", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#125174")
        self.style.configure("Panel.TLabel", background="white", font=("Segoe UI", 11, "bold"))
        self.style.configure("Metric.TLabel", background="white", font=("Segoe UI", 22, "bold"), foreground="#087e8b")
        self.style.configure("TButton", padding=6)
        self.style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        head = ttk.Frame(root, padding=(18, 12))
        head.pack(fill="x")
        ttk.Label(head, text="ResQGrid", style="Title.TLabel").pack(anchor="w")
        ttk.Label(head, text="Disaster Resource Allocation & Relief Coordination").pack(anchor="w")
        ttk.Button(head, text="Export JSON", command=self.export).pack(side="right", anchor="e")
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.dashboard = ttk.Frame(self.tabs, padding=12)
        self.incident_tab = ttk.Frame(self.tabs, padding=12)
        self.resource_tab = ttk.Frame(self.tabs, padding=12)
        self.match_tab = ttk.Frame(self.tabs, padding=12)
        self.allocation_tab = ttk.Frame(self.tabs, padding=12)
        self.log_tab = ttk.Frame(self.tabs, padding=12)
        for frame, name in [(self.dashboard,"Dashboard"),(self.incident_tab,"Incidents"),
                            (self.resource_tab,"Resources"),(self.match_tab,"Smart Allocation"),
                            (self.allocation_tab,"Allocations"),(self.log_tab,"Activity Log")]:
            self.tabs.add(frame, text=name)
        self.build_dashboard()
        self.build_incidents()
        self.build_resources()
        self.build_match()
        self.build_allocations()
        self.build_log()
        ttk.Label(root, text="Educational prototype • Fictional sample data • Not for real emergency dispatch",
                  foreground="#8b4b16", font=("Segoe UI", 9, "bold")).pack(pady=(0, 7))
        self.refresh()

    def load(self):
        if os.path.exists(FILE):
            try:
                with open(FILE, encoding="utf-8") as f:
                    d = json.load(f)
                for k in ("incidents","resources","allocations","activity"): d.setdefault(k, [])
                return d
            except (OSError, json.JSONDecodeError):
                messagebox.showwarning("Data", "Data file could not be read; starting with demo data.")
        return demo()

    def save(self):
        try:
            with open(FILE, "w", encoding="utf-8") as f: json.dump(self.data, f, indent=2)
        except OSError as e: messagebox.showerror("Save error", str(e))

    def log(self, text):
        self.data["activity"].insert(0, {"time":stamp(), "message":text})
        self.data["activity"] = self.data["activity"][:300]
        self.save()

    def tree(self, parent, columns, headings, height=13):
        box = ttk.Frame(parent); box.pack(fill="both", expand=True)
        t = ttk.Treeview(box, columns=columns, show="headings", height=height, selectmode="browse")
        sy = ttk.Scrollbar(box, orient="vertical", command=t.yview)
        sx = ttk.Scrollbar(box, orient="horizontal", command=t.xview)
        t.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        for c,h in zip(columns,headings):
            t.heading(c,text=h); t.column(c,width=120,minwidth=65,anchor="w")
        t.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
        box.rowconfigure(0,weight=1); box.columnconfigure(0,weight=1)
        return t

    def clear(self, tree):
        for item in tree.get_children(): tree.delete(item)

    def build_dashboard(self):
        cards = ttk.Frame(self.dashboard); cards.pack(fill="x", pady=(0,12))
        self.metrics = {}
        for key,label in [("inc","Incidents"),("critical","Critical"),("people","People affected"),
                          ("stock","Available stock units"),("done","Fulfilled allocations")]:
            c=ttk.Frame(cards,style="Panel.TFrame",padding=12); c.pack(side="left",fill="both",expand=True,padx=4)
            v=ttk.Label(c,text="0",style="Metric.TLabel"); v.pack(anchor="w")
            ttk.Label(c,text=label,style="Panel.TLabel").pack(anchor="w",pady=(4,0))
            self.metrics[key]=v
        lower=ttk.Frame(self.dashboard); lower.pack(fill="both",expand=True)
        left=ttk.Frame(lower,style="Panel.TFrame",padding=10); left.pack(side="left",fill="both",expand=True,padx=(0,5))
        right=ttk.Frame(lower,style="Panel.TFrame",padding=10); right.pack(side="left",fill="both",expand=True,padx=(5,0))
        ttk.Label(left,text="Reported incidents",style="Panel.TLabel").pack(anchor="w",pady=(0,8))
        ttk.Label(right,text="Available resources",style="Panel.TLabel").pack(anchor="w",pady=(0,8))
        self.dash_i=self.tree(left,("area","disaster","severity","people","status"),("Area","Disaster","Severity","People","Status"),10)
        self.dash_r=self.tree(right,("type","available","unit","area"),("Resource","Available","Unit","Location"),10)

    def build_incidents(self):
        bar=ttk.Frame(self.incident_tab); bar.pack(fill="x",pady=(0,9))
        ttk.Button(bar,text="+ Add Incident",command=self.add_incident).pack(side="left")
        ttk.Button(bar,text="Change Status",command=self.change_incident).pack(side="left",padx=6)
        ttk.Button(bar,text="Delete Selected",command=self.delete_incident).pack(side="left")
        self.it=self.tree(self.incident_tab,("id","area","disaster","severity","people","status","created","notes"),
                          ("ID","Area","Disaster","Severity","People","Status","Reported","Notes"),15)
        self.it.column("notes",width=230)

    def build_resources(self):
        bar=ttk.Frame(self.resource_tab); bar.pack(fill="x",pady=(0,9))
        ttk.Button(bar,text="+ Add Resource Stock",command=self.add_resource).pack(side="left")
        ttk.Button(bar,text="Edit Available Qty",command=self.edit_resource).pack(side="left",padx=6)
        ttk.Button(bar,text="Delete Selected",command=self.delete_resource).pack(side="left")
        self.rt=self.tree(self.resource_tab,("id","type","area","quantity","available","unit","notes"),
                          ("ID","Resource","Location","Initial Qty","Available","Unit","Storage / Notes"),15)
        self.rt.column("notes",width=220)

    def build_match(self):
        ttk.Label(self.match_tab,text="Choose an incident, resource type and quantity. Recommendations are rule-based, not trained AI.",
                  wraplength=900).pack(anchor="w",pady=(0,12))
        form=ttk.Frame(self.match_tab); form.pack(fill="x",pady=(0,10))
        self.inc_var=tk.StringVar(); self.inc_combo=ttk.Combobox(form,textvariable=self.inc_var,state="readonly",width=54)
        self.typ_var=tk.StringVar(value="Food"); self.typ_combo=ttk.Combobox(form,textvariable=self.typ_var,values=TYPES,state="readonly",width=25)
        self.qty_var=tk.StringVar(value="50")
        ttk.Label(form,text="Incident").grid(row=0,column=0,sticky="w",padx=5,pady=5); self.inc_combo.grid(row=0,column=1,sticky="w",pady=5)
        ttk.Label(form,text="Resource type").grid(row=1,column=0,sticky="w",padx=5,pady=5); self.typ_combo.grid(row=1,column=1,sticky="w",pady=5)
        ttk.Label(form,text="Quantity").grid(row=2,column=0,sticky="w",padx=5,pady=5); ttk.Entry(form,textvariable=self.qty_var,width=28).grid(row=2,column=1,sticky="w",pady=5)
        ttk.Button(form,text="Find Best Matches",command=self.find_matches).grid(row=0,column=2,rowspan=2,padx=14)
        ttk.Button(form,text="Allocate Selected Match",command=self.allocate).grid(row=2,column=2,padx=14)
        self.mt=self.tree(self.match_tab,("score","type","area","available","unit","reason","id"),
                          ("Score","Resource","Stock Location","Available","Unit","Reason","Stock ID"),12)
        self.mt.column("reason",width=390)
        ttk.Label(self.match_tab,text="Scoring: same area +35 • critical incident +20 • disaster compatibility +20 • sufficient stock +15 • nearby fallback +10").pack(anchor="w",pady=8)

    def build_allocations(self):
        bar=ttk.Frame(self.allocation_tab); bar.pack(fill="x",pady=(0,9))
        ttk.Button(bar,text="Mark In Progress",command=lambda:self.update_allocation("In Progress")).pack(side="left")
        ttk.Button(bar,text="Mark Fulfilled",command=lambda:self.update_allocation("Fulfilled")).pack(side="left",padx=6)
        ttk.Button(bar,text="Cancel / Return Stock",command=self.cancel_allocation).pack(side="left")
        self.at=self.tree(self.allocation_tab,("id","incident_area","disaster","resource","source_area","quantity","unit","status","created"),
                          ("ID","Incident Area","Disaster","Resource","Stock Location","Qty","Unit","Status","Created"),15)

    def build_log(self):
        bar=ttk.Frame(self.log_tab); bar.pack(fill="x",pady=(0,9))
        ttk.Button(bar,text="Refresh",command=self.refresh_log).pack(side="left")
        ttk.Button(bar,text="Clear Log",command=self.clear_log).pack(side="left",padx=6)
        self.lt=self.tree(self.log_tab,("time","message"),("Time","Activity"),18)
        self.lt.column("message",width=850)

    def refresh(self):
        incidents=self.data["incidents"]; resources=self.data["resources"]; allocations=self.data["allocations"]
        vals={"inc":len(incidents),"critical":sum(i["severity"]=="Critical" and i["status"]!="Fulfilled" for i in incidents),
              "people":sum(int(i["people"]) for i in incidents if i["status"]!="Fulfilled"),
              "stock":sum(int(r["available"]) for r in resources),"done":sum(a["status"]=="Fulfilled" for a in allocations)}
        for k,v in vals.items(): self.metrics[k].configure(text=f"{v:,}")
        self.clear(self.dash_i)
        order={"Critical":0,"High":1,"Medium":2,"Low":3}
        for i in sorted(incidents,key=lambda x:order.get(x["severity"],4)):
            self.dash_i.insert("","end",values=(i["area"],i["disaster"],i["severity"],i["people"],i["status"]))
        self.clear(self.dash_r)
        for r in resources: self.dash_r.insert("","end",values=(r["type"],r["available"],r["unit"],r["area"]))
        self.clear(self.it)
        for i in incidents: self.it.insert("","end",iid=i["id"],values=(i["id"],i["area"],i["disaster"],i["severity"],i["people"],i["status"],i["created"],i["notes"]))
        self.clear(self.rt)
        for r in resources: self.rt.insert("","end",iid=r["id"],values=(r["id"],r["type"],r["area"],r["quantity"],r["available"],r["unit"],r["notes"]))
        self.clear(self.at)
        for a in allocations: self.at.insert("","end",iid=a["id"],values=(a["id"],a["incident_area"],a["disaster"],a["resource"],a["source_area"],a["quantity"],a["unit"],a["status"],a["created"]))
        choices=[f'{i["id"]} | {i["area"]} | {i["disaster"]} | {i["severity"]}' for i in incidents if i["status"]!="Fulfilled"]
        self.inc_combo["values"]=choices
        if choices and self.inc_var.get() not in choices: self.inc_var.set(choices[0])
        if not choices: self.inc_var.set("")
        self.refresh_log()

    def refresh_log(self):
        self.clear(self.lt)
        for n,a in enumerate(self.data["activity"]): self.lt.insert("","end",iid=str(n),values=(a["time"],a["message"]))

    def form(self,title,fields,callback):
        win=tk.Toplevel(self.root); win.title(title); win.transient(self.root); win.grab_set(); win.resizable(False,False)
        frame=ttk.Frame(win,padding=16); frame.pack(fill="both",expand=True)
        ttk.Label(frame,text=title,font=("Segoe UI",14,"bold")).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,10))
        variables={}
        for row,(label,kind,options,default) in enumerate(fields,1):
            ttk.Label(frame,text=label).grid(row=row,column=0,sticky="w",padx=(0,12),pady=5)
            var=tk.StringVar(value=default); variables[label]=var
            widget=ttk.Combobox(frame,textvariable=var,values=options,state="readonly",width=29) if kind=="combo" else ttk.Entry(frame,textvariable=var,width=32)
            widget.grid(row=row,column=1,sticky="ew",pady=5)
        def submit():
            result=callback({k:v.get().strip() for k,v in variables.items()})
            if result is not False: win.destroy()
        buttons=ttk.Frame(frame); buttons.grid(row=len(fields)+1,column=0,columnspan=2,sticky="e",pady=(12,0))
        ttk.Button(buttons,text="Cancel",command=win.destroy).pack(side="right",padx=(6,0))
        ttk.Button(buttons,text="Save",command=submit).pack(side="right")
        win.bind("<Return>",lambda e:submit())

    def selected(self,tree,what):
        ids=tree.selection()
        if not ids: messagebox.showinfo("Select row",f"Select a {what} first."); return None
        return ids[0]

    def add_incident(self):
        self.form("Report Incident",[("Area","combo",AREAS,"North Zone"),("Disaster type","combo",DISASTERS,"Flood"),
            ("Severity","combo",SEVERITIES,"High"),("People affected","entry",None,"100"),("Notes","entry",None,"")],self.save_incident)

    def save_incident(self,v):
        try:
            people=int(v["People affected"])
            if people<0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input","People affected must be a non-negative whole number."); return False
        i=dict(id=ident(),area=v["Area"],disaster=v["Disaster type"],severity=v["Severity"],people=people,
               notes=v["Notes"],status="Open",created=stamp())
        self.data["incidents"].append(i); self.log(f'Reported {i["disaster"]} incident in {i["area"]} ({i["severity"]}).')
        self.refresh(); return True

    def add_resource(self):
        self.form("Add Resource Stock",[("Location","combo",AREAS,"Central Zone"),("Resource type","combo",TYPES,"Food"),
            ("Quantity","entry",None,"100"),("Unit","entry",None,"units"),("Storage / notes","entry",None,"")],self.save_resource)

    def save_resource(self,v):
        try:
            qty=int(v["Quantity"])
            if qty<=0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid quantity","Quantity must be a positive whole number."); return False
        r=dict(id=ident(),area=v["Location"],type=v["Resource type"],quantity=qty,available=qty,
               unit=v["Unit"] or "units",notes=v["Storage / notes"])
        self.data["resources"].append(r); self.log(f'Added {qty} {r["unit"]} of {r["type"]} at {r["area"]}.')
        self.refresh(); return True

    def change_incident(self):
        iid=self.selected(self.it,"incident")
        if not iid:return
        i=next(x for x in self.data["incidents"] if x["id"]==iid)
        self.form("Change Incident Status",[("Status","combo",STATUSES,i["status"])],
                  lambda v:self.set_incident(i,v["Status"]))

    def set_incident(self,i,status):
        i["status"]=status; self.log(f'Incident {i["id"]} status changed to {status}.'); self.refresh(); return True

    def delete_incident(self):
        iid=self.selected(self.it,"incident")
        if not iid:return
        if messagebox.askyesno("Confirm","Delete this incident? Existing allocations remain in history."):
            self.data["incidents"]=[i for i in self.data["incidents"] if i["id"]!=iid]
            self.log(f"Incident {iid} deleted."); self.refresh()

    def edit_resource(self):
        rid=self.selected(self.rt,"resource")
        if not rid:return
        r=next(x for x in self.data["resources"] if x["id"]==rid)
        def save(v):
            try:
                q=int(v["Available quantity"])
                if q<0 or q>int(r["quantity"]): raise ValueError
            except ValueError:
                messagebox.showerror("Invalid quantity","Enter a whole number from zero to the initial quantity."); return False
            r["available"]=q; self.log(f'Updated available {r["type"]} at {r["area"]}: {q} {r["unit"]}.'); self.refresh(); return True
        self.form("Edit Available Quantity",[("Available quantity","entry",None,str(r["available"]))],save)

    def delete_resource(self):
        rid=self.selected(self.rt,"resource")
        if not rid:return
        if messagebox.askyesno("Confirm","Delete this stock record?"):
            self.data["resources"]=[r for r in self.data["resources"] if r["id"]!=rid]
            self.log(f"Resource stock {rid} deleted."); self.refresh()

    def incident_selected(self):
        value=self.inc_var.get()
        return next((i for i in self.data["incidents"] if value.startswith(i["id"]+" | ")),None) if value else None

    def compatible(self,typ,disaster):
        mapping={"Flood":{"Food","Drinking Water","Rescue Boats","Medical Teams","First Aid Kits","Shelter Kits"},
        "Cyclone":{"Food","Drinking Water","Blankets","Shelter Kits","Power Generators","Medical Teams"},
        "Earthquake":{"First Aid Kits","Medical Teams","Food","Drinking Water","Shelter Kits","Blankets"},
        "Fire":{"First Aid Kits","Medical Teams","Drinking Water","Shelter Kits"},
        "Landslide":{"Medical Teams","Food","Drinking Water","First Aid Kits","Shelter Kits"}}
        return typ in mapping.get(disaster,set(TYPES))

    def zone_distance(self,a,b):
        # Demo-only zone order, not real geographic distance.
        order=["North Zone","East Zone","Central Zone","West Zone","South Zone"]
        try:return abs(order.index(a)-order.index(b))
        except ValueError:return 99

    def find_matches(self):
        inc=self.incident_selected()
        if not inc: messagebox.showinfo("Incident","Add or select an open incident first."); return
        try:
            qty=int(self.qty_var.get())
            if qty<=0: raise ValueError
        except ValueError:
            messagebox.showerror("Quantity","Enter a positive whole number."); return
        self.clear(self.mt); found=[]
        for r in self.data["resources"]:
            if r["type"]!=self.typ_var.get() or int(r["available"])<=0: continue
            score=0; reasons=[]
            if r["area"]==inc["area"]: score+=35; reasons.append("same area +35")
            elif self.zone_distance(r["area"],inc["area"])==1: score+=10; reasons.append("nearby-zone fallback +10")
            if inc["severity"]=="Critical": score+=20; reasons.append("critical priority +20")
            if self.compatible(r["type"],inc["disaster"]): score+=20; reasons.append("disaster compatibility +20")
            if int(r["available"])>=qty: score+=15; reasons.append("sufficient stock +15")
            if r["area"]!=inc["area"] and self.zone_distance(r["area"],inc["area"])>1: reasons.append("confirm transport from distant zone")
            found.append((score,r,"; ".join(reasons) or "available stock"))
        found.sort(key=lambda x:(-x[0],x[1]["area"]))
        for score,r,reason in found:
            self.mt.insert("","end",iid=r["id"],values=(score,r["type"],r["area"],r["available"],r["unit"],reason,r["id"]))
        if not found: messagebox.showinfo("No stock",f"No available stock found for {self.typ_var.get()}.")

    def allocate(self):
        inc=self.incident_selected(); rid=self.selected(self.mt,"match")
        if not inc or not rid:return
        try:
            qty=int(self.qty_var.get())
            if qty<=0:raise ValueError
        except ValueError: messagebox.showerror("Quantity","Enter a positive whole number."); return
        r=next((x for x in self.data["resources"] if x["id"]==rid),None)
        if not r: messagebox.showerror("Stock","Resource no longer exists. Find matches again."); return
        if qty>int(r["available"]): messagebox.showerror("Stock",f"Only {r['available']} {r['unit']} available."); return
        prompt=f"Allocate {qty} {r['unit']} of {r['type']} from {r['area']} to {inc['area']}?"
        if not messagebox.askyesno("Confirm allocation",prompt):return
        r["available"]-=qty
        a=dict(id=ident(),incident_id=inc["id"],incident_area=inc["area"],disaster=inc["disaster"],
               resource_id=r["id"],resource=r["type"],source_area=r["area"],quantity=qty,unit=r["unit"],
               status="Open",created=stamp())
        self.data["allocations"].append(a); self.log(f'Allocated {qty} {r["unit"]} of {r["type"]} to {inc["area"]}.')
        self.refresh(); self.tabs.select(self.allocation_tab)
        messagebox.showinfo("Allocation created","Allocation recorded and available stock reduced.")

    def update_allocation(self,status):
        aid=self.selected(self.at,"allocation")
        if not aid:return
        a=next(x for x in self.data["allocations"] if x["id"]==aid)
        if a["status"]=="Cancelled": messagebox.showinfo("Cancelled","Cancelled allocations cannot be updated."); return
        a["status"]=status; self.log(f'Allocation {aid} marked {status}.'); self.refresh()

    def cancel_allocation(self):
        aid=self.selected(self.at,"allocation")
        if not aid:return
        a=next(x for x in self.data["allocations"] if x["id"]==aid)
        if a["status"]=="Cancelled":return
        if not messagebox.askyesno("Cancel allocation","Cancel and return the quantity to available stock?"):return
        r=next((x for x in self.data["resources"] if x["id"]==a["resource_id"]),None)
        if r:r["available"]=min(int(r["quantity"]),int(r["available"])+int(a["quantity"]))
        a["status"]="Cancelled"; self.log(f'Allocation {aid} cancelled; stock returned if source still exists.'); self.refresh()

    def clear_log(self):
        if messagebox.askyesno("Clear log","Clear the activity log?"):
            self.data["activity"]=[]; self.save(); self.refresh_log()

    def export(self):
        path=filedialog.asksaveasfilename(title="Export ResQGrid data",defaultextension=".json",
            filetypes=[("JSON files","*.json"),("All files","*.*")],initialfile="resqgrid_export.json")
        if not path:return
        try:
            with open(path,"w",encoding="utf-8") as f:json.dump(self.data,f,indent=2)
            messagebox.showinfo("Export complete","Data exported successfully.")
        except OSError as e:messagebox.showerror("Export error",str(e))

def main():
    root=tk.Tk()
    ResQGrid(root)
    root.mainloop()

if __name__=="__main__":
    main()
