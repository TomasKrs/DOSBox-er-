import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class DetailPanel(tb.Frame):
    def __init__(self, parent, logic_instance, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = parent
        self.logic = logic_instance
        self._init_ui()

    def _init_ui(self):
        self.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 5))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)

        f_nav = tb.Frame(self)
        f_nav.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        f_nav.columnconfigure(0, weight=1)
        self.btn_toggle_desc = tb.Button(f_nav, text="≡ Details", bootstyle="secondary-outline", command=self.app.toggle_description)
        self.btn_toggle_desc.pack(side=tk.LEFT)
        self.btn_list = tb.Button(f_nav, text="List", bootstyle="secondary-outline", command=self.app.toggle_list)
        self.btn_list.pack(side=tk.RIGHT)

        image_frame = tb.Frame(self, width=512, height=384)
        image_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        image_frame.grid_propagate(False) # Zabráni zmršteniu
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)

        self.lbl_img = tb.Label(image_frame, text="No Image", anchor="center", bootstyle="secondary")
        self.lbl_img.grid(row=0, column=0, sticky="nsew")
        self.lbl_img.bind("<Button-1>", self.app.next_image)

        self.lbl_img_info = tb.Label(self, text="", anchor="e", bootstyle="secondary")
        self.lbl_img_info.grid(row=2, column=0, sticky="e", padx=10, pady=(0, 5))

        f_title = tb.Frame(self); f_title.grid(row=3, column=0, sticky="ew"); f_title.columnconfigure(1, weight=1)
        self.btn_prev = tb.Button(f_title, text="<", command=self.app.select_prev); self.btn_prev.grid(row=0, column=0, padx=(0,5))
        self.lbl_title = tb.Label(f_title, text="Select a game", font=("Segoe UI", 16, "bold"), anchor="center"); self.lbl_title.grid(row=0, column=1, sticky="ew")
        self.btn_next = tb.Button(f_title, text=">", command=self.app.select_next); self.btn_next.grid(row=0, column=2, padx=(5,0))

        f_meta = tb.Frame(self); f_meta.grid(row=4, column=0, sticky="ew", padx=5); f_meta.columnconfigure(0, weight=1)
        self.lbl_year = tb.Label(f_meta, text="", anchor="w", bootstyle="secondary"); self.lbl_year.grid(row=0, column=0, sticky="w")
        self.lbl_rating = tb.Label(f_meta, text="", anchor="e", bootstyle="warning"); self.lbl_rating.grid(row=0, column=1, sticky="e")
        
        f_all_buttons = tb.Frame(self); f_all_buttons.grid(row=5, column=0, sticky="ew", pady=10); f_all_buttons.columnconfigure(0, weight=1)
        self.btn_play = tb.Button(f_all_buttons, text="▶ PLAY", bootstyle="success", state=tk.DISABLED, command=self.app.on_play)
        self.btn_play.grid(row=0, column=0, sticky="ew", padx=2, pady=(0,5))
        f_config_row = tb.Frame(f_all_buttons); f_config_row.grid(row=1, column=0, sticky="ew"); f_config_row.columnconfigure(0, weight=1) 
        self.btn_edit = tb.Button(f_config_row, text="✎ Configuration", bootstyle="info", state=tk.DISABLED, command=self.app.open_edit_window)
        self.btn_edit.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_install = tb.Button(f_config_row, text="Install", bootstyle="primary-outline", state=tk.DISABLED, command=self.app.on_install)
        self.btn_install.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_uninstall = tb.Button(f_config_row, text="🗑", bootstyle="danger-outline", state=tk.DISABLED, command=self.app.on_uninstall)
        self.btn_uninstall.grid(row=0, column=2, sticky="ew", padx=2)
        
        self.tabs = tb.Notebook(self, bootstyle="dark")
        self.tabs.grid(row=7, column=0, sticky="nsew")
        
        # --- FRAME PRE INFO S POSUVNÍKOM ---
        self.txt_desc_frame = tb.Frame(self.tabs)
        self.txt_desc_frame.pack(fill="both", expand=True)
        self.txt_desc = tb.Text(self.txt_desc_frame, wrap="word", relief="flat", state="disabled", height=11)
        desc_scroll = tb.Scrollbar(self.txt_desc_frame, orient="vertical", command=self.txt_desc.yview)
        self.txt_desc['yscrollcommand'] = desc_scroll.set
        desc_scroll.pack(side="right", fill="y")
        self.txt_desc.pack(side="left", fill="both", expand=True)

        # --- FRAME PRE NOTES S POSUVNÍKOM ---
        self.txt_notes_frame = tb.Frame(self.tabs)
        self.txt_notes_frame.pack(fill="both", expand=True)
        self.txt_notes = tb.Text(self.txt_notes_frame, wrap="word", relief="flat", height=11)
        notes_scroll = tb.Scrollbar(self.txt_notes_frame, orient="vertical", command=self.txt_notes.yview)
        self.txt_notes['yscrollcommand'] = notes_scroll.set
        notes_scroll.pack(side="right", fill="y")
        self.txt_notes.pack(side="left", fill="both", expand=True)
        
        self.lbl_sheet_frame = tb.Frame(self.tabs)
        self.lbl_sheet = tb.Label(self.lbl_sheet_frame, text="", anchor="nw", justify="left"); self.lbl_sheet.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabs.add(self.txt_desc_frame, text="Info")
        self.tabs.add(self.txt_notes_frame, text="Notes")
        self.tabs.add(self.lbl_sheet_frame, text="Shortcuts")
        
        self.lbl_size = tb.Label(self, text="", bootstyle="secondary", anchor="e")
        self.lbl_size.grid(row=8, column=0, sticky="se", padx=5)