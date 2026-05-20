#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
from datetime import datetime

class RenamerEngine:
    """
    Modelo / Backend: Maneja la lógica pura de renombrado y el estado de archivos.
    Sin dependencias de PyQt6.
    """
    def __init__(self):
        self.directory = ""
        self.files_state = [] # Lista de dicts: {'original': str, 'base': str, 'ext': str, 'preview': str}
        self.video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v')
        self.history = [] # Pila de estados previos (Undo)
        self.redo_stack = [] # Pila para Redo
        self.history_log = [] # Registro cronológico: [(datetime, old, new), ...]
        self.batch_state = [] # Mesa de trabajo para procesos por lotes
        self.custom_vocabulary = set() # Nombres confirmados por el usuario para autocompletado

        # --- NUEVO: Gestión Inteligente del Diccionario ---
        self.ruta_config_dir = os.path.expanduser("~/.config/reylag-rename-studio")
        self.ruta_diccionario = os.path.join(self.ruta_config_dir, "diccionario.txt")
        self.diccionario = []
        self.inicializar_diccionario()

    def inicializar_diccionario(self):
        """Crea la carpeta en .config si no existe y asegura el diccionario activo."""
        try:
            if not os.path.exists(self.ruta_config_dir):
                os.makedirs(self.ruta_config_dir, exist_ok=True)
            
            # Si no existe el personalizado, intentamos copiar diccionario_por_defecto.txt si existe al lado de este archivo,
            # de lo contrario creamos uno base inicial genérico
            if not os.path.exists(self.ruta_diccionario):
                default_dic = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diccionario_por_defecto.txt")
                if os.path.exists(default_dic):
                    try:
                        shutil.copy2(default_dic, self.ruta_diccionario)
                        self.cargar_diccionario()
                    except Exception:
                        base_inicial = ["Toma_01", "Entrevista", "B_Roll", "Plano_General", "Recurso"]
                        self.guardar_diccionario_ordenado(base_inicial)
                else:
                    base_inicial = ["Toma_01", "Entrevista", "B_Roll", "Plano_General", "Recurso"]
                    self.guardar_diccionario_ordenado(base_inicial)
            else:
                self.cargar_diccionario()
        except Exception as e:
            print(f"Error de permisos al inicializar diccionario: {e}")

    def natural_sort_key(self, s):
        """Clave de ordenamiento natural: identifica números dentro de cadenas de texto."""
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def cargar_diccionario(self):
        """Carga el diccionario activo ordenándolo de forma natural y sin duplicados."""
        if os.path.exists(self.ruta_diccionario):
            with open(self.ruta_diccionario, 'r', encoding='utf-8') as f:
                lineas = [l.strip() for l in f if l.strip()]
            # Eliminar duplicados y aplicar orden natural (1, 2, 10...)
            self.diccionario = sorted(list(set(lineas)), key=self.natural_sort_key)

    def guardar_diccionario_ordenado(self, lista_palabras):
        """Escribe los cambios físicamente en el diccionario personalizado."""
        self.diccionario = sorted(list(set([p.strip() for p in lista_palabras if p.strip()])), key=self.natural_sort_key)
        with open(self.ruta_diccionario, 'w', encoding='utf-8') as f:
            for palabra in self.diccionario:
                f.write(f"{palabra}\n")

    def agregar_palabra_al_vuelo(self, palabra):
        """Añade una nueva palabra desde la caja de texto conservando tu personalización."""
        if palabra.strip() and palabra not in self.diccionario:
            self.diccionario.append(palabra.strip())
            self.guardar_diccionario_ordenado(self.diccionario)

    # --- NUEVO: Funciones de Fusión del Menú Superior ---
    def importar_y_fusionar(self, ruta_externa):
        """Fusiona un diccionario externo con el tuyo. El tuyo mantiene la prioridad."""
        if os.path.exists(ruta_externa):
            with open(ruta_externa, 'r', encoding='utf-8') as f:
                lineas_externas = [l.strip() for l in f if l.strip()]
            
            # Unión matemática de conjuntos (Evita duplicados)
            fusion = list(set(self.diccionario) | set(lineas_externas))
            self.guardar_diccionario_ordenado(fusion)
            return True
        return False

    def exportar_diccionario(self, ruta_destino):
        """Exporta una copia exacta de tu diccionario activo a cualquier ruta (ej: Pendrive)."""
        try:
            shutil.copy2(self.ruta_diccionario, ruta_destino)
            return True
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

    def nombre_ya_existe_en_disco(self, nuevo_nombre_sin_ext, ext_actual):
        """Comprueba si el archivo que estás escribiendo ya existe físicamente en la carpeta."""
        if not self.directory:
            return False
        nombre_completo = f"{nuevo_nombre_sin_ext}{ext_actual}"
        return os.path.exists(os.path.join(self.directory, nombre_completo))

    def load_directory(self, path):
        if not os.path.isdir(path):
            return False
        self.directory = path
        self.files_state = []
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(self.video_extensions)]
            for f in sorted(files):
                base, ext = os.path.splitext(f)
                self.files_state.append({
                    'original': f,
                    'current': f,
                    'preview': f,
                    'base': base,
                    'ext': ext
                })
            return True
        except Exception:
            return False

    def load_single_file(self, file_path):
        """Añade un único archivo al estado actual."""
        if not os.path.isfile(file_path):
            return False
        
        path, filename = os.path.split(file_path)
        if not self.directory:
            self.directory = path
            
        if filename.lower().endswith(self.video_extensions):
            base, ext = os.path.splitext(filename)
            # Evitar duplicados
            if any(f['original'] == filename for f in self.files_state):
                return False
                
            self.files_state.append({
                'original': filename,
                'current': filename,
                'preview': filename,
                'base': base,
                'ext': ext
            })
            return True
        return False

    def get_suggestions_vocabulary(self):
        """
        Genera una lista de palabras sugeridas basada en los archivos actuales
        y el vocabulario del diccionario activo, ordenada de forma natural.
        """
        vocab = set(self.diccionario)

        for file_info in self.files_state:
            base_name = file_info.get('base', '')
            if base_name:
                vocab.add(base_name)

        return sorted(list(vocab), key=self.natural_sort_key)

    def add_to_vocabulary(self, new_name):
        """Añade un nombre confirmado por el usuario al vocabulario de autocompletado."""
        if new_name:
            self.agregar_palabra_al_vuelo(new_name)

    def update_individual_name(self, index, new_name):
        if 0 <= index < len(self.files_state):
            # Al actualizar individualmente, cambiamos el 'current' (nombre virtual actual)
            self.files_state[index]['current'] = new_name
            name, ext = os.path.splitext(new_name)
            self.files_state[index]['base'] = name
            self.files_state[index]['ext'] = ext
            return True
        return False

    def generate_previews(self, mode, params):
        """Calcula los nuevos nombres sin aplicarlos en el estado BATCH."""
        for file_info in self.batch_state:
            name = file_info['base']
            ext = file_info['ext']
            
            new_name = name

            if mode == 0: # Formato Dolphin ###
                template = params.get('template', 'Video_###')
                try:
                    start_num = int(params.get('start_num', 1))
                except ValueError:
                    start_num = 1
                
                wildcards = re.findall(r'#+', template)
                if wildcards:
                    pattern = sorted(wildcards, key=len, reverse=True)[0]
                    padding = len(pattern)
                    number_str = str(start_num + self.batch_state.index(file_info)).zfill(padding)
                    new_base = template.replace(pattern, number_str)
                else:
                    new_base = f"{template}_{start_num + self.batch_state.index(file_info)}"
                file_info['preview'] = new_base + ext

            elif mode == 1: # Reemplazo
                search = params.get('search', '')
                replace = params.get('replace', '')
                if search:
                    new_base = name.replace(search, replace)
                    file_info['preview'] = new_base + ext

            elif mode == 2: # Añadir
                text = params.get('text', '')
                position = params.get('position', 'Prefijo')
                if position == 'Prefijo':
                    new_base = text + name
                else:
                    new_base = name + text
                file_info['preview'] = new_base + ext

            elif mode == 3: # Caso / Limpieza
                case_mode = params.get('case_mode', 'Sin cambios')
                clean_special = params.get('clean_special', False)
                clean_spaces = params.get('clean_spaces', False)

                # 1. Transformación de Caso
                if case_mode == 'Minúsculas':
                    new_base = name.lower()
                elif case_mode == 'MAYÚSCULAS':
                    new_base = name.upper()
                elif case_mode == 'Title Case':
                    new_base = name.title()
                else:
                    new_base = name

                # 2. Limpieza de caracteres especiales (mantiene letras, números y guiones)
                if clean_special:
                    new_base = re.sub(r'[^a-zA-Z0-9\s\-_]', '', new_base)

                # 3. Limpieza de espacios extra
                if clean_spaces:
                    new_base = " ".join(new_base.split())

                file_info['preview'] = new_base + ext

    def execute_renaming(self):
        """Ejecuta el renombrado masivo sobre el estado BATCH."""
        success = 0
        errors = []
        current_history = []
        
        for file_info in self.batch_state:
            old_name = file_info['current']
            new_name = file_info['preview']
            
            if old_name == new_name:
                continue
                
            old_path = os.path.join(self.directory, old_name)
            new_path = os.path.join(self.directory, new_name)
            
            if os.path.exists(new_path):
                errors.append(f"Error: El destino ya existe para {new_name}")
                continue
                
            try:
                os.rename(old_path, new_path)
                current_history.append((new_name, old_name)) # Para el Undo: (nuevo, viejo)
                
                # Registrar en el historial cronológico
                self.history_log.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'old': old_name,
                    'new': new_name
                })
                
                # Actualizar estado interno (en batch y en files_state si existe)
                file_info['current'] = new_name
                file_info['original'] = new_name
                
                for f in self.files_state:
                    if f['original'] == old_name:
                        f['original'] = new_name
                        f['current'] = new_name
                        f['preview'] = new_name
                
                success += 1
            except Exception as e:
                errors.append(f"Fallo al renombrar {old_name}: {str(e)}")
        
        if current_history:
            self.history.append(current_history)
            self.redo_stack.clear()
            
        return success, errors

    def rename_single_file(self, row, new_name):
        """Renombra un archivo individual de forma instantánea en el disco."""
        if row < 0 or row >= len(self.files_state):
            return False, "Índice fuera de rango."
            
        file_info = self.files_state[row]
        old_name = file_info['current']
        
        if old_name == new_name:
            return True, "Sin cambios."
            
        old_path = os.path.join(self.directory, old_name)
        new_path = os.path.join(self.directory, new_name)
        
        if os.path.exists(new_path):
            return False, f"El archivo {new_name} ya existe."
            
        try:
            os.rename(old_path, new_path)
            
            # Actualizar historial
            self.history_log.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'old': old_name,
                'new': new_name
            })
            
            # Actualizar estado interno
            file_info['original'] = new_name
            file_info['current'] = new_name
            file_info['preview'] = new_name
            name, ext = os.path.splitext(new_name)
            file_info['base'] = name
            
            return True, "Éxito"
        except Exception as e:
            return False, str(e)

    def undo_last_operation(self):
        """Revierte la última operación de renombrado masivo."""
        if not self.history:
            return 0, ["No hay operaciones para deshacer."]
            
        last_op = self.history.pop()
        success = 0
        errors = []
        
        for current_name, old_name in last_op:
            current_path = os.path.join(self.directory, current_name)
            old_path = os.path.join(self.directory, old_name)
            
            try:
                os.rename(current_path, old_path)
                # Actualizar el estado interno
                for f in self.files_state:
                    if f['original'] == current_name:
                        f['original'] = old_name
                        f['current'] = old_name
                        f['preview'] = old_name
                        name, ext = os.path.splitext(old_name)
                        f['base'] = name
                success += 1
            except Exception as e:
                errors.append(f"Error al deshacer {current_name}: {str(e)}")
        
        if success > 0:
            # Guardamos la operación en redo (viejo -> nuevo)
            self.redo_stack.append([(old, cur) for cur, old in last_op])
                
        return success, errors

    def redo_last_operation(self):
        """Vuelve a aplicar la última operación deshecha."""
        if not self.redo_stack:
            return 0, ["No hay operaciones para rehacer."]
            
        last_redo = self.redo_stack.pop()
        success = 0
        errors = []
        
        for old_name, current_name in last_redo:
            old_path = os.path.join(self.directory, old_name)
            current_path = os.path.join(self.directory, current_name)
            
            try:
                os.rename(old_path, current_path)
                # Actualizar el estado interno
                for f in self.files_state:
                    if f['original'] == old_name:
                        f['original'] = current_name
                        f['current'] = current_name
                        f['preview'] = current_name
                        name, ext = os.path.splitext(current_name)
                        f['base'] = name
                success += 1
            except Exception as e:
                errors.append(f"Error al rehacer {old_name}: {str(e)}")
        
        if success > 0:
            # Volvemos a ponerlo en el historial de deshacer (nuevo -> viejo)
            self.history.append([(cur, old) for old, cur in last_redo])
            
        return success, errors
