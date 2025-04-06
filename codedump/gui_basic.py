import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import datetime
from codedump.codedump import concatenate_files, should_skip, get_file_info
import pyperclip
from PIL import Image, ImageTk

class CodeDumpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeDump GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)  # Tamaño mínimo para la ventana
        
        self.selected_directory = tk.StringVar(value="")
        self.dump_content = ""
        self.status_var = tk.StringVar(value="Listo")
        
        # Cargar iconos
        self.load_icons()
        
        # Crear frames principales
        self.create_top_frame()
        self.create_main_frame()
        self.create_bottom_frame()
        
        # Configurar redimensionamiento
        self.root.columnconfigure(0, weight=1)  # La columna principal se expande
        self.root.rowconfigure(1, weight=1)     # El main_frame se expande
    
    def load_icons(self):
        """Carga los iconos para carpetas y archivos"""
        try:
            # Crear iconos básicos si no existen imágenes
            # Icono de carpeta (cuadrado azul)
            folder_img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
            for i in range(16):
                for j in range(16):
                    if (i == 0 or i == 15 or j == 0 or j == 15 or 
                        (i == 5 and j <= 10) or (j == 10 and i <= 5)):
                        folder_img.putpixel((i, j), (0, 0, 128, 255))  # Azul
            
            # Icono de archivo (rectángulo verde)
            file_img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
            for i in range(16):
                for j in range(16):
                    if (i == 0 or i == 15 or j == 0 or j == 15 or 
                        (i == 4 and 2 <= j <= 13) or (i == 8 and 2 <= j <= 13) or (i == 12 and 2 <= j <= 13)):
                        file_img.putpixel((i, j), (0, 100, 0, 255))  # Verde oscuro
            
            # Convertir a PhotoImage
            self.folder_icon = ImageTk.PhotoImage(folder_img)
            self.file_icon = ImageTk.PhotoImage(file_img)
        except ImportError:
            # Si PIL no está disponible, usar None para los iconos
            self.folder_icon = None
            self.file_icon = None
            print("Aviso: PIL no instalado. No se mostrarán iconos.")
        except Exception as e:
            # En caso de cualquier otro error, usar None para los iconos
            self.folder_icon = None
            self.file_icon = None
            print(f"Error al cargar iconos: {e}")
        
    def create_top_frame(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky='ew')
        
        # Botón para seleccionar directorio
        select_dir_button = ttk.Button(top_frame, text="Seleccionar Directorio", command=self.select_directory)
        select_dir_button.pack(side=tk.LEFT, padx=5)
        
        # Botón para refrescar el directorio actual
        refresh_button = ttk.Button(top_frame, text="Refrescar", command=self.refresh_directory)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Etiqueta para mostrar la ruta seleccionada
        dir_label = ttk.Label(top_frame, textvariable=self.selected_directory)
        dir_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_main_frame(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky='nsew')
        
        # Crear un panel con separador ajustable
        panedwindow = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        panedwindow.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior para el Treeview
        tree_frame = ttk.Frame(panedwindow)
        panedwindow.add(tree_frame, weight=3)
        
        # Crear un Treeview para mostrar los archivos
        self.tree = ttk.Treeview(tree_frame)
        self.tree.heading('#0', text='Estructura de archivos', anchor='w')
        
        # Configurar las etiquetas para diferenciar archivos y carpetas
        self.tree.tag_configure('folder', foreground='navy')
        self.tree.tag_configure('file', foreground='darkgreen')
        self.tree.tag_configure('checked', foreground='black')
        self.tree.tag_configure('unchecked', foreground='gray')
        
        # Asociar el evento de clic al Treeview
        self.tree.bind("<Button-1>", self.toggle_check)
        
        # Añadir scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Colocar el Treeview y las barras de desplazamiento
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # Configurar el grid para que se expanda
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Frame inferior para el texto
        text_frame = ttk.Frame(panedwindow)
        panedwindow.add(text_frame, weight=1)
        
        # Añadir un área de texto para mostrar el resultado
        self.result_text = tk.Text(text_frame, wrap=tk.WORD, height=10, state='disabled')
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=text_scroll.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_bottom_frame(self):
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.grid(row=2, column=0, sticky='ew')
        
        # Botones
        buttons_frame = ttk.Frame(bottom_frame)
        buttons_frame.pack(side=tk.LEFT, fill=tk.X)
        
        # Botón para generar dump
        generate_button = ttk.Button(buttons_frame, text="Generar Dump", command=self.generate_dump)
        generate_button.pack(side=tk.LEFT, padx=5)
        
        # Botón para copiar al portapapeles
        copy_button = ttk.Button(buttons_frame, text="Copiar al Portapapeles", command=self.copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # Barra de estado
        status_frame = ttk.Frame(bottom_frame, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W, padding=2)
        status_label.pack(fill=tk.X)
    
    def select_directory(self):
        """Permite al usuario seleccionar un directorio y actualiza la vista de árbol"""
        self.status_var.set("Seleccionando directorio...")
        self.root.update_idletasks()  # Actualizar la interfaz
        
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
            self.status_var.set("Cargando directorio...")
            self.root.update_idletasks()  # Actualizar la interfaz
            
            self.populate_treeview(directory)
            self.status_var.set(f"Directorio cargado: {os.path.basename(directory)}")
        else:
            self.status_var.set("Listo")
    
    def populate_treeview(self, path):
        """Llena el Treeview con la estructura de directorios y archivos, usando should_skip para filtrar"""
        # Limpiar el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Función para añadir nodos recursivamente
        def add_node(parent, path, dirname):
            # Verificar si debemos omitir este directorio
            if os.path.isdir(path) and should_skip(path):
                return
                
            # Insertar el nodo (directorio o archivo raíz)
            node_id = path
            node = self.tree.insert(parent, 'end', iid=node_id, text=f"☐ {dirname}", 
                                   tags=('unchecked', 'folder'), open=False, 
                                   image=self.folder_icon if hasattr(self, 'folder_icon') else '')
            
            try:
                # Listar contenidos del directorio
                for item in sorted(os.listdir(path)):
                    item_path = os.path.join(path, item)
                    
                    # Verificar si debemos omitir este item
                    if should_skip(item_path):
                        continue
                    
                    # Si es un directorio, llamar recursivamente
                    if os.path.isdir(item_path):
                        add_node(node, item_path, item)
                    else:
                        # Si es un archivo, añadirlo como hoja
                        self.tree.insert(node, 'end', iid=item_path, text=f"☐ {item}", 
                                        tags=('unchecked', 'file'), image=self.file_icon if hasattr(self, 'file_icon') else '')
            except PermissionError:
                # Manejar errores de permisos
                error_id = f"{node_id}_error_perm"
                self.tree.insert(node, 'end', iid=error_id, text="Sin acceso (Permisos denegados)")
            except Exception as e:
                # Manejar otros errores
                error_id = f"{node_id}_error_general"
                self.tree.insert(node, 'end', iid=error_id, text=f"Error: {str(e)}")
        
        # Añadir el directorio raíz
        root_dir = os.path.basename(path)
        if not root_dir:  # Si es la raíz, usar la ruta completa
            root_dir = path
        add_node('', path, root_dir)
    
    def toggle_check(self, event):
        """Cambia el estado de check/uncheck del item clickeado y sus hijos"""
        # Identificar la región y fila clickeada
        region = self.tree.identify_region(event.x, event.y)
        item_id = self.tree.identify_row(event.y)
        
        # Solo procesar clics en la región de texto o icono
        if region in ('tree', 'cell', 'text', 'image') and item_id:
            tags = list(self.tree.item(item_id, 'tags'))
            current_text = self.tree.item(item_id, 'text')
            item_name = current_text[2:]  # Quitar el símbolo de checkbox
            
            if 'unchecked' in tags:
                # Cambiar a checked
                tags.remove('unchecked')
                tags.append('checked')
                new_text = f"☑ {item_name}"
            else:
                # Cambiar a unchecked
                if 'checked' in tags:
                    tags.remove('checked')
                tags.append('unchecked')
                new_text = f"☐ {item_name}"
            
            # Actualizar el item
            self.tree.item(item_id, text=new_text, tags=tags)
            
            # Si es una carpeta, aplicar el mismo cambio a todos los hijos recursivamente
            if 'folder' in tags:
                self.toggle_children(item_id, 'checked' in tags)
    
    def toggle_children(self, parent_id, checked):
        """Aplica el mismo estado de check/uncheck a todos los hijos recursivamente"""
        for child_id in self.tree.get_children(parent_id):
            child_tags = list(self.tree.item(child_id, 'tags'))
            current_text = self.tree.item(child_id, 'text')
            item_name = current_text[2:]  # Quitar el símbolo de checkbox
            
            # Actualizar tags
            if 'checked' in child_tags and not checked:
                child_tags.remove('checked')
                child_tags.append('unchecked')
            elif 'unchecked' in child_tags and checked:
                child_tags.remove('unchecked')
                child_tags.append('checked')
            
            # Actualizar texto con el símbolo apropiado
            new_text = f"☑ {item_name}" if checked else f"☐ {item_name}"
            self.tree.item(child_id, text=new_text, tags=child_tags)
            
            # Recursivamente aplicar a los hijos
            if self.tree.get_children(child_id):
                self.toggle_children(child_id, checked)
    
    def get_checked_files(self, parent=''):
        """Recorre el árbol y devuelve una lista de archivos marcados"""
        checked_files = []
        
        def collect_checked(parent):
            for item_id in self.tree.get_children(parent):
                tags = self.tree.item(item_id, 'tags')
                
                if 'checked' in tags:
                    # Si es un archivo y está marcado, añadirlo a la lista
                    if 'file' in tags and os.path.isfile(item_id):
                        checked_files.append(item_id)
                
                # Recursivamente revisar hijos
                if self.tree.get_children(item_id):
                    collect_checked(item_id)
        
        collect_checked(parent)
        return checked_files
    
    def generate_dump(self):
        """Genera un dump con el contenido de los archivos seleccionados"""
        # Obtener archivos seleccionados
        self.status_var.set("Buscando archivos seleccionados...")
        self.root.update_idletasks()
        
        selected_files = self.get_checked_files()
        
        if not selected_files:
            self.show_text_message("No hay archivos seleccionados. Marca algunos archivos usando los checkboxes.")
            self.status_var.set("No hay archivos seleccionados")
            return
        
        # Generar el dump
        self.status_var.set(f"Generando dump de {len(selected_files)} archivos...")
        self.root.update_idletasks()
        
        output = []
        total_size = 0
        error_count = 0
        
        for index, file_path in enumerate(selected_files):
            # Actualizar el estado periódicamente
            if index % 5 == 0:
                self.status_var.set(f"Procesando archivo {index+1} de {len(selected_files)}...")
                self.root.update_idletasks()
            
            try:
                file_info = get_file_info(file_path)
                total_size += file_info['size']
                
                output.append(f"\n\n{'=' * 80}")
                output.append(f"File: {file_path}")
                output.append(f"Size: {file_info['size']} bytes")
                output.append(f"Last Modified: {file_info['last_modified']}")
                output.append('=' * 80 + '\n')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        output.append(content)
                except UnicodeDecodeError:
                    # Probar con otra codificación o saltar
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                            output.append(content)
                    except Exception as e:
                        output.append(f"Error al leer el archivo (problema de codificación): {str(e)}")
                        error_count += 1
                except PermissionError:
                    output.append("Error al leer el archivo: Permiso denegado")
                    error_count += 1
                except Exception as e:
                    output.append(f"Error al leer el archivo: {str(e)}")
                    error_count += 1
            except Exception as e:
                output.append(f"\n\n{'=' * 80}")
                output.append(f"Error al procesar el archivo {file_path}: {str(e)}")
                output.append('=' * 80 + '\n')
                error_count += 1
        
        # Guardar el contenido para la función de copiar
        self.dump_content = '\n'.join(output)
        
        # Mostrar el resultado en el área de texto
        self.show_text_message(self.dump_content)
        
        # Informar al usuario
        if error_count > 0:
            status_text = f"Dump generado con {error_count} errores: {len(selected_files)} archivos, {self.format_size(total_size)}"
        else:
            status_text = f"Dump generado correctamente: {len(selected_files)} archivos, {self.format_size(total_size)}"
        
        self.status_var.set(status_text)
    
    def show_text_message(self, message):
        """Muestra un mensaje en el área de texto"""
        # Habilitar el widget para escritura
        self.result_text.config(state='normal')
        
        # Limpiar contenido anterior
        self.result_text.delete(1.0, tk.END)
        
        # Insertar el nuevo texto
        self.result_text.insert(tk.END, message)
        
        # Volver a deshabilitar
        self.result_text.config(state='disabled')
    
    def format_size(self, size_bytes):
        """Formatea un tamaño en bytes a una representación legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024 or unit == 'GB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
    
    def copy_to_clipboard(self):
        """Copia el contenido generado al portapapeles"""
        if self.dump_content:
            self.status_var.set("Copiando al portapapeles...")
            self.root.update_idletasks()
            
            try:
                pyperclip.copy(self.dump_content)
                self.status_var.set("Contenido copiado al portapapeles")
            except Exception as e:
                self.status_var.set(f"Error al copiar: {str(e)}")
            
            # Tiempo de espera para mostrar confirmación (2 segundos)
            self.root.after(2000, lambda: self.status_var.set("Listo"))
        else:
            self.status_var.set("No hay contenido para copiar. Genera un dump primero.")
            self.root.after(2000, lambda: self.status_var.set("Listo"))
    
    def refresh_directory(self):
        """Refresca el directorio actual sin necesidad de volver a seleccionarlo"""
        directory = self.selected_directory.get()
        if directory and os.path.exists(directory):
            self.status_var.set("Refrescando directorio...")
            self.root.update_idletasks()  # Actualizar la interfaz
            
            # Repoblar el Treeview manteniendo las selecciones actuales
            self.refresh_treeview(directory)
            self.status_var.set(f"Directorio refrescado: {os.path.basename(directory)}")
        else:
            self.status_var.set("No hay directorio seleccionado para refrescar")
    
    def refresh_treeview(self, path):
        """Actualiza el Treeview preservando las selecciones actuales"""
        # Guardar las selecciones actuales
        checked_items = []
        
        def collect_checked_items(parent=''):
            for item_id in self.tree.get_children(parent):
                tags = self.tree.item(item_id, 'tags')
                if 'checked' in tags:
                    checked_items.append(item_id)
                
                if self.tree.get_children(item_id):
                    collect_checked_items(item_id)
        
        collect_checked_items()
        
        # Repoblar el Treeview
        self.populate_treeview(path)
        
        # Restaurar las selecciones que aún existen
        for item_id in checked_items:
            if os.path.exists(item_id) and self.tree.exists(item_id):
                # Obtener las etiquetas actuales y el texto
                tags = list(self.tree.item(item_id, 'tags'))
                current_text = self.tree.item(item_id, 'text')
                item_name = current_text[2:]  # Quitar el símbolo de checkbox
                
                # Actualizar a checked
                if 'unchecked' in tags:
                    tags.remove('unchecked')
                if 'checked' not in tags:
                    tags.append('checked')
                
                # Actualizar el item
                self.tree.item(item_id, text=f"☑ {item_name}", tags=tags)

def main():
    root = tk.Tk()
    app = CodeDumpGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 