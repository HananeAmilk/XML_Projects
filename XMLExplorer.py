import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from lxml import etree
import os
import json
from datetime import datetime
import re
import threading
import webbrowser
import tempfile
from playwright.sync_api import sync_playwright

import logging
logging.basicConfig(level=logging.ERROR)
 
class XPathExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Explorer")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Theme colors
        self.colors = {
            "primary": "#2c3e50",
            "secondary": "#3498db", 
            "accent": "#27ae60",
            "warning": "#e74c3c",
            "background": "#f5f7fa",
            "card": "#ffffff",
            "text": "#333333",
            "light_text": "#7f8c8d"
        }
        
        # Configuration variables
        self.current_file = None
        self.xml_tree = None
        self.xml_root = None
        self.xslt_file = None
        self.xslt_transform = None
        self.history = []
        self.history_index = -1
        self.favorites = []
        self.load_settings()
        
        # Apply theme
        self.root.configure(bg=self.colors["background"])
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("Card.TFrame", background=self.colors["card"])
        self.style.configure("TButton", 
                             background=self.colors["secondary"], 
                             foreground="white",
                             padding=10,
                             font=("Segoe UI", 10))
        self.style.map("TButton", 
                       background=[('active', '#2980b9'), ('pressed', '#1f6aa5')])
        self.style.configure("Accent.TButton", 
                             background=self.colors["accent"],
                             foreground="white")
        self.style.map("Accent.TButton", 
                       background=[('active', '#219653'), ('pressed', '#1e874b')])
        self.style.configure("TLabel", 
                             background=self.colors["background"],
                             foreground=self.colors["text"],
                             font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", 
                             font=("Segoe UI", 16, "bold"),
                             foreground=self.colors["primary"],
                             background=self.colors["background"])
        self.style.configure("Subheader.TLabel", 
                             font=("Segoe UI", 12),
                             foreground=self.colors["secondary"],
                             background=self.colors["background"])
        
        # Create menu
        self.create_menu()
        
        # Create UI
        self.create_ui()
        
        # Initialize status
        self.update_status("Prêt")
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Ouvrir XML...", command=self.load_xml_file)
        file_menu.add_command(label="Ouvrir XSLT...", command=self.load_xslt_file)
        file_menu.add_separator()
        file_menu.add_command(label="Enregistrer résultats...", command=self.save_results)
        file_menu.add_command(label="Exporter en PDF...", command=self.export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copier résultats", command=self.copy_results)
        edit_menu.add_command(label="Effacer historique", command=self.clear_history)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        
        # Transform menu
        transform_menu = tk.Menu(menubar, tearoff=0)
        transform_menu.add_command(label="Appliquer transformation XSLT", command=self.apply_xslt)
        transform_menu.add_command(label="Prévisualiser HTML", command=self.preview_html)
        transform_menu.add_command(label="Enregistrer HTML...", command=self.save_html)
        menubar.add_cascade(label="Transformation", menu=transform_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Afficher arborescence XML", command=self.show_xml_tree)
        view_menu.add_command(label="Afficher XML brut", command=self.show_xml_raw)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Aide XPath", command=self.show_xpath_reference)
        help_menu.add_command(label="Aide XSLT", command=self.show_xslt_reference)
        help_menu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="XML Explorer", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        self.file_label = ttk.Label(header_frame, text="Aucun fichier chargé", style="Subheader.TLabel")
        self.file_label.pack(side=tk.RIGHT)
        
        # Content layout (with left sidebar and main content)
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for history and favorites
        sidebar_frame = ttk.Frame(content_frame, style="Card.TFrame")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15), pady=0)
        
        # Notebook for sidebar tabs
        sidebar_notebook = ttk.Notebook(sidebar_frame)
        sidebar_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # History tab
        history_frame = ttk.Frame(sidebar_notebook, style="Card.TFrame")
        sidebar_notebook.add(history_frame, text="Historique")
        
        self.history_list = tk.Listbox(history_frame, bg=self.colors["card"], 
                                      fg=self.colors["text"],
                                      font=("Segoe UI", 10),
                                      width=30,
                                      height=15,
                                      selectbackground=self.colors["secondary"],
                                      selectforeground="white")
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_list.bind("<<ListboxSelect>>", self.load_from_history)
        
        history_buttons = ttk.Frame(history_frame, style="Card.TFrame")
        history_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(history_buttons, text="Effacer", command=self.clear_history, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_buttons, text="Utiliser", command=lambda: self.load_from_history(None), 
                  width=10).pack(side=tk.RIGHT, padx=5)
        
        # Favorites tab
        favorites_frame = ttk.Frame(sidebar_notebook, style="Card.TFrame")
        sidebar_notebook.add(favorites_frame, text="Favoris")
        
        self.favorites_list = tk.Listbox(favorites_frame, bg=self.colors["card"], 
                                        fg=self.colors["text"],
                                        font=("Segoe UI", 10),
                                        width=30,
                                        selectbackground=self.colors["secondary"],
                                        selectforeground="white")
        self.favorites_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.favorites_list.bind("<<ListboxSelect>>", self.load_from_favorites)
        
        favorites_buttons = ttk.Frame(favorites_frame, style="Card.TFrame")
        favorites_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(favorites_buttons, text="Supprimer", command=self.remove_favorite, 
                  width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(favorites_buttons, text="Utiliser", command=lambda: self.load_from_favorites(None), 
                  width=10).pack(side=tk.RIGHT, padx=5)
        
        # XSLT tab
        xslt_frame = ttk.Frame(sidebar_notebook, style="Card.TFrame")
        sidebar_notebook.add(xslt_frame, text="XSLT")
        
        xslt_info_frame = ttk.Frame(xslt_frame, style="Card.TFrame")
        xslt_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(xslt_info_frame, text="Fichier XSLT:", 
                background=self.colors["card"]).pack(side=tk.LEFT, padx=5)
        
        self.xslt_status = ttk.Label(xslt_info_frame, text="Non chargé", 
                                   foreground=self.colors["warning"],
                                   background=self.colors["card"])
        self.xslt_status.pack(side=tk.RIGHT, padx=5)
        
        xslt_buttons_frame = ttk.Frame(xslt_frame, style="Card.TFrame")
        xslt_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(xslt_buttons_frame, text="Charger XSLT", 
                 command=self.load_xslt_file).pack(fill=tk.X, pady=5)
        ttk.Button(xslt_buttons_frame, text="Transformer", 
                 command=self.apply_xslt).pack(fill=tk.X, pady=5)
        ttk.Button(xslt_buttons_frame, text="Prévisualiser", 
                 command=self.preview_html).pack(fill=tk.X, pady=5)
        ttk.Button(xslt_buttons_frame, text="Enregistrer HTML", 
                 command=self.save_html).pack(fill=tk.X, pady=5)
        ttk.Button(xslt_buttons_frame, text="Exporter PDF", 
                 command=self.export_to_pdf).pack(fill=tk.X, pady=5)
        
        # Main content area
        main_content = ttk.Frame(content_frame, style="TFrame")
        main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # XPath input area
        xpath_frame = ttk.Frame(main_content, style="Card.TFrame")
        xpath_frame.pack(fill=tk.X, pady=(0, 15))
        
        xpath_header = ttk.Frame(xpath_frame, style="Card.TFrame")
        xpath_header.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        ttk.Label(xpath_header, text="Requête XPath:", style="TLabel", 
                background=self.colors["card"]).pack(side=tk.LEFT)
        
        self.favorite_btn = ttk.Button(xpath_header, text="★ Favori", 
                                     command=self.add_to_favorites, width=12)
        self.favorite_btn.pack(side=tk.RIGHT, padx=5)
        
        # XPath entry with buttons
        xpath_input_frame = ttk.Frame(xpath_frame, style="Card.TFrame")
        xpath_input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.xpath_var = tk.StringVar()
        self.xpath_entry = ttk.Entry(xpath_input_frame, textvariable=self.xpath_var, 
                                   font=("Consolas", 12))
        self.xpath_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.xpath_entry.bind("<Return>", lambda event: self.execute_xpath())
        self.xpath_entry.bind("<Up>", self.history_up)
        self.xpath_entry.bind("<Down>", self.history_down)
        
        ttk.Button(xpath_input_frame, text="Exécuter", style="Accent.TButton",
                  command=self.execute_xpath, width=12).pack(side=tk.RIGHT)
        
        # Results area with tabs
        self.results_notebook = ttk.Notebook(main_content)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        results_frame = ttk.Frame(self.results_notebook, style="Card.TFrame")
        self.results_notebook.add(results_frame, text="Résultats")
        
        # Results text area with scrolling
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 11),
                                                    background=self.colors["card"],
                                                    foreground=self.colors["text"])
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.results_text.config(state=tk.DISABLED)
        
        # XML view tab
        self.xml_frame = ttk.Frame(self.results_notebook, style="Card.TFrame")
        self.results_notebook.add(self.xml_frame, text="Aperçu XML")
        
        self.xml_text = scrolledtext.ScrolledText(self.xml_frame, 
                                               wrap=tk.WORD, 
                                               font=("Consolas", 11),
                                               background=self.colors["card"],
                                               foreground=self.colors["text"])
        self.xml_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.xml_text.config(state=tk.DISABLED)
        
        # HTML view tab
        self.html_frame = ttk.Frame(self.results_notebook, style="Card.TFrame")
        self.results_notebook.add(self.html_frame, text="Aperçu HTML")
        
        self.html_text = scrolledtext.ScrolledText(self.html_frame, 
                                                wrap=tk.WORD, 
                                                font=("Consolas", 11),
                                                background=self.colors["card"],
                                                foreground=self.colors["text"])
        self.html_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.html_text.config(state=tk.DISABLED)
        
        # Status bar
        status_frame = ttk.Frame(main_frame, style="TFrame")
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_label = ttk.Label(status_frame, text="Prêt", 
                                    font=("Segoe UI", 9),
                                    foreground=self.colors["light_text"])
        self.status_label.pack(side=tk.LEFT)
        
        # Initialize UI state
        self.refresh_history_list()
        self.refresh_favorites_list()
        
    def update_status(self, message):
        """Mettre à jour la barre de statut avec un message et un horodatage"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"{timestamp} - {message}")
        
    def load_xml_file(self):
        """Charger un fichier XML avec gestion des erreurs"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers XML", "*.xml"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.update_status(f"Chargement du fichier: {file_path}")
            
            # Utiliser un thread pour éviter le gel de l'interface avec des fichiers volumineux
            def load_xml_thread():
                try:
                    self.xml_tree = etree.parse(file_path)
                    self.xml_root = self.xml_tree.getroot()
                    self.current_file = file_path
                    
                    # Mettre à jour l'interface depuis le thread principal
                    self.root.after(0, self.update_after_load, file_path)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erreur de chargement XML", 
                        f"Échec du chargement du fichier XML:\n{str(e)}"
                    ))
                    self.root.after(0, lambda: self.update_status(f"Erreur de chargement du fichier: {str(e)}"))
            
            # Démarrer le thread de chargement
            threading.Thread(target=load_xml_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier XML: {str(e)}")
            self.update_status(f"Erreur de chargement du fichier: {str(e)}")
    
    def load_xslt_file(self):
        """Charger un fichier XSLT avec gestion des erreurs"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers XSLT", "*.xsl *.xslt"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.update_status(f"Chargement du fichier XSLT: {file_path}")
            
            # Utiliser un thread pour éviter le gel de l'interface
            def load_xslt_thread():
                try:
                    xslt_tree = etree.parse(file_path)
                    self.xslt_transform = etree.XSLT(xslt_tree)
                    self.xslt_file = file_path
                    
                    # Mettre à jour l'interface depuis le thread principal
                    self.root.after(0, self.update_after_xslt_load, file_path)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erreur de chargement XSLT", 
                        f"Échec du chargement du fichier XSLT:\n{str(e)}"
                    ))
                    self.root.after(0, lambda: self.update_status(f"Erreur de chargement XSLT: {str(e)}"))
            
            # Démarrer le thread de chargement
            threading.Thread(target=load_xslt_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier XSLT: {str(e)}")
            self.update_status(f"Erreur de chargement XSLT: {str(e)}")
    
    def update_after_xslt_load(self, file_path):
        """Mettre à jour l'interface après le chargement réussi d'un XSLT"""
        filename = os.path.basename(file_path)
        self.xslt_status.config(text=f"{filename}", foreground=self.colors["accent"])
        self.update_status(f"Fichier XSLT chargé: {filename}")
    
    def update_after_load(self, file_path):
        """Mettre à jour l'interface après le chargement réussi d'un XML"""
        filename = os.path.basename(file_path)
        self.file_label.config(text=f"Fichier: {filename}")
        
        # Afficher l'aperçu XML
        self.xml_text.config(state=tk.NORMAL)
        self.xml_text.delete("1.0", tk.END)
        
        # Formater le XML avec une indentation appropriée
        xml_string = etree.tostring(self.xml_root, pretty_print=True, encoding='unicode')
        self.xml_text.insert(tk.END, xml_string)
        
        # Appliquer la coloration syntaxique
        self.highlight_xml()
        self.xml_text.config(state=tk.DISABLED)
        
        # Passer à l'onglet d'aperçu XML
        self.results_notebook.select(1)  # Sélectionner l'onglet d'aperçu XML
        
        self.update_status(f"Fichier XML chargé: {filename}")
        
        # Effacer les résultats
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"✅ Fichier XML chargé avec succès\n")
        self.results_text.insert(tk.END, f"📂 Fichier: {file_path}\n")
        self.results_text.insert(tk.END, f"🔢 Éléments: {self.count_elements(self.xml_root)}\n")
        self.results_text.insert(tk.END, "\nEntrez une requête XPath et cliquez sur Exécuter")
        self.results_text.config(state=tk.DISABLED)
        
        # Si un XSLT est déjà chargé, proposer d'appliquer la transformation
        if self.xslt_transform is not None:
            if messagebox.askyesno("Appliquer XSLT", 
                                "Un fichier XSLT est chargé. Souhaitez-vous appliquer la transformation?"):
                self.apply_xslt()
    
    def highlight_xml(self):
        """Appliquer la coloration syntaxique à l'aperçu XML"""
        content = self.xml_text.get("1.0", tk.END)
        
        # Effacer tous les tags
        self.xml_text.tag_remove("tag", "1.0", tk.END)
        self.xml_text.tag_remove("attr", "1.0", tk.END)
        self.xml_text.tag_remove("string", "1.0", tk.END)
        self.xml_text.tag_remove("comment", "1.0", tk.END)
        
        # Configurer les tags
        self.xml_text.tag_configure("tag", foreground="#2980b9")
        self.xml_text.tag_configure("attr", foreground="#27ae60")
        self.xml_text.tag_configure("string", foreground="#e67e22")
        self.xml_text.tag_configure("comment", foreground="#7f8c8d")
        
        # Motifs de tags
        pos = "1.0"
        
        # Commentaires
        pattern = r"<!--[\s\S]*?-->"
        for match in re.finditer(pattern, content):
            start = content[:match.start()].count('\n') + 1
            start_col = match.start() - content[:match.start()].rfind('\n') - 1
            end = content[:match.end()].count('\n') + 1
            end_col = match.end() - content[:match.end()].rfind('\n') - 1
            self.xml_text.tag_add("comment", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Balises
        pattern = r"<[/!]?[\w:]+|/?>"
        for match in re.finditer(pattern, content):
            start = content[:match.start()].count('\n') + 1
            start_col = match.start() - content[:match.start()].rfind('\n') - 1
            end = content[:match.end()].count('\n') + 1
            end_col = match.end() - content[:match.end()].rfind('\n') - 1
            self.xml_text.tag_add("tag", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Attributs (correction du pattern)
        pattern = r'\s(\w+)=["\'"]'
        for match in re.finditer(pattern, content):
            start = content[:match.start(1)].count('\n') + 1
            start_col = match.start(1) - content[:match.start(1)].rfind('\n') - 1
            end = content[:match.end(1)].count('\n') + 1
            end_col = match.end(1) - content[:match.end(1)].rfind('\n') - 1
            self.xml_text.tag_add("attr", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Chaînes
        pattern = r'"[^"]*"|\'[^\']*\''
        for match in re.finditer(pattern, content):
            start = content[:match.start()].count('\n') + 1
            start_col = match.start() - content[:match.start()].rfind('\n') - 1
            end = content[:match.end()].count('\n') + 1
            end_col = match.end() - content[:match.end()].rfind('\n') - 1
            self.xml_text.tag_add("string", f"{start}.{start_col}", f"{end}.{end_col}")
    
    def highlight_html(self):
        """Appliquer la coloration syntaxique à l'aperçu HTML"""
        content = self.html_text.get("1.0", tk.END)
        
        # Effacer tous les tags
        self.html_text.tag_remove("tag", "1.0", tk.END)
        self.html_text.tag_remove("attr", "1.0", tk.END)
        self.html_text.tag_remove("string", "1.0", tk.END)
        self.html_text.tag_remove("comment", "1.0", tk.END)
        
        # Configurer les tags
        self.html_text.tag_configure("tag", foreground="#e74c3c")
        self.html_text.tag_configure("attr", foreground="#9b59b6")
        self.html_text.tag_configure("string", foreground="#f39c12")
        self.html_text.tag_configure("comment", foreground="#7f8c8d")
        
        # Motifs de tags
        pos = "1.0"
        
        # Commentaires
        pattern = r"<!--[\s\S]*?-->"
        for match in re.finditer(pattern, content):
            start = content[:match.start()].count('\n') + 1
            start_col = match.start() - content[:match.start()].rfind('\n') - 1
            end = content[:match.end()].count('\n') + 1
            end_col = match.end() - content[:match.end()].rfind('\n') - 1
            self.html_text.tag_add("comment", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Balises
        pattern = r"<[/!]?[\w:]+|/?>"
        for match in re.finditer(pattern, content):
            start = content[:match.start()].count('\n') + 1
            start_col = match.start() - content[:match.start()].rfind('\n') - 1
            end = content[:match.end()].count('\n') + 1
            end_col = match.end() - content[:match.end()].rfind('\n') - 1
            self.html_text.tag_add("tag", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Attributs
        pattern = r'\s(\w+)=["\'"]'
        for match in re.finditer(pattern, content):
            start = content[:match.start(1)].count('\n') + 1
            start_col = match.start(1) - content[:match.start(1)].rfind('\n') - 1
            end = content[:match.end(1)].count('\n') + 1
            end_col = match.end(1) - content[:match.end(1)].rfind('\n') - 1
            self.html_text.tag_add("attr", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Chaînes
        pattern = r'"[^"]*"|\'[^\']*\''
        for match in re.finditer(pattern, content):
            start = content[:match.start()].count('\n') + 1
            start_col = match.start() - content[:match.start()].rfind('\n') - 1
            end = content[:match.end()].count('\n') + 1
            end_col = match.end() - content[:match.end()].rfind('\n') - 1
            self.html_text.tag_add("string", f"{start}.{start_col}", f"{end}.{end_col}")
    
    def count_elements(self, root):
        """Compter le nombre total d'éléments dans le document XML"""
        count = 1  # Compter l'élément racine
        for child in root:
            count += self.count_elements(child)
        return count

    def execute_xpath(self):
        """Exécuter la requête XPath et afficher les résultats"""
        xpath_query = self.xpath_var.get().strip()
        
        if not xpath_query:
            messagebox.showinfo("Information", "Veuillez entrer une requête XPath")
            return
            
        if not self.xml_root:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XML")
            return
        
        # Ajouter à l'historique
        if xpath_query not in self.history:
            self.history.append(xpath_query)
            self.history_index = len(self.history) - 1
            self.refresh_history_list()
            self.save_settings()  # Sauvegarder l'historique
        
        try:
            self.update_status(f"Exécution de la requête: {xpath_query}")
            
            # Exécuter la requête dans un thread séparé
            def execute_query_thread():
                try:
                    results = self.xml_tree.xpath(xpath_query)
                    self.root.after(0, lambda: self.display_results(results, xpath_query))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erreur XPath", 
                        f"Erreur dans la requête XPath:\n{str(e)}"
                    ))
                    self.root.after(0, lambda: self.update_status(f"Erreur XPath: {str(e)}"))
            
            threading.Thread(target=execute_query_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution de la requête XPath: {str(e)}")
            self.update_status(f"Erreur de requête: {str(e)}")

    def display_results(self, results, query):
        """Afficher les résultats d'une requête XPath"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        # Afficher l'info sur la requête
        self.results_text.insert(tk.END, f"Requête XPath: {query}\n", "heading")
        self.results_text.insert(tk.END, f"Nombre de résultats: {len(results)}\n\n", "info")
        
        # Configuration des styles de texte
        self.results_text.tag_configure("heading", font=("Segoe UI", 12, "bold"), foreground=self.colors["primary"])
        self.results_text.tag_configure("info", font=("Segoe UI", 10), foreground=self.colors["secondary"])
        self.results_text.tag_configure("element", font=("Consolas", 10), foreground=self.colors["accent"])
        self.results_text.tag_configure("attribute", font=("Consolas", 10), foreground="#9b59b6")
        self.results_text.tag_configure("text", font=("Consolas", 10), foreground=self.colors["text"])
        
        if not results:
            self.results_text.insert(tk.END, "Aucun résultat trouvé", "info")
        else:
            for i, result in enumerate(results):
                # Déterminer le type de résultat
                if isinstance(result, etree._Element):
                    # C'est un élément XML
                    self.results_text.insert(tk.END, f"Résultat {i+1}: ", "heading")
                    self.results_text.insert(tk.END, f"Élément <{result.tag}>\n", "element")
                    
                    # Attributs
                    if result.attrib:
                        self.results_text.insert(tk.END, "  Attributs:\n", "info")
                        for name, value in result.attrib.items():
                            self.results_text.insert(tk.END, f"    {name}=\"{value}\"\n", "attribute")
                    
                    # Texte
                    if result.text and result.text.strip():
                        self.results_text.insert(tk.END, "  Texte:\n", "info")
                        self.results_text.insert(tk.END, f"    {result.text.strip()}\n", "text")
                    
                    # Sous-éléments (juste le nombre)
                    children = list(result)
                    if children:
                        self.results_text.insert(tk.END, f"  Sous-éléments: {len(children)}\n", "info")
                    
                    # XML complet
                    self.results_text.insert(tk.END, "  XML:\n", "info")
                    xml_string = etree.tostring(result, pretty_print=True, encoding='unicode')
                    self.results_text.insert(tk.END, f"{xml_string}\n\n", "text")
                    
                elif isinstance(result, etree._ElementUnicodeResult) or isinstance(result, str):
                    # C'est un texte ou une valeur
                    self.results_text.insert(tk.END, f"Résultat {i+1}: ", "heading")
                    self.results_text.insert(tk.END, "Valeur\n", "info")
                    self.results_text.insert(tk.END, f"  {result}\n\n", "text")
                    
                elif isinstance(result, bool) or isinstance(result, float) or isinstance(result, int):
                    # C'est une valeur booléenne ou numérique
                    self.results_text.insert(tk.END, f"Résultat {i+1}: ", "heading")
                    self.results_text.insert(tk.END, f"Valeur ({type(result).__name__})\n", "info")
                    self.results_text.insert(tk.END, f"  {result}\n\n", "text")
                    
                else:
                    # Type inconnu, afficher la représentation en chaîne
                    self.results_text.insert(tk.END, f"Résultat {i+1}: ", "heading")
                    self.results_text.insert(tk.END, f"Type: {type(result).__name__}\n", "info")
                    self.results_text.insert(tk.END, f"  {str(result)}\n\n", "text")
        
        self.results_text.config(state=tk.DISABLED)
        
        # Passer à l'onglet des résultats
        self.results_notebook.select(0)  # Sélectionner l'onglet des résultats
        
        self.update_status(f"Requête exécutée: {len(results)} résultat(s)")

    def apply_xslt(self):
        """Appliquer la transformation XSLT au document XML"""
        if not self.xml_tree:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XML")
            return
            
        if not self.xslt_transform:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XSLT")
            return
        
        try:
            self.update_status("Application de la transformation XSLT...")
            
            # Appliquer la transformation dans un thread séparé
            def transform_thread():
                try:
                    result = self.xslt_transform(self.xml_tree)
                    html_string = str(result)
                    
                    # Mettre à jour l'interface depuis le thread principal
                    self.root.after(0, lambda: self.display_html(html_string))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erreur XSLT", 
                        f"Erreur lors de la transformation XSLT:\n{str(e)}"
                    ))
                    self.root.after(0, lambda: self.update_status(f"Erreur XSLT: {str(e)}"))
            
            threading.Thread(target=transform_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la transformation XSLT: {str(e)}")
            self.update_status(f"Erreur XSLT: {str(e)}")

    def display_html(self, html_string):
        """Afficher le résultat HTML d'une transformation XSLT"""
        self.html_text.config(state=tk.NORMAL)
        self.html_text.delete("1.0", tk.END)
        self.html_text.insert(tk.END, html_string)
        
        # Appliquer la coloration syntaxique HTML
        self.highlight_html()
        
        self.html_text.config(state=tk.DISABLED)
        
        # Passer à l'onglet HTML
        self.results_notebook.select(2)  # Sélectionner l'onglet HTML
        
        self.update_status("Transformation XSLT appliquée avec succès")

    def preview_html(self):
        """Prévisualiser le HTML dans un navigateur avec mise en forme"""
        if self.html_text.get("1.0", tk.END).strip() == "":
            messagebox.showinfo("Information", "Appliquez d'abord une transformation XSLT")
            return
        
        # Créer un fichier temporaire avec mise en forme basique
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; margin: 10px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: {self.colors['primary']}; color: white; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {self.html_text.get("1.0", tk.END)}
            </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
            f.write(html_content.encode('utf-8'))
            temp_path = f.name
        
        webbrowser.open('file://' + temp_path)
        self.update_status("Aperçu HTML amélioré dans le navigateur")

    def save_html(self):
        """Enregistrer le résultat HTML dans un fichier"""
        if self.html_text.get("1.0", tk.END).strip() == "":
            messagebox.showinfo("Information", "Appliquez d'abord une transformation XSLT")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("Fichiers HTML", "*.html"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.html_text.get("1.0", tk.END))
            
            self.update_status(f"HTML enregistré: {os.path.basename(file_path)}")
            messagebox.showinfo("Succès", "Fichier HTML enregistré avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement du fichier HTML: {str(e)}")
            self.update_status(f"Erreur d'enregistrement: {str(e)}")

   
    
    def export_to_pdf(self):
        """Solution PDF locale avec Playwright"""
        try:
            html_content = self.html_text.get("1.0", tk.END)
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf")
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_content)
                page.pdf(path=file_path, format='A4')
                browser.close()
                
            self.update_status(f"PDF généré : {file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec Playwright : {str(e)}")
    def add_to_favorites(self):
        """Ajouter la requête XPath actuelle aux favoris"""
        xpath_query = self.xpath_var.get().strip()
        
        if not xpath_query:
            messagebox.showinfo("Information", "Veuillez entrer une requête XPath")
            return
        
        if xpath_query in self.favorites:
            messagebox.showinfo("Information", "Cette requête est déjà dans vos favoris")
            return
        
        # Ajouter aux favoris
        self.favorites.append(xpath_query)
        self.refresh_favorites_list()
        self.save_settings()
        
        self.update_status(f"Requête ajoutée aux favoris: {xpath_query}")

    def remove_favorite(self):
        """Supprimer la requête XPath sélectionnée des favoris"""
        selected = self.favorites_list.curselection()
        
        if not selected:
            messagebox.showinfo("Information", "Veuillez sélectionner un favori à supprimer")
            return
        
        index = selected[0]
        xpath_query = self.favorites[index]
        
        # Supprimer des favoris
        self.favorites.pop(index)
        self.refresh_favorites_list()
        self.save_settings()
        
        self.update_status(f"Favori supprimé: {xpath_query}")

    def load_from_favorites(self, event):
        """Charger une requête XPath depuis les favoris"""
        selected = self.favorites_list.curselection()
        
        if not selected:
            if event:  # Si événement de liste, ne rien faire
                return
            messagebox.showinfo("Information", "Veuillez sélectionner un favori")
            return
        
        index = selected[0]
        xpath_query = self.favorites[index]
        
        # Mettre à jour l'entrée XPath
        self.xpath_var.set(xpath_query)
        
        # Exécuter la requête si un fichier XML est chargé
        if self.xml_root:
            self.execute_xpath()
        
        self.update_status(f"Favori chargé: {xpath_query}")

    def refresh_favorites_list(self):
        """Mettre à jour la liste des favoris dans l'interface"""
        self.favorites_list.delete(0, tk.END)
        
        for favorite in self.favorites:
            self.favorites_list.insert(tk.END, favorite)

    def history_up(self, event):
        """Naviguer dans l'historique vers le haut"""
        if not self.history:
            return
        
        if self.history_index > 0:
            self.history_index -= 1
            self.xpath_var.set(self.history[self.history_index])

    def history_down(self, event):
        """Naviguer dans l'historique vers le bas"""
        if not self.history:
            return
        
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.xpath_var.set(self.history[self.history_index])
        else:
            # À la fin de l'historique, effacer l'entrée
            self.xpath_var.set("")

    def load_from_history(self, event):
        """Charger une requête XPath depuis l'historique"""
        selected = self.history_list.curselection()
        
        if not selected:
            if event:  # Si événement de liste, ne rien faire
                return
            messagebox.showinfo("Information", "Veuillez sélectionner une entrée de l'historique")
            return
        
        index = selected[0]
        xpath_query = self.history[index]
        
        # Mettre à jour l'entrée XPath
        self.xpath_var.set(xpath_query)
        self.history_index = index
        
        # Exécuter la requête si un fichier XML est chargé
        if self.xml_root:
            self.execute_xpath()
        
        self.update_status(f"Requête chargée depuis l'historique: {xpath_query}")

    def refresh_history_list(self):
        """Mettre à jour la liste de l'historique dans l'interface"""
        self.history_list.delete(0, tk.END)
        
        for query in self.history:
            self.history_list.insert(tk.END, query)

    def clear_history(self):
        """Effacer tout l'historique des requêtes"""
        if not self.history:
            return
        
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment effacer tout l'historique?"):
            self.history = []
            self.history_index = -1
            self.refresh_history_list()
            self.save_settings()
            
            self.update_status("Historique effacé")

    def copy_results(self):
        """Copier les résultats dans le presse-papiers"""
        if self.results_notebook.index("current") == 0:  # Onglet résultats
            text = self.results_text.get("1.0", tk.END)
        elif self.results_notebook.index("current") == 1:  # Onglet XML
            text = self.xml_text.get("1.0", tk.END)
        elif self.results_notebook.index("current") == 2:  # Onglet HTML
            text = self.html_text.get("1.0", tk.END)
        else:
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        self.update_status("Contenu copié dans le presse-papiers")

    def save_results(self):
        """Enregistrer les résultats dans un fichier texte"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            if self.results_notebook.index("current") == 0:  # Onglet résultats
                text = self.results_text.get("1.0", tk.END)
            elif self.results_notebook.index("current") == 1:  # Onglet XML
                text = self.xml_text.get("1.0", tk.END)
            elif self.results_notebook.index("current") == 2:  # Onglet HTML
                text = self.html_text.get("1.0", tk.END)
            else:
                return
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.update_status(f"Résultats enregistrés: {os.path.basename(file_path)}")
            messagebox.showinfo("Succès", "Résultats enregistrés avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des résultats: {str(e)}")
            self.update_status(f"Erreur d'enregistrement: {str(e)}")

    def show_xml_tree(self):
        """Afficher l'arborescence XML dans une nouvelle fenêtre"""
        if not self.xml_root:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XML")
            return
        
        tree_window = tk.Toplevel(self.root)
        tree_window.title("Arborescence XML")
        tree_window.geometry("800x600")
        tree_window.minsize(600, 400)
        
        # Configuration du style
        tree_window.configure(bg=self.colors["background"])
        
        # Titre
        title_frame = ttk.Frame(tree_window, style="TFrame")
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(title_frame, text="Arborescence XML", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_frame, text=os.path.basename(self.current_file), 
                style="Subheader.TLabel").pack(side=tk.RIGHT)
        
        # Arborescence
        tree_frame = ttk.Frame(tree_window, style="Card.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Créer l'arborescence
        xml_tree = ttk.Treeview(tree_frame)
        xml_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(xml_tree, orient="vertical", command=xml_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=xml_tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        xml_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Colonnes
        xml_tree["columns"] = ("value", "attributes")
        xml_tree.column("#0", width=250, minwidth=150)
        xml_tree.column("value", width=200, minwidth=100)
        xml_tree.column("attributes", width=300, minwidth=150)
        
        xml_tree.heading("#0", text="Élément")
        xml_tree.heading("value", text="Valeur")
        xml_tree.heading("attributes", text="Attributs")
        
        # Remplir l'arborescence
        def fill_tree(parent_item, element):
            # Préparer le texte des attributs
            attrs = ""
            if element.attrib:
                attrs = ", ".join([f"{k}=\"{v}\"" for k, v in element.attrib.items()])
            
            # Préparer la valeur (texte de l'élément)
            value = ""
            if element.text and element.text.strip():
                value = element.text.strip()
                if len(value) > 100:  # Tronquer si trop long
                    value = value[:97] + "..."
            
            # Insérer l'élément dans l'arborescence
            item = xml_tree.insert(parent_item, "end", text=element.tag, values=(value, attrs))
            
            # Insérer les enfants
            for child in element:
                fill_tree(item, child)
        
        # Remplir à partir de la racine
        fill_tree("", self.xml_root)
        
        # Ouvrir automatiquement les premiers niveaux
        xml_tree.item(xml_tree.get_children("")[0], open=True)
        
        self.update_status("Arborescence XML affichée")

    def show_xml_raw(self):
        """Afficher le XML brut dans une nouvelle fenêtre"""
        if not self.xml_root:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XML")
            return
        
        raw_window = tk.Toplevel(self.root)
        raw_window.title("XML Brut")
        raw_window.geometry("800x600")
        raw_window.minsize(600, 400)
        
        # Configuration du style
        raw_window.configure(bg=self.colors["background"])
        
        # Titre
        title_frame = ttk.Frame(raw_window, style="TFrame")
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(title_frame, text="XML Brut", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_frame, text=os.path.basename(self.current_file), 
                style="Subheader.TLabel").pack(side=tk.RIGHT)
        
        # Boutons
        button_frame = ttk.Frame(raw_window, style="TFrame")
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        ttk.Button(button_frame, text="Copier tout", 
                command=lambda: raw_window.clipboard_append(xml_text.get("1.0", tk.END))).pack(side=tk.LEFT)
        
        # Zone de texte
        xml_frame = ttk.Frame(raw_window, style="Card.TFrame")
        xml_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        xml_text = scrolledtext.ScrolledText(xml_frame, wrap=tk.NONE, 
                                            font=("Consolas", 11),
                                            background=self.colors["card"],
                                            foreground=self.colors["text"])
        xml_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Remplir le contenu XML
        xml_string = etree.tostring(self.xml_root, pretty_print=True, encoding='unicode')
        xml_text.insert(tk.END, xml_string)
        
        # Appliquer la coloration syntaxique
        # Configurer les tags
        xml_text.tag_configure("tag", foreground="#2980b9")
        xml_text.tag_configure("attr", foreground="#27ae60")
        xml_text.tag_configure("string", foreground="#e67e22")
        xml_text.tag_configure("comment", foreground="#7f8c8d")
        
        # Commentaires
        pattern = r"<!--[\s\S]*?-->"
        for match in re.finditer(pattern, xml_string):
            start = xml_string[:match.start()].count('\n') + 1
            start_col = match.start() - xml_string[:match.start()].rfind('\n') - 1
            end = xml_string[:match.end()].count('\n') + 1
            end_col = match.end() - xml_string[:match.end()].rfind('\n') - 1
            xml_text.tag_add("comment", f"{start}.{start_col}", f"{end}.{end_col}")
    
        # Balises
        pattern = r"<[/!]?[\w:]+|/?>"
        for match in re.finditer(pattern, xml_string):
            start = xml_string[:match.start()].count('\n') + 1
            start_col = match.start() - xml_string[:match.start()].rfind('\n') - 1
            end = xml_string[:match.end()].count('\n') + 1
            end_col = match.end() - xml_string[:match.end()].rfind('\n') - 1
            xml_text.tag_add("tag", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Attributs
        pattern = r'\s(\w+)=["\'"]'
        for match in re.finditer(pattern, xml_string):
            start = xml_string[:match.start(1)].count('\n') + 1
            start_col = match.start(1) - xml_string[:match.start(1)].rfind('\n') - 1
            end = xml_string[:match.end(1)].count('\n') + 1
            end_col = match.end(1) - xml_string[:match.end(1)].rfind('\n') - 1
            xml_text.tag_add("attr", f"{start}.{start_col}", f"{end}.{end_col}")
        
        # Chaînes
        pattern = r'"[^"]*"|\'[^\']*\''
        for match in re.finditer(pattern, xml_string):
            start = xml_string[:match.start()].count('\n') + 1
            start_col = match.start() - xml_string[:match.start()].rfind('\n') - 1
            end = xml_string[:match.end()].count('\n') + 1
            end_col = match.end() - xml_string[:match.end()].rfind('\n') - 1
            xml_text.tag_add("string", f"{start}.{start_col}", f"{end}.{end_col}")
        
        self.update_status("XML brut affiché")

    def show_xpath_reference(self):
        """Afficher une référence des expressions XPath courantes"""
        ref_window = tk.Toplevel(self.root)
        ref_window.title("Référence XPath")
        ref_window.geometry("900x600")
        ref_window.minsize(600, 400)
        
        # Configuration du style
        ref_window.configure(bg=self.colors["background"])
        
        # Titre
        title_frame = ttk.Frame(ref_window, style="TFrame")
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(title_frame, text="Référence des expressions XPath", style="Header.TLabel").pack(side=tk.LEFT)
        
        # Contenu avec défilement
        content_frame = ttk.Frame(ref_window, style="Card.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        ref_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                        font=("Segoe UI", 11),
                                        background=self.colors["card"],
                                        foreground=self.colors["text"])
        ref_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configurer les styles
        ref_text.tag_configure("heading", font=("Segoe UI", 14, "bold"), foreground=self.colors["primary"])
        ref_text.tag_configure("subheading", font=("Segoe UI", 12, "bold"), foreground=self.colors["secondary"])
        ref_text.tag_configure("code", font=("Consolas", 10), background="#f0f0f0", foreground=self.colors["accent"])
        ref_text.tag_configure("description", font=("Segoe UI", 10))
        
        # Contenu de la référence
        ref_text.insert(tk.END, "Guide de référence XPath\n\n", "heading")
        
        ref_text.insert(tk.END, "Expressions XPath de base\n", "subheading")
        ref_text.insert(tk.END, "/", "code")
        ref_text.insert(tk.END, " - Racine du document\n", "description")
        ref_text.insert(tk.END, "/element", "code")
        ref_text.insert(tk.END, " - Élément enfant direct de la racine\n", "description")
        ref_text.insert(tk.END, "//element", "code")
        ref_text.insert(tk.END, " - Élément à n'importe quel niveau\n", "description")
        ref_text.insert(tk.END, "./element", "code")
        ref_text.insert(tk.END, " - Élément enfant du contexte actuel\n", "description")
        ref_text.insert(tk.END, "../element", "code")
        ref_text.insert(tk.END, " - Élément au niveau parent\n", "description")
        ref_text.insert(tk.END, "@attribute", "code")
        ref_text.insert(tk.END, " - Attribut de l'élément actuel\n\n", "description")
        
        ref_text.insert(tk.END, "Prédicats\n", "subheading")
        ref_text.insert(tk.END, "element[1]", "code")
        ref_text.insert(tk.END, " - Premier élément (les index commencent à 1)\n", "description")
        ref_text.insert(tk.END, "element[last()]", "code")
        ref_text.insert(tk.END, " - Dernier élément\n", "description")
        ref_text.insert(tk.END, "element[@attr]", "code")
        ref_text.insert(tk.END, " - Élément avec l'attribut spécifié\n", "description")
        ref_text.insert(tk.END, "element[@attr='value']", "code")
        ref_text.insert(tk.END, " - Élément où l'attribut a la valeur spécifiée\n", "description")
        ref_text.insert(tk.END, "element[child]", "code")
        ref_text.insert(tk.END, " - Élément qui a un enfant spécifié\n\n", "description")
        
        ref_text.insert(tk.END, "Caractères joker\n", "subheading")
        ref_text.insert(tk.END, "*", "code")
        ref_text.insert(tk.END, " - N'importe quel élément\n", "description")
        ref_text.insert(tk.END, "@*", "code")
        ref_text.insert(tk.END, " - N'importe quel attribut\n", "description")
        ref_text.insert(tk.END, "node()", "code")
        ref_text.insert(tk.END, " - N'importe quel nœud\n\n", "description")
        
        ref_text.insert(tk.END, "Opérateurs\n", "subheading")
        ref_text.insert(tk.END, "=, !=, <, >, <=, >=", "code")
        ref_text.insert(tk.END, " - Comparaisons\n", "description")
        ref_text.insert(tk.END, "and, or, not()", "code")
        ref_text.insert(tk.END, " - Opérateurs logiques\n", "description")
        ref_text.insert(tk.END, "+, -, *, div, mod", "code")
        ref_text.insert(tk.END, " - Opérateurs arithmétiques\n\n", "description")
        
        ref_text.insert(tk.END, "Axes\n", "subheading")
        ref_text.insert(tk.END, "child::", "code")
        ref_text.insert(tk.END, " - Enfants directs (par défaut)\n", "description")
        ref_text.insert(tk.END, "descendant::", "code")
        ref_text.insert(tk.END, " - Tous les descendants\n", "description")
        ref_text.insert(tk.END, "parent::", "code")
        ref_text.insert(tk.END, " - Le parent direct\n", "description")
        ref_text.insert(tk.END, "ancestor::", "code")
        ref_text.insert(tk.END, " - Tous les ancêtres\n", "description")
        ref_text.insert(tk.END, "following-sibling::", "code")
        ref_text.insert(tk.END, " - Éléments frères qui suivent\n", "description")
        ref_text.insert(tk.END, "preceding-sibling::", "code")
        ref_text.insert(tk.END, " - Éléments frères qui précèdent\n", "description")
        ref_text.insert(tk.END, "self::", "code")
        ref_text.insert(tk.END, " - L'élément actuel\n\n", "description")
        
        ref_text.insert(tk.END, "Fonctions\n", "subheading")
        ref_text.insert(tk.END, "count(nodes)", "code")
        ref_text.insert(tk.END, " - Nombre de nœuds\n", "description")
        ref_text.insert(tk.END, "sum(nodes)", "code")
        ref_text.insert(tk.END, " - Somme des valeurs numériques\n", "description")
        ref_text.insert(tk.END, "contains(str1, str2)", "code")
        ref_text.insert(tk.END, " - Vérifie si str1 contient str2\n", "description")
        ref_text.insert(tk.END, "starts-with(str1, str2)", "code")
        ref_text.insert(tk.END, " - Vérifie si str1 commence par str2\n", "description")
        ref_text.insert(tk.END, "substring(str, start, len)", "code")
        ref_text.insert(tk.END, " - Extrait une sous-chaîne\n", "description")
        ref_text.insert(tk.END, "string-length(str)", "code")
        ref_text.insert(tk.END, " - Longueur de la chaîne\n", "description")
        ref_text.insert(tk.END, "normalize-space(str)", "code")
        ref_text.insert(tk.END, " - Normalise les espaces\n", "description")
        ref_text.insert(tk.END, "translate(str, chars, trans)", "code")
        ref_text.insert(tk.END, " - Traduit des caractères\n\n", "description")
        
        ref_text.insert(tk.END, "Exemples pratiques\n", "subheading")
        ref_text.insert(tk.END, "//book[author='John Doe']", "code")
        ref_text.insert(tk.END, " - Tous les livres écrits par John Doe\n", "description")
        ref_text.insert(tk.END, "//employee[@id='123']//address", "code")
        ref_text.insert(tk.END, " - Adresses de l'employé avec id=123\n", "description")
        ref_text.insert(tk.END, "//product[price > 100]", "code")
        ref_text.insert(tk.END, " - Produits coûtant plus de 100\n", "description")
        ref_text.insert(tk.END, "//title[contains(., 'XML')]", "code")
        ref_text.insert(tk.END, " - Titres contenant 'XML'\n", "description")
        ref_text.insert(tk.END, "count(//book[publisher='Acme'])", "code")
        ref_text.insert(tk.END, " - Nombre de livres publiés par Acme\n", "description")
        ref_text.insert(tk.END, "//book[position() <= 3]", "code")
        ref_text.insert(tk.END, " - Les trois premiers livres\n", "description")
        
        ref_text.config(state=tk.DISABLED)
        self.update_status("Référence XPath affichée")

    def show_xslt_reference(self):
        """Afficher une référence des éléments XSLT courants"""
        ref_window = tk.Toplevel(self.root)
        ref_window.title("Référence XSLT")
        ref_window.geometry("900x600")
        ref_window.minsize(600, 400)
        
        # Configuration du style
        ref_window.configure(bg=self.colors["background"])
        
        # Titre
        title_frame = ttk.Frame(ref_window, style="TFrame")
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(title_frame, text="Référence des éléments XSLT", style="Header.TLabel").pack(side=tk.LEFT)
        
        # Contenu avec défilement
        content_frame = ttk.Frame(ref_window, style="Card.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        ref_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                        font=("Segoe UI", 11),
                                        background=self.colors["card"],
                                        foreground=self.colors["text"])
        ref_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configurer les styles
        ref_text.tag_configure("heading", font=("Segoe UI", 14, "bold"), foreground=self.colors["primary"])
        ref_text.tag_configure("subheading", font=("Segoe UI", 12, "bold"), foreground=self.colors["secondary"])
        ref_text.tag_configure("element", font=("Consolas", 10, "bold"), foreground="#e74c3c")
        ref_text.tag_configure("code", font=("Consolas", 10), background="#f0f0f0")
        ref_text.tag_configure("description", font=("Segoe UI", 10))
        
        # Contenu de la référence
        ref_text.insert(tk.END, "Guide de référence XSLT\n\n", "heading")
        
        ref_text.insert(tk.END, "Structure de base d'un document XSLT\n", "subheading")
        ref_text.insert(tk.END, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n", "code")
        ref_text.insert(tk.END, "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">\n", "code")
        ref_text.insert(tk.END, "  <xsl:output method=\"html\" indent=\"yes\"/>\n\n", "code")
        ref_text.insert(tk.END, "  <xsl:template match=\"/\">\n", "code")
        ref_text.insert(tk.END, "    <!-- Contenu de la transformation -->\n", "code")
        ref_text.insert(tk.END, "  </xsl:template>\n", "code")
        ref_text.insert(tk.END, "</xsl:stylesheet>\n\n", "code")
        
        ref_text.insert(tk.END, "Éléments XSLT principaux\n", "subheading")
        
        ref_text.insert(tk.END, "<xsl:template>", "element")
        ref_text.insert(tk.END, "\nDéfinit un modèle pour transformer une partie du document XML.\nAttributs: match, name, mode, priority\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:apply-templates>", "element")
        ref_text.insert(tk.END, "\nApplique les modèles aux enfants de l'élément actuel ou aux nœuds sélectionnés.\nAttributs: select, mode\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:value-of>", "element")
        ref_text.insert(tk.END, "\nInsère la valeur d'une expression.\nAttributs: select, disable-output-escaping\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:for-each>", "element")
        ref_text.insert(tk.END, "\nBoucle sur un ensemble de nœuds.\nAttributs: select\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:if>", "element")
        ref_text.insert(tk.END, "\nTraitement conditionnel.\nAttributs: test\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:choose>", "element")
        ref_text.insert(tk.END, "\nGroupe multiple conditions (contient xsl:when et xsl:otherwise).\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:when>", "element")
        ref_text.insert(tk.END, "\nBranche conditionnelle (utilisée dans xsl:choose).\nAttributs: test\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:otherwise>", "element")
        ref_text.insert(tk.END, "\nBranche par défaut (utilisée dans xsl:choose).\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:variable>", "element")
        ref_text.insert(tk.END, "\nDéfinit une variable.\nAttributs: name, select\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:param>", "element")
        ref_text.insert(tk.END, "\nDéfinit un paramètre.\nAttributs: name, select\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:with-param>", "element")
        ref_text.insert(tk.END, "\nPasse un paramètre à un modèle appelé.\nAttributs: name, select\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:call-template>", "element")
        ref_text.insert(tk.END, "\nAppelle un modèle nommé.\nAttributs: name\n\n", "description")
        
        ref_text.insert(tk.END, "<xsl:output>", "element")
        ref_text.insert(tk.END, "\nSpécifie le format de sortie.\nAttributs: method, indent, encoding, omit-xml-declaration\n\n", "description")
        
        ref_text.insert(tk.END, "Exemple pratique\n", "subheading")
        ref_text.insert(tk.END, "<!-- Transformation d'un catalogue de livres en HTML -->\n", "code")
        ref_text.insert(tk.END, "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">\n", "code")
        ref_text.insert(tk.END, "  <xsl:output method=\"html\" indent=\"yes\"/>\n\n", "code")
        ref_text.insert(tk.END, "  <xsl:template match=\"/\">\n", "code")
        ref_text.insert(tk.END, "    <html>\n", "code")
        ref_text.insert(tk.END, "      <head>\n", "code")
        ref_text.insert(tk.END, "        <title>Catalogue de Livres</title>\n", "code")
        ref_text.insert(tk.END, "      </head>\n", "code")
        ref_text.insert(tk.END, "      <body>\n", "code")
        ref_text.insert(tk.END, "        <h1>Catalogue de Livres</h1>\n", "code")
        ref_text.insert(tk.END, "        <table border=\"1\">\n", "code")
        ref_text.insert(tk.END, "          <tr>\n", "code")
        ref_text.insert(tk.END, "            <th>Titre</th>\n", "code")
        ref_text.insert(tk.END, "            <th>Auteur</th>\n", "code")
        ref_text.insert(tk.END, "            <th>Prix</th>\n", "code")
        ref_text.insert(tk.END, "          </tr>\n", "code")
        ref_text.insert(tk.END, "          <xsl:for-each select=\"catalog/book\">\n", "code")
        ref_text.insert(tk.END, "            <tr>\n", "code")
        ref_text.insert(tk.END, "              <td><xsl:value-of select=\"title\"/></td>\n", "code")
        ref_text.insert(tk.END, "              <td><xsl:value-of select=\"author\"/></td>\n", "code")
        ref_text.insert(tk.END, "              <td>\n", "code")
        ref_text.insert(tk.END, "                <xsl:choose>\n", "code")
        ref_text.insert(tk.END, "                  <xsl:when test=\"price > 30\">\n", "code")
        ref_text.insert(tk.END, "                    <span style=\"color:red;\"><xsl:value-of select=\"price\"/>€</span>\n", "code")
        ref_text.insert(tk.END, "                  </xsl:when>\n", "code")
        ref_text.insert(tk.END, "                  <xsl:otherwise>\n", "code")
        ref_text.insert(tk.END, "                    <xsl:value-of select=\"price\"/>€\n", "code")
        ref_text.insert(tk.END, "                  </xsl:otherwise>\n", "code")
        ref_text.insert(tk.END, "                </xsl:choose>\n", "code")
        ref_text.insert(tk.END, "              </td>\n", "code")
        ref_text.insert(tk.END, "            </tr>\n", "code")
        ref_text.insert(tk.END, "          </xsl:for-each>\n", "code")
        ref_text.insert(tk.END, "        </table>\n", "code")
        ref_text.insert(tk.END, "      </body>\n", "code")
        ref_text.insert(tk.END, "    </html>\n", "code")
        ref_text.insert(tk.END, "  </xsl:template>\n", "code")
        ref_text.insert(tk.END, "</xsl:stylesheet>\n", "code")
        
        ref_text.config(state=tk.DISABLED)
        self.update_status("Référence XSLT affichée")

    def show_about(self):
        """Afficher les informations à propos de l'application"""
        about_window = tk.Toplevel(self.root)
        about_window.title("À propos")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        
        # Configuration du style
        about_window.configure(bg=self.colors["background"])
        
        # Contenu
        content_frame = ttk.Frame(about_window, style="Card.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo (ici représenté par un texte, pourrait être remplacé par une image)
        logo_frame = ttk.Frame(content_frame, style="Card.TFrame")
        logo_frame.pack(pady=15)
        
        logo_label = ttk.Label(logo_frame, text="XML Explorer", 
                            font=("Segoe UI", 36, "bold"),
                            foreground=self.colors["secondary"],
                            background=self.colors["card"])
        logo_label.pack()
        
        logo_label2 = ttk.Label(logo_frame, text="", 
                            font=("Segoe UI", 18),
                            foreground=self.colors["primary"],
                            background=self.colors["card"])
        logo_label2.pack()
        
        # Informations sur l'application
        info_frame = ttk.Frame(content_frame, style="Card.TFrame")
        info_frame.pack(fill=tk.X, pady=15)
        
        version_label = ttk.Label(info_frame, text="Version 1.0", 
                                font=("Segoe UI", 10),
                                background=self.colors["card"])
        version_label.pack()
        
        desc_label = ttk.Label(info_frame, 
                            text="Outil d'exploration et de manipulation de documents XML\n"
                                "avec support des requêtes XPath et des transformations XSLT.",
                            font=("Segoe UI", 9),
                            justify=tk.CENTER,
                            wraplength=400,
                            background=self.colors["card"])
        desc_label.pack(pady=5)
        
        # Informations sur les technologies
        tech_frame = ttk.Frame(content_frame, style="Card.TFrame")
        tech_frame.pack(fill=tk.X, pady=5)
        
        tech_label = ttk.Label(tech_frame, 
                            text="Développé avec Python  tkinter",
                            font=("Segoe UI", 9),
                            background=self.colors["card"])
        tech_label.pack()
        
        # Copyright
        copyright_label = ttk.Label(content_frame, 
                                text="© 2025 XML Explorer",
                                font=("Segoe UI", 8),
                                foreground=self.colors["light_text"],
                                background=self.colors["card"])
        copyright_label.pack(side=tk.BOTTOM, pady=10)
        
        self.update_status("À propos affiché")

    def load_settings(self):
        """Charger les paramètres de l'application depuis un fichier JSON"""
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        
        # Paramètres par défaut
        default_settings = {
            "history": [],
            "favorites": [],
            "recent_files": [],
            "window_size": "1200x800"
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # Charger l'historique
                    if "history" in settings and isinstance(settings["history"], list):
                        self.history = settings["history"][-100:]  # Limiter à 100 entrées
                    
                    # Charger les favoris
                    if "favorites" in settings and isinstance(settings["favorites"], list):
                        self.favorites = settings["favorites"]
                    
                    # Charger la taille de la fenêtre
                    if "window_size" in settings:
                        self.root.geometry(settings["window_size"])
            else:
                # Créer le fichier de paramètres s'il n'existe pas
                self.save_settings()
                
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {str(e)}")
            # Utiliser les paramètres par défaut en cas d'erreur
            self.history = default_settings["history"]
            self.favorites = default_settings["favorites"]

    def save_settings(self):
        """Enregistrer les paramètres de l'application dans un fichier JSON"""
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        
        try:
            settings = {
                "history": self.history[-100:],  # Limiter à 100 entrées
                "favorites": self.favorites,
                "recent_files": [self.current_file] if self.current_file else [],
                "window_size": self.root.geometry()
            }
            
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur lors de l'enregistrement des paramètres: {str(e)}")
            messagebox.showwarning("Attention", 
                                f"Impossible d'enregistrer les paramètres: {str(e)}")

    # Point d'entrée de l'application
def main():
    root = tk.Tk()
    app = XPathExplorer(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_settings(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()