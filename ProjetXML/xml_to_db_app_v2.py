import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import mysql.connector
import xml.etree.ElementTree as ET
import os
import datetime

class XMLtoDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XML vers Base de Données MySQL")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables pour la connexion MySQL
        self.host = tk.StringVar(value="localhost")
        self.user = tk.StringVar()
        self.password = tk.StringVar()
        self.database = tk.StringVar()
        self.port = tk.StringVar(value="3306")
        
        self.xml_path = tk.StringVar()
        self.connection = None
        self.cursor = None
        
        # Interface utilisateur
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section connexion MySQL
        db_frame = ttk.LabelFrame(main_frame, text="Connexion MySQL", padding="10")
        db_frame.pack(fill=tk.X, pady=5)
        
        # Host
        host_frame = ttk.Frame(db_frame)
        host_frame.pack(fill=tk.X, pady=2)
        ttk.Label(host_frame, text="Host:", width=10).pack(side=tk.LEFT)
        ttk.Entry(host_frame, textvariable=self.host).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Port
        port_frame = ttk.Frame(db_frame)
        port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(port_frame, text="Port:", width=10).pack(side=tk.LEFT)
        ttk.Entry(port_frame, textvariable=self.port).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Utilisateur
        user_frame = ttk.Frame(db_frame)
        user_frame.pack(fill=tk.X, pady=2)
        ttk.Label(user_frame, text="Utilisateur:", width=10).pack(side=tk.LEFT)
        ttk.Entry(user_frame, textvariable=self.user).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Mot de passe
        pwd_frame = ttk.Frame(db_frame)
        pwd_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pwd_frame, text="Mot de passe:", width=10).pack(side=tk.LEFT)
        ttk.Entry(pwd_frame, textvariable=self.password, show="*").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Base de données
        db_name_frame = ttk.Frame(db_frame)
        db_name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(db_name_frame, text="Base de données:", width=10).pack(side=tk.LEFT)
        ttk.Entry(db_name_frame, textvariable=self.database).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Boutons de connexion
        btn_frame = ttk.Frame(db_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Connecter", command=self.connect_to_db).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(btn_frame, text="Créer Base de Données", command=self.create_database).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Section XML
        xml_frame = ttk.LabelFrame(main_frame, text="Fichier XML", padding="10")
        xml_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(xml_frame, text="Chemin du fichier XML:").pack(anchor=tk.W)
        
        xml_entry_frame = ttk.Frame(xml_frame)
        xml_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(xml_entry_frame, textvariable=self.xml_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(xml_entry_frame, text="Parcourir", command=self.browse_xml).pack(side=tk.RIGHT, padx=5)
        
        # Section Import
        import_frame = ttk.LabelFrame(main_frame, text="Importation", padding="10")
        import_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(import_frame, text="Importer XML vers la base de données", 
                  command=self.import_xml_to_db).pack(fill=tk.X, pady=5)
        
        # Zone de log
        log_frame = ttk.LabelFrame(main_frame, text="Journal", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, yscrollcommand=log_scroll.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)
        
        # Barre de statut
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_xml(self):
        xml_file = filedialog.askopenfilename(
            title="Sélectionner un fichier XML",
            filetypes=[("Fichiers XML", "*.xml"), ("Tous les fichiers", "*.*")]
        )
        if xml_file:
            self.xml_path.set(xml_file)
            self.log("Fichier XML sélectionné: " + xml_file)
    
    def create_database(self):
        """Crée une nouvelle base de données MySQL"""
        if not self.validate_connection_fields(check_database=False):
            return
            
        try:
            # Connexion au serveur MySQL sans spécifier de base de données
            temp_conn = mysql.connector.connect(
                host=self.host.get(),
                port=self.port.get(),
                user=self.user.get(),
                password=self.password.get()
            )
            
            temp_cursor = temp_conn.cursor()
            
            # Demander le nom de la nouvelle base de données
            db_name = tk.simpledialog.askstring("Création de base de données", 
                                              "Nom de la nouvelle base de données:")
            
            if not db_name:
                return
                
            # Création de la base de données
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            
            self.database.set(db_name)
            self.log(f"Base de données '{db_name}' créée avec succès.")
            
            # Fermer la connexion temporaire
            temp_cursor.close()
            temp_conn.close()
            
            # Se connecter à la nouvelle base de données
            self.connect_to_db()
            
        except mysql.connector.Error as err:
            self.log(f"Erreur MySQL: {err}")
            messagebox.showerror("Erreur MySQL", str(err))
    
    def validate_connection_fields(self, check_database=True):
        """Vérifie que les champs de connexion sont remplis"""
        if not self.host.get():
            messagebox.showerror("Erreur", "Veuillez spécifier un hôte.")
            return False
        if not self.user.get():
            messagebox.showerror("Erreur", "Veuillez spécifier un nom d'utilisateur.")
            return False
        if check_database and not self.database.get():
            messagebox.showerror("Erreur", "Veuillez spécifier une base de données.")
            return False
        return True
    
    def connect_to_db(self):
        """Établir une connexion à la base de données MySQL"""
        if not self.validate_connection_fields():
            return
        
        try:
            # Fermer la connexion existante si elle existe
            if self.connection:
                self.connection.close()
            
            # Établir une nouvelle connexion
            self.connection = mysql.connector.connect(
                host=self.host.get(),
                port=self.port.get(),
                user=self.user.get(),
                password=self.password.get(),
                database=self.database.get()
            )
            
            self.cursor = self.connection.cursor()
            self.log(f"Connecté à la base de données MySQL: {self.database.get()} sur {self.host.get()}")
            self.status_var.set(f"Connecté à {self.database.get()} sur {self.host.get()}")
            messagebox.showinfo("Connexion réussie", "Connexion à la base de données établie avec succès.")
        except mysql.connector.Error as err:
            self.log(f"Erreur de connexion MySQL: {err}")
            messagebox.showerror("Erreur de connexion", str(err))
    
    def import_xml_to_db(self):
        if not self.connection:
            messagebox.showerror("Erreur", "Veuillez d'abord vous connecter à une base de données.")
            return
        
        xml_path = self.xml_path.get()
        if not xml_path:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier XML.")
            return
        
        try:
            self.log("Analyse du fichier XML...")
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Récupérer le nom de la racine pour nommer la table
            table_name = root.tag
            self.log(f"Racine XML: {table_name}")
            
            # Analyser la structure XML et créer la table
            # On prend le premier élément enfant pour déterminer les colonnes
            if len(root) > 0:
                first_child = root[0]
                columns = []
                
                for child in first_child:
                    column_name = child.tag
                    columns.append(column_name)
                
                # Créer la table avec MySQL
                if columns:
                    # Supprimer la table si elle existe déjà
                    drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
                    self.cursor.execute(drop_table_sql)
                    
                    # Créer la nouvelle table
                    columns_sql = ", ".join([f"`{col}` TEXT" for col in columns])
                    create_table_sql = f"CREATE TABLE `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY, {columns_sql})"
                    self.cursor.execute(create_table_sql)
                    self.log(f"Table '{table_name}' créée avec les colonnes: {', '.join(columns)}")
                    
                    # Insérer les données
                    insert_count = 0
                    for item in root:
                        values = []
                        for col in columns:
                            # Chercher l'élément correspondant à cette colonne
                            element = item.find(col)
                            if element is not None and element.text:
                                values.append(element.text)
                            else:
                                values.append(None)  # Valeur NULL si l'élément n'existe pas
                        
                        placeholders = ", ".join(["%s" for _ in columns])
                        column_names = ", ".join([f"`{col}`" for col in columns])
                        insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"
                        self.cursor.execute(insert_sql, values)
                        insert_count += 1
                    
                    self.connection.commit()
                    self.log(f"{insert_count} enregistrements importés dans la table '{table_name}'.")
                    messagebox.showinfo("Importation réussie", f"{insert_count} enregistrements importés avec succès.")
                else:
                    self.log("Aucune colonne trouvée dans le premier élément enfant.")
                    messagebox.showwarning("Attention", "Aucune colonne n'a été trouvée dans le XML.")
            else:
                self.log("Le XML ne contient aucun élément enfant.")
                messagebox.showwarning("Attention", "Le XML ne contient aucun élément à importer.")
            
        except ET.ParseError as e:
            self.log(f"Erreur d'analyse XML: {str(e)}")
            messagebox.showerror("Erreur XML", f"Le fichier n'est pas un XML valide: {str(e)}")
        except mysql.connector.Error as e:
            self.log(f"Erreur MySQL: {str(e)}")
            messagebox.showerror("Erreur de base de données", str(e))
        except Exception as e:
            self.log(f"Erreur: {str(e)}")
            messagebox.showerror("Erreur", str(e))
    
    def log(self, message):
        """Ajoute un message au journal avec un horodatage"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLtoDatabaseApp(root)
    root.mainloop()
