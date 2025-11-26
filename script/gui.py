import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
import sys
import webbrowser

try:
    from PIL import Image, ImageTk
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from logic import GameLogic
from settings import SettingsManager
from windows.settings_window import SettingsWindow
from windows.edit_window import EditWindow
from components.detail_panel import DetailPanel
from components.library_panel import LibraryPanel
from utils import format_size, truncate_text, get_folder_size, get_file_size
import constants

class DOSManagerApp(tb.Window):
    DETAIL_PANEL_WIDTH = 550
    LIBRARY_PANEL_WIDTH = 750
    
    def __init__(self):
        self.settings = SettingsManager()
        theme = self.settings.get("theme") or "darkly"
        super().__init__(themename=theme)
        self.title("DOS Game Manager")
        self.geometry("")

        self.logic = GameLogic(self.settings)
        self.win_settings, self.win_edit = None, None
        self.playlist_visible, self.description_visible = True, True
        self.current_images, self.current_img_index = [], 0
        
        self.search_var = tk.StringVar()
        self.fav_only_var = tk.BooleanVar(value=False)
        self.search_var.trace("w", lambda *args: self.refresh_library())
        self.sort_col, self.sort_desc = "name", False
        self.force_fullscreen_var, self.hide_console_var = tk.BooleanVar(value=False), tk.BooleanVar(value=True)

        self.init_ui()
        self.minsize(550, 500)

        if os.path.exists(self.settings.get("root_dir")):
            self.refresh_library()
        else:
            messagebox.showinfo("Welcome", "Please configure Settings.")

    def init_ui(self):
        self.columnconfigure(0, weight=0, minsize=self.DETAIL_PANEL_WIDTH)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.detail_panel = DetailPanel(self, self.logic)
        self.library_panel = LibraryPanel(self)
        self.tree = self.library_panel.tree

    def toggle_description(self):
        if self.description_visible:
            self.detail_panel.tabs.grid_remove()
            self.detail_panel.btn_toggle_desc.config(bootstyle="secondary")
        else:
            self.detail_panel.tabs.grid()
            self.detail_panel.btn_toggle_desc.config(bootstyle="secondary-outline")
        self.description_visible = not self.description_visible

    def toggle_list(self):
        if self.playlist_visible:
            self.library_panel.grid_remove()
            self.columnconfigure(1, minsize=0, weight=0) # Odstráni minimálnu veľkosť a váhu
            self.detail_panel.btn_list.config(bootstyle="primary")
        else:
            self.library_panel.grid()
            self.columnconfigure(1, minsize=self.LIBRARY_PANEL_WIDTH, weight=1) # Vráti ich späť
            self.detail_panel.btn_list.config(bootstyle="secondary-outline")
        self.playlist_visible = not self.playlist_visible

    def on_play(self):
        zip_name = self._get_selected_zip()
        if zip_name:
            try:
                self.logic.launch_game(zip_name, force_fullscreen=self.force_fullscreen_var.get(), hide_console=self.hide_console_var.get())
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel: self.clear_preview(); return
        
        zip_name = sel[0]; name = os.path.splitext(zip_name)[0]
        is_installed = 'installed' in self.tree.item(zip_name, 'tags')
        dp = self.detail_panel
        dp.btn_edit.configure(state=tk.NORMAL)
        
        if is_installed:
            dp.btn_install.configure(state=tk.DISABLED); dp.btn_play.configure(state=tk.NORMAL); dp.btn_uninstall.configure(state=tk.NORMAL)
        else:
            dp.btn_install.configure(state=tk.NORMAL); dp.btn_play.configure(state=tk.DISABLED); dp.btn_uninstall.configure(state=tk.DISABLED)

        title_text = truncate_text(name.replace("_"," ").title(), 30)
        if self.logic.is_favorite(name): title_text += " ★"
        dp.lbl_title.config(text=title_text)
        
        g = self.logic.load_meta(name, ".genre"); y = self.logic.load_meta(name, ".year"); c = self.logic.load_meta(name, ".company")
        txt_meta = f"[{g}] " if g else ""; txt_meta += f"Year: {y} " if y else ""; txt_meta += f"| Dev: {truncate_text(c, 20)}" if c else ""
        dp.lbl_year.config(text=txt_meta)

        r = self.logic.load_rating(name); dp.lbl_rating.config(text="★" * r if r else "")
        
        desc = self.logic.load_meta(name, ".txt")
        dp.txt_desc.config(state=tk.NORMAL); dp.txt_desc.delete(1.0, tk.END); dp.txt_desc.insert(tk.END, desc or "No description."); dp.txt_desc.config(state=tk.DISABLED)
        notes = self.logic.load_meta(name, ".notes"); dp.txt_notes.delete(1.0, tk.END); dp.txt_notes.insert(tk.END, notes or "")

        z_sz = get_file_size(os.path.join(self.logic.zipped_dir, zip_name)) if self.logic.zipped_dir else 0
        h_sz = get_folder_size(os.path.join(self.logic.installed_dir, name)) if is_installed and self.logic.installed_dir else 0
        dp.lbl_size.config(text=f"Zip: {format_size(z_sz)} | HDD: {format_size(h_sz)}")

        self.current_images = self.logic.get_game_images(name); self.current_img_index = 0
        self.load_and_display_image()

    def load_and_display_image(self):
        dp = self.detail_panel
        if not HAS_PILLOW or not self.current_images:
            dp.lbl_img.config(image='', text="No Image"); dp.lbl_img.image = None; dp.lbl_img_info.config(text=""); return
        
        if self.current_img_index >= len(self.current_images): self.current_img_index = 0
        path = self.current_images[self.current_img_index]
        
        try:
            # Oprava: Použijeme .resize() na natiahnutie obrázku
            img = Image.open(path); img = img.resize((512, 384), Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            dp.lbl_img.image = photo_img; dp.lbl_img.config(image=photo_img)
            info_text = f"Image {self.current_img_index + 1} of {len(self.current_images)}" if len(self.current_images) > 1 else ""
            dp.lbl_img_info.config(text=info_text)
        except Exception as e:
            dp.lbl_img.config(image='', text="Image Error"); dp.lbl_img.image = None; print(f"Image Error: {e}")

    def next_image(self, event=None):
        if len(self.current_images) > 1:
            self.current_img_index = (self.current_img_index + 1) % len(self.current_images)
            self.load_and_display_image()

    def on_double_click(self):
        zip_name = self._get_selected_zip()
        if not zip_name: return
        if 'installed' in self.tree.item(zip_name, 'tags'): self.on_play()
        else: self.on_install()
            
    def _move_selection(self, direction):
        selected_id = self._get_selected_zip()
        if not selected_id: return
        all_ids = self.tree.get_children()
        if not all_ids: return
        try:
            current_index = all_ids.index(selected_id)
            new_index = (current_index + direction) % len(all_ids)
            self.tree.selection_set(all_ids[new_index]); self.tree.see(all_ids[new_index])
        except ValueError: pass

    def select_prev(self): self._move_selection(-1)
    def select_next(self): self._move_selection(1)
            
    def refresh_library(self):
        search = self.search_var.get().lower().strip(); fav_only = self.fav_only_var.get()
        selected = self.tree.selection(); save_id = selected[0] if selected else None
        for i in self.tree.get_children(): self.tree.delete(i)
        
        game_list, installed_set = self.logic.get_game_list(); data_rows = []
        for zip_name in game_list:
            name_no_zip = os.path.splitext(zip_name)[0]
            if search and search not in name_no_zip.lower(): continue
            is_fav = self.logic.is_favorite(name_no_zip)
            if fav_only and not is_fav: continue
            is_inst = zip_name in installed_set
            
            g = self.logic.load_meta(name_no_zip, ".genre"); y = self.logic.load_meta(name_no_zip, ".year"); c = self.logic.load_meta(name_no_zip, ".company")
            r = self.logic.load_rating(name_no_zip)
            z_sz = get_file_size(os.path.join(self.logic.zipped_dir, zip_name)) if self.logic.zipped_dir else 0
            h_sz = get_folder_size(os.path.join(self.logic.installed_dir, name_no_zip)) if is_inst and self.logic.installed_dir else 0
            
            prefix = "✓" if is_inst else "…"; disp_name = f"{prefix} {name_no_zip}"
            if is_fav: disp_name += " ★"
            tag = 'installed' if is_inst else 'zipped'; rating_stars = "★" * r if r else ""
            row_data = {"name": disp_name, "genre": g, "year": y, "company": c, "rating": rating_stars, "zip": format_size(z_sz), "hdd": format_size(h_sz), "id": zip_name, "tag": tag, "_sort_rating": r, "_sort_zip": z_sz, "_sort_hdd": h_sz}
            data_rows.append(row_data)
            
        sort_map = {"name": "id", "genre": "genre", "company": "company", "year": "year", "rating": "_sort_rating", "zip": "_sort_zip", "hdd": "_sort_hdd"}
        sort_key_name = sort_map.get(self.sort_col, "id")
        data_rows.sort(key=lambda item: (item.get(sort_key_name) or "").lower() if isinstance(item.get(sort_key_name), str) else (item.get(sort_key_name) or 0), reverse=self.sort_desc)
        
        visible_columns = self.tree["columns"]
        for row in data_rows:
            values_to_insert = [row.get(col_id) for col_id in visible_columns]
            self.tree.insert("", "end", iid=row["id"], values=values_to_insert, tags=(row["tag"],))
            
        if save_id and self.tree.exists(save_id): self.tree.selection_set(save_id); self.tree.see(save_id)
        elif data_rows:
            first_id = data_rows[0]["id"]
            if self.tree.exists(first_id): self.tree.selection_set(first_id)
        else: self.clear_preview()
        self.on_select()
    
    def clear_preview(self):
        dp = self.detail_panel; dp.lbl_title.config(text="Select Game"); dp.lbl_img.config(image='', text="No Image")
        dp.lbl_img.image = None; dp.btn_play.config(state=tk.DISABLED); dp.btn_install.config(state=tk.DISABLED)
        dp.lbl_size.config(text=""); dp.lbl_img_info.config(text=""); dp.txt_desc.config(state=tk.NORMAL)
        dp.txt_desc.delete(1.0, tk.END); dp.txt_desc.config(state=tk.DISABLED); dp.txt_notes.delete(1.0, tk.END); dp.lbl_sheet.config(text="")
        self.current_images = []

    def _get_selected_zip(self): sel = self.tree.selection(); return sel[0] if sel else None
    def on_install(self):
        zip_name = self._get_selected_zip()
        if zip_name:
            try: self.logic.install_game(zip_name); self.refresh_library()
            except Exception as e: messagebox.showerror("Error", str(e))
    def on_uninstall(self):
        zip_name = self._get_selected_zip()
        if zip_name and messagebox.askyesno("Confirm", "Uninstall game?"): self.logic.uninstall_game(zip_name); self.refresh_library()
    def restart_program(self): sys.stdout.flush(); os.execl(sys.executable, sys.executable, *sys.argv)
    def open_settings(self):
        if self.win_settings and self.win_settings.winfo_exists(): self.win_settings.lift()
        else: self.win_settings = SettingsWindow(self)
    def open_edit_window(self):
        zip_name = self._get_selected_zip()
        if not zip_name: return
        if self.win_edit and self.win_edit.winfo_exists(): self.win_edit.lift()
        else: self.win_edit = EditWindow(self, zip_name)
    def sort_tree(self, col):
        if self.sort_col == col: self.sort_desc = not self.sort_desc
        else: self.sort_col = col; self.sort_desc = False
        self.refresh_library()
    def save_notes(self):
        sel = self._get_selected_zip()
        if sel: self.logic.save_meta(os.path.splitext(sel)[0], ".notes", self.detail_panel.txt_notes.get(1.0, tk.END).strip())
    def show_tree_context(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        self.tree.selection_set(item_id); is_inst = 'installed' in self.tree.item(item_id, 'tags'); name = os.path.splitext(item_id)[0]
        menu = tb.Menu(self, tearoff=0)
        menu.add_command(label="✎ Configuration", command=self.open_edit_window)
        is_fav = self.logic.is_favorite(name); fav_label = "💔 Unfavorite" if is_fav else "★ Favorite"
        menu.add_command(label=fav_label, command=lambda n=name: self.toggle_fav_from_context(n))
        menu.add_separator()
        if is_inst:
            menu.add_command(label="▶ Play Game", command=self.on_play)
            exe_map = self.logic.load_exe_map(name); custom_items = [(info.get("title", os.path.basename(exe)), exe) for exe, info in exe_map.items() if info.get("role") != "main"]
            if custom_items:
                sub_custom = tb.Menu(menu, tearoff=0)
                for title, exe in custom_items: sub_custom.add_command(label=title, command=lambda i=item_id, x=exe: self.logic.launch_game(i, specific_exe=x, force_fullscreen=self.force_fullscreen_var.get(), hide_console=self.hide_console_var.get()))
                menu.add_cascade(label="📂 Other Executables", menu=sub_custom)
            menu.add_separator()
            menu.add_command(label="📝 Edit Config (Notepad)", command=lambda i=item_id: self.logic.open_config_in_notepad(i))
            menu.add_command(label="💻 Run DOSBox (CMD)", command=lambda i=item_id: self.logic.launch_dosbox_prompt(i))
            menu.add_separator()
            menu.add_command(label="Uninstall", command=self.on_uninstall)
        else: menu.add_command(label="Install", command=self.on_install)
        menu.add_separator()
        rate_menu = tb.Menu(menu, tearoff=0)
        for i in range(1, 6): rate_menu.add_command(label="★" * i, command=lambda r=i: self.set_rating(item_id, r))
        menu.add_cascade(label="Rate", menu=rate_menu)
        menu.post(event.x_root, event.y_root)
    def toggle_fav_from_context(self, name): self.logic.toggle_favorite(name); self.refresh_library()
    def set_rating(self, item_id, rating): self.logic.save_meta(os.path.splitext(item_id)[0], ".rating", rating); self.refresh_library()