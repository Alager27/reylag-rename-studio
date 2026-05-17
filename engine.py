#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime

class RenamerEngine:
    """
    Modelo / Backend: Maneja la lógica pura de renombrado y el estado de archivos.
    Sin dependencias de PyQt6.
    """
    def __init__(self):
        self.directory = ""
        self.files_state = [] # Lista de dicts: {'original': str, 'base': str, 'ext': str, 'preview': str}
        self.video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
        self.history = [] # Pila de estados previos (Undo)
        self.redo_stack = [] # Pila para Redo
        self.history_log = [] # Registro cronológico: [(datetime, old, new), ...]
        self.batch_state = [] # Mesa de trabajo para procesos por lotes
        self.custom_vocabulary = set() # Nombres confirmados por el usuario para autocompletado

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
        y el vocabulario personalizado, ordenada alfabéticamente de forma natural.
        """
        vocab = set(self.custom_vocabulary)

        for file_info in self.files_state:
            base_name = file_info.get('base', '')
            if base_name:
                vocab.add(base_name)

        return sorted(list(vocab), key=str.casefold)

    def add_to_vocabulary(self, new_name):
        """Añade un nombre confirmado por el usuario al vocabulario de autocompletado."""
        if new_name:
            self.custom_vocabulary.add(new_name)

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
