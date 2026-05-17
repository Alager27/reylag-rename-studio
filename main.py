import os
import sys
import logging
import re

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, compatible con PyInstaller y código fuente."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- CONFIGURACIÓN DE ENTORNO REYLAG STUDIO ---
os.environ["QT_QPA_PLATFORMTHEME"] = "kde"  # Fuerza a Qt6 a integrarse con el panel de control y tema de KDE
# Silenciar la búsqueda de drivers de Nvidia (VDPAU)
os.environ["VDPAU_DRIVER"] = "none"

# Usamos un modo más seguro para evitar el Segfault en Intel antiguas (Ivy Bridge)
os.environ["MESA_LOADER_DRIVER_OVERRIDE"] = "crocus"
os.environ["LIBVA_DRIVER_NAME"] = "i965"
os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"

# Desactivamos el renderizado por hilos para evitar el choque del QPaintDevice
os.environ["QSG_RENDER_LOOP"] = "basic" 
os.environ["QT_VIDEO_BACKEND"] = "ffmpeg"
os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "ffmpeg"

# IMPORTANTE: No forzamos software, permitimos que Qt use OpenGL 
# para que Crocus haga el trabajo pesado de renderizado.
os.environ["QT_RHI_BACKEND"] = "opengl"
os.environ["QSG_RHI_BACKEND"] = "opengl"
os.environ["QT_XCB_GL_INTEGRATION"] = "xcb_egl"

# Silenciar basura de logs para mantener la terminal limpia
os.environ["QT_LOGGING_RULES"] = "qt.multimedia.ffmpeg.debug=false;*.debug=false;qt.qpa.wayland=false;qt.text.font.db=false;qt.svg.warning=false"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QProgressDialog, QMenu, QDialog, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit, QPushButton
)
from PyQt6.QtCore import Qt, QUrl, QTime, QThread, pyqtSignal, QSettings, QTimer, QSizeF
from PyQt6.QtGui import QIcon, QFont, QDesktopServices, QShortcut, QKeySequence, QSurfaceFormat, QFontDatabase

# Configuración de Logging
logging.basicConfig(
    filename='videorenamer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Importar Componentes MVC
from engine import RenamerEngine
from ui import VideoRenamerUI

from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QTimer

# --- SPLASH SCREEN BLINDADO ---
class ReyLagSplash(QSplashScreen):
    def __init__(self):
        # Usamos un tamaño fijo para evitar cálculos de layout en el arranque
        pix = QPixmap(500, 300)
        pix.fill(QColor("#1a1a1b"))
        
        # Pintamos el logo de forma estática una sola vez
        painter = QPainter(pix)
        painter.setPen(QColor("#3DAEE9"))
        painter.drawRect(0, 0, 499, 299)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("sans-serif", 22, QFont.Weight.Bold))
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "ReyLag Rename Studio®")
        
        # Subtítulo de carga
        painter.setFont(QFont("sans-serif", 10))
        painter.drawText(0, 260, 500, 30, Qt.AlignmentFlag.AlignCenter, "Cargando motor multimedia...")
        painter.end()
        
        super().__init__(pix)

class RenameWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, list)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def run(self):
        success, errors = self.engine.execute_renaming()
        self.finished.emit(success, errors)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Inicializar el motor (Modelo)
        self.engine = RenamerEngine()

        # 2. Inicializar la interfaz (Vista) - ¡SUPER IMPORTANTE QUE VAYA AQUÍ!
        self.view = VideoRenamerUI(self)

        # 3. Conectar las señales (Controlador)
        self.connect_signals()

        # 4. Resto de configuraciones (Historial, portapapeles, etc.)
        self.view.list_files.installEventFilter(self)
        
        self.rename_history = set()
        self.dict_path = os.path.expanduser("~/.config/reylag_diccionario.txt")
        os.makedirs(os.path.dirname(self.dict_path), exist_ok=True)
        self.load_dictionary_from_disk()

        self.setWindowTitle("ReyLag Rename Studio")
        self.resize(1350, 900)

        # Cargar el icono de forma segura para PyInstaller
        icon_path = resource_path("reylag_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setAcceptDrops(True)

        # 3. Persistencia (QSettings)
        self.settings = QSettings("KDE", "VideoRenamer")
        # SE DESPLAZA: La restauración se hace ahora tras el Splash en el __main__
        # self.restore_settings()

        logging.info("Aplicación iniciada correctamente.")

    def connect_signals(self):
        # Menú Barra
        self.view.action_open_dir.triggered.connect(self.on_open_directory)
        self.view.action_open_file.triggered.connect(self.on_open_file)
        self.view.action_history.triggered.connect(self.on_show_history)
        self.view.action_exit.triggered.connect(self.close)

        self.view.action_undo.triggered.connect(self.on_undo)
        self.view.action_redo.triggered.connect(self.on_redo)
        self.view.action_clear.triggered.connect(self.on_clear_list)

        self.view.action_lang_es.triggered.connect(lambda _: self.on_change_language("es"))
        self.view.action_lang_en.triggered.connect(lambda _: self.on_change_language("en"))
        self.view.action_lang_gl.triggered.connect(lambda _: self.on_change_language("gl"))

        # Explorador
        self.view.btn_open.clicked.connect(self.on_open_directory)
        self.view.btn_refresh.clicked.connect(self.on_refresh_directory) # NUEVO CONECTOR
        self.view.edit_filter.textChanged.connect(self.filter_list)
        # self.view.list_files.itemDoubleClicked.connect(self.on_item_double_clicked)
        # NUEVO: Restauramos la conexión de selección simple
        self.view.list_files.itemSelectionChanged.connect(self.on_simple_selection)
        # Arrancar reproducción continua solo al hacer doble clic
        self.view.list_files.itemDoubleClicked.connect(lambda item: self.view.media_player.play())

        # Edición Individual
        self.view.btn_apply_name.clicked.connect(self.on_apply_individual)
        self.view.edit_name.returnPressed.connect(self.on_apply_individual)
        self.view.btn_dict.clicked.connect(self.open_dictionary_manager)

        # Motor de Renombrado (Instant Preview)
        self.view.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
        self.view.edit_template.textChanged.connect(self.update_preview)
        self.view.edit_start_at.textChanged.connect(self.update_preview)
        self.view.edit_search.textChanged.connect(self.update_preview)
        self.view.edit_add_text.textChanged.connect(self.update_preview)
        self.view.combo_pos.currentIndexChanged.connect(self.update_preview)

        # Caso / Limpieza
        self.view.combo_case.currentIndexChanged.connect(self.update_preview)
        self.view.check_clean_special.toggled.connect(self.update_preview)
        self.view.check_clean_spaces.toggled.connect(self.update_preview)

        # Filtro de lista
        self.view.btn_play.clicked.connect(self.toggle_playback)
        self.view.btn_prev.clicked.connect(self.on_prev_file)
        self.view.btn_next.clicked.connect(self.on_next_file)
        self.view.slider_progress.sliderMoved.connect(self.view.media_player.setPosition)
        self.view.media_player.positionChanged.connect(self.on_media_position_changed)
        self.view.media_player.durationChanged.connect(self.on_media_duration_changed)
        self.view.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        self.view.media_player.errorOccurred.connect(self.handle_media_error)

        # Zoom y Fullscreen
        self.view.slider_zoom.valueChanged.connect(self.apply_zoom)
        self.view.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.view.video_item.nativeSizeChanged.connect(self.on_video_size_changed)
        # La señal fullScreenChanged no existe en QGraphicsView por defecto, 
        # así que la lógica de iconos del botón la manejaremos directamente en toggle_fullscreen.

        # Audio
        self.view.btn_mute.clicked.connect(self.toggle_mute)
        self.view.slider_volume.valueChanged.connect(self.change_volume)
        self.btn_screenshot = self.view.btn_screenshot
        self.btn_screenshot.clicked.connect(self.take_screenshot)
        self.view.audio_output.setVolume(0.7)

        # Ejecución
        self.view.btn_execute.clicked.connect(self.on_execute_renaming)
        self.view.btn_reset.clicked.connect(self.on_reset_rules)
        self.view.btn_clear_batch.clicked.connect(self.on_clear_batch)

        # Drag & Drop especial
        self.view.table_batch.dragEnterEvent = self.table_drag_enter
        self.view.table_batch.dropEvent = self.table_drop
        self.view.table_batch.customContextMenuRequested.connect(self.show_batch_context_menu)
        self.view.table_batch.model().rowsMoved.connect(self.on_batch_reordered)

        # Menú Contextual
        self.view.list_files.customContextMenuRequested.connect(self.show_context_menu)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self, self.take_screenshot)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.on_undo)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.apply_quick_tag(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.apply_quick_tag(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.apply_quick_tag(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.apply_quick_tag(3))
        QShortcut(QKeySequence("Space"), self, self.toggle_playback)

    def apply_quick_tag(self, index):
        if index < len(self.view.suggestions):
            tag = self.view.suggestions[index]
            self.view.edit_name.setText(tag)
            self.view.edit_name.setFocus()
            self.view.edit_name.setCursorPosition(len(tag))

    def restore_settings(self):
        last_dir = self.settings.value("last_directory", "")
        if last_dir and os.path.exists(last_dir):
            reply = QMessageBox.question(
                self, "Restaurar sesión", f"¿Deseas volver a abrir esta carpeta?\n\n{last_dir}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.load_path(last_dir)
            else:
                self.settings.remove("last_directory")
        
        lang = self.settings.value("language", "es")
        self.on_change_language(lang)
        self.view.combo_mode.setCurrentIndex(int(self.settings.value("renamer_mode", 0)))
        
        # INYECCIÓN DE ETIQUETAS: Textos rápidos para los atajos Ctrl+1, Ctrl+2, Ctrl+3, Ctrl+4
        self.view.suggestions = self.settings.value("suggestions", ["Juicio", "Declaración", "Prueba", "Sentencia"])

    def save_settings(self):
        if self.engine.directory:
            self.settings.setValue("last_directory", self.engine.directory)
        self.settings.setValue("renamer_mode", self.view.combo_mode.currentIndex())
        
        # Seguro contra fallos: solo guardar si el atributo existe
        if hasattr(self.view, 'suggestions'):
            self.settings.setValue("suggestions", self.view.suggestions)

    def load_dictionary_from_disk(self):
        """Despierta el diccionario leyendo el historial guardado en disco.
           Si es el primer inicio, copia un diccionario base de fábrica."""

        # 1. SI ES LA PRIMERA VEZ: Intentamos instalar el "Starter Kit"
        if not os.path.exists(self.dict_path):
            import shutil
            default_dic = resource_path("diccionario_por_defecto.txt")
            if os.path.exists(default_dic):
                try:
                    shutil.copy(default_dic, self.dict_path)
                    print("Primer inicio detectado: Diccionario de fábrica instalado.")
                except Exception as e:
                    print(f"Error al instalar el diccionario base: {e}")
            else:
                print("Primer inicio: No se encontró diccionario base, iniciando vacío.")

        # 2. CARGAMOS EL DICCIONARIO (ya sea el antiguo o el recién copiado)
        if os.path.exists(self.dict_path):
            try:
                with open(self.dict_path, 'r', encoding='utf-8') as f:
                    words = [
                        line.strip() for line in f
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    self.rename_history.update(words)
                    self.engine.custom_vocabulary.update(words)
                print(f"Diccionario cargado con {len(words)} palabras.")
            except Exception as e:
                print(f"Error al cargar el diccionario: {e}")

        # 3. Refrescamos la UI para que el autocompletado ya sepa las palabras
        self.update_completer_suggestions()

    def save_dictionary_to_disk(self):
        """Guarda el vocabulario actual en el disco sin duplicados y ordenado."""
        # 1. Obtenemos el vocabulario limpio y sin duplicados del motor
        clean_vocab = self.engine.get_suggestions_vocabulary()

        # 2. Sobrescribimos el archivo completo (usamos 'w' en lugar de 'a')
        try:
            with open(self.dict_path, 'w', encoding='utf-8') as f:
                for word in clean_vocab:
                    if word.strip():  # Evitamos guardar líneas en blanco
                        f.write(word.strip() + '\n')
            print("Diccionario guardado y optimizado con éxito.")
        except Exception as e:
            print(f"Error al guardar el diccionario: {e}")

    def open_dictionary_manager(self):
        """Abre la ventana flotante con el editor libre y el buscador en tiempo real."""
        from ui import DictionaryDialog

        dialog = DictionaryDialog(self.dict_path, self)

        if dialog.exec():  # Si el usuario pulsó "Guardar y Actualizar"
            # 1. Recargar el diccionario en memoria desde el archivo modificado
            self.load_dictionary_from_disk()
            # 2. Refrescar la UI
            self.refresh_ui_list()
            self.view.status_bar.showMessage("✅ Diccionario actualizado y cargado con éxito.", 4000)

    def closeEvent(self, event):
        self.save_settings()
        self.save_dictionary_to_disk()  # Limpieza final: sin duplicados, ordenado
        super().closeEvent(event)

    def on_open_directory(self):
        home_dir = os.path.expanduser("~")
        
        # 1. Creamos el diálogo de forma segura pasándole el directorio real
        dialog = QFileDialog(self, "Seleccionar Carpeta", home_dir)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        
        # 2. Obtenemos los accesos directos que ya tiene por defecto
        urls = dialog.sidebarUrls()
        
        # 3. Añadimos la carpeta de Descargas
        descargas = os.path.join(home_dir, "Descargas")
        if not os.path.exists(descargas): # Por si tu sistema está en inglés
            descargas = os.path.join(home_dir, "Downloads")
        urls.append(QUrl.fromLocalFile(descargas))
        
        # 4. Añadimos la ruta a los Discos Externos
        media_path = f"/run/media/{os.getlogin()}"
        if os.path.exists(media_path):
            urls.append(QUrl.fromLocalFile(media_path))
            
        # 5. Aplicamos los nuevos accesos directos
        dialog.setSidebarUrls(urls)

        # 6. Lanzamos el diálogo
        if dialog.exec():
            path = dialog.selectedFiles()[0]
            self.load_path(path)

    def on_refresh_directory(self):
        import os
        # Buscamos la carpeta actual en la memoria del motor
        carpeta = getattr(self.engine, 'current_dir', 
                  getattr(self.engine, 'directory', 
                  getattr(self.engine, 'current_directory', '')))
        
        if carpeta and os.path.exists(carpeta):
            # Guardamos la fila que estaba seleccionada para no perder la posición
            fila_actual = self.view.list_files.currentRow()
            
            # Recargamos la carpeta entera
            self.load_path(carpeta)
            
            # Intentamos devolver el cursor a donde estaba
            if fila_actual >= 0 and fila_actual < self.view.list_files.count():
                self.view.list_files.setCurrentRow(fila_actual)
                
            self.view.status_bar.showMessage("Lista sincronizada con el disco.", 3000)
        else:
            self.view.status_bar.showMessage("No hay ninguna carpeta abierta para actualizar.", 3000)

    def on_open_file(self):
        home_dir = os.path.expanduser("~")
        
        dialog = QFileDialog(self, "Abrir Video", home_dir, "Videos (*.mp4 *.mkv *.avi *.mov *.webm)")
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        # Repetimos la magia de la barra lateral para abrir archivos individuales
        urls = dialog.sidebarUrls()
        
        descargas = os.path.join(home_dir, "Descargas")
        if not os.path.exists(descargas):
            descargas = os.path.join(home_dir, "Downloads")
        urls.append(QUrl.fromLocalFile(descargas))
        
        media_path = f"/run/media/{os.getlogin()}"
        if os.path.exists(media_path):
            urls.append(QUrl.fromLocalFile(media_path))
            
        dialog.setSidebarUrls(urls)

        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            if self.engine.load_single_file(file_path):
                self.refresh_ui_list()
                self.update_preview()

    def load_path(self, path):
        # 1. Quitamos el "if". Ejecutamos la carga en el motor obligatoriamente.
        self.engine.load_directory(path)

        # 2. Refrescamos la UI (la lista, la previsualización y el diccionario)
        self.refresh_ui_list()
        self.update_preview()
        self.update_completer_suggestions()

    def update_completer_suggestions(self):
        """
        Sincroniza el QCompleter de la UI con el vocabulario actual:
        nombres base de los archivos cargados + historial de nombres escritos por el usuario.
        """
        # Vocabulario del motor (archivos cargados + nombres añadidos en sesión)
        vocab_engine = self.engine.get_suggestions_vocabulary()

        # Combinamos con el historial persistente guardado en disco
        vocab_combined = sorted(set(vocab_engine) | self.rename_history, key=str.casefold)

        self.view.completer_model.setStringList(vocab_combined)

    def refresh_ui_list(self):
        # Usamos .get() por seguridad. Si el motor usa 'original' en vez de 'current', la app no se colgará.
        def natural_sort_key(file_info):
            nombre = file_info.get('current', file_info.get('original', ''))
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', nombre)]

        self.engine.files_state.sort(key=natural_sort_key)

        self.view.list_files.blockSignals(True)
        self.view.list_files.clear()

        for f in self.engine.files_state:
            nombre = f.get('current', f.get('original', 'Desconocido'))
            self.view.list_files.addItem(nombre)

        # CRÍTICO: Desbloqueamos las señales ANTES de seleccionar el primer archivo
        self.view.list_files.blockSignals(False)

        if self.engine.files_state:
            self.view.list_files.setCurrentRow(0)  # ¡Ahora sí disparará la carga del vídeo!


    def on_simple_selection(self):
        items = self.view.list_files.selectedItems()
        if items:
            item = items[0]
            # 1. Ponemos el nombre en la caja de edición (vital para tu flujo)
            self.view.edit_name.setText(item.text())
            
            # 2. CARGA AUTOMÁTICA: Cargamos el vídeo al instante
            import os
            file_name = item.text()
            carpeta = getattr(self.engine, 'current_dir', 
                      getattr(self.engine, 'directory', 
                      getattr(self.engine, 'current_directory', '')))
            
            if carpeta:
                ruta_completa = os.path.join(carpeta, file_name)
                self.load_video(ruta_completa)
                # Opcional: self.view.media_player.play() si quieres que arranque solo

    def load_video(self, ruta_completa):
        import os
        from PyQt6.QtCore import QUrl
        import logging

        if not os.path.exists(ruta_completa):
            return

        # 1. PURGA: Detener y limpiar recursos de la GPU previos obligatoriamente
        self.view.media_player.stop()
        self.view.media_player.setSource(QUrl())

        # 2. INTENTO DE CARGA BLINDADO
        try:
            # Filtramos que realmente sea un formato de vídeo conocido
            extensiones_validas = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm')
            if ruta_completa.lower().endswith(extensiones_validas):

                url = QUrl.fromLocalFile(os.path.abspath(ruta_completa))
                self.view.media_player.setSource(url)

                # Retardo táctico de 100ms para asegurar el buffer, pero forzamos PAUSA
                # Esto carga el primer fotograma (miniatura) sin saturar la decodificación de la GPU
                QTimer.singleShot(100, self.view.media_player.pause)
            else:
                self.view.status_bar.showMessage(f"Formato no reproducible: {os.path.basename(ruta_completa)}", 3000)

        except Exception as e:
            self.view.status_bar.showMessage(f"Error de lectura: {os.path.basename(ruta_completa)}", 3000)
            logging.error(f"Excepción grave en load_video: {e}")

    def on_apply_individual(self):
        row = self.view.list_files.currentRow()
        if row < 0 or row >= len(self.engine.files_state):
            return
            
        new_name = self.view.edit_name.text().strip()
        current_name = self.engine.files_state[row]['current']
        
        # 1. Si presionas Enter sin haber cambiado nada, simplemente saltamos al siguiente
        if new_name == current_name:
            self.go_to_next_row(row)
            return
            
        # 2. ESCUDO ANTICOLISIONES: Verificamos si el nombre ya existe en la lista
        # Comparamos en minúsculas por seguridad extra
        nombre_existe = any(f['current'].lower() == new_name.lower() for f in self.engine.files_state)
        
        if nombre_existe:
            QMessageBox.warning(self, "Nombre Duplicado", f"Ya existe un archivo llamado:\n\n'{new_name}'\n\nPor favor, usa un nombre distinto para evitar perder datos.")
            self.view.edit_name.setFocus()
            self.view.edit_name.selectAll()
            return

        # 3. Si pasó las defensas, procedemos a renombrar
        self.view.media_player.stop()
        success, msg = self.engine.rename_single_file(row, new_name)
        if success:
            import os
            nombre_sin_ext = os.path.splitext(new_name)[0].strip()

            if nombre_sin_ext and nombre_sin_ext not in self.rename_history:
                self.rename_history.add(nombre_sin_ext)

            # Persistir en disco de forma limpia (sobrescribe sin duplicados)
            self.save_dictionary_to_disk()

            # Añadir al vocabulario del motor y refrescar el completer
            self.engine.add_to_vocabulary(nombre_sin_ext)
            self.update_completer_suggestions()

            self.refresh_ui_list()
            self.go_to_next_row(row)
            self.update_preview()
        else:
            QMessageBox.critical(self, "Error al Renombrar", msg)

    def filter_list(self, text):
        search_text = text.lower()
        for i in range(self.view.list_files.count()):
            item = self.view.list_files.item(i)
            item.setHidden(search_text not in item.text().lower())

    def eventFilter(self, source, event):
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeySequence
        from PyQt6.QtWidgets import QApplication
        if (event.type() == QEvent.Type.KeyPress and 
            source is self.view.list_files and 
            event.matches(QKeySequence.StandardKey.Copy)):
            item = self.view.list_files.currentItem()
            if item:
                QApplication.clipboard().setText(item.text())
            return True
        return super().eventFilter(source, event)

    def on_prev_file(self):
        current_row = self.view.list_files.currentRow()
        if current_row > 0:
            self.go_to_row(current_row - 1)

    def on_next_file(self):
        current_row = self.view.list_files.currentRow()
        if current_row < self.view.list_files.count() - 1:
            self.go_to_row(current_row + 1)

    def go_to_next_row(self, current_row):
        # Mantenemos este para cuando se pulsa Enter al renombrar
        self.go_to_row(current_row + 1)

    def go_to_row(self, target_row):
        if 0 <= target_row < self.view.list_files.count():
            # 1. Saltamos a la fila objetivo (esto dispara on_simple_selection -> load_video en pausa)
            self.view.list_files.setCurrentRow(target_row)
            self.view.edit_name.setFocus()
            self.view.edit_name.selectAll()

    def update_preview(self):
        params = {
            'template': self.view.edit_template.text(),
            'start_num': self.view.edit_start_at.text(),
            'search': self.view.edit_search.text(),
            'replace': self.view.edit_replace.text(),
            'text': self.view.edit_add_text.text(),
            'position': self.view.combo_pos.currentText(),
            'case_mode': self.view.combo_case.currentText(),
            'clean_special': self.view.check_clean_special.isChecked(),
            'clean_spaces': self.view.check_clean_spaces.isChecked()
        }
        self.engine.generate_previews(self.view.combo_mode.currentIndex(), params)
        self.view.table_batch.setRowCount(len(self.engine.batch_state))
        for i, info in enumerate(self.engine.batch_state):
            self.view.table_batch.setItem(i, 0, QTableWidgetItem(info['current']))
            self.view.table_batch.setItem(i, 1, QTableWidgetItem(info['preview']))

    def on_execute_renaming(self):
        if not self.engine.files_state: return
        if QMessageBox.question(self, "Confirmar", "¿Ejecutar cambios reales en disco?") == QMessageBox.StandardButton.Yes:
            self.worker = RenameWorker(self.engine)
            self.worker.finished.connect(self.on_rename_finished)
            self.worker.start()

    def on_rename_finished(self, success, errors):
        self.refresh_ui_list()
        self.update_preview()

    def on_undo(self):
        success, errors = self.engine.undo_last_operation()
        if success > 0:
            self.refresh_ui_list()
            self.update_preview()
            self.view.status_bar.showMessage(f"Se deshicieron {success} cambios.", 5000)
        if errors:
            QMessageBox.warning(self, "Undo", "\n".join(errors))

    def on_redo(self):
        success, errors = self.engine.redo_last_operation()
        if success > 0:
            self.refresh_ui_list()
            self.update_preview()
            self.view.status_bar.showMessage(f"Se rehicieron {success} cambios.", 5000)
        if errors:
            QMessageBox.warning(self, "Redo", "\n".join(errors))

    def on_change_language(self, lang):
        """Cambia el idioma de la aplicación de forma dinámica, desmarca los otros y guarda."""
        # 1. Pasar la orden a la vista para que cambie los textos
        self.view.retranslate_ui(lang)

        # 2. Sincronizar los "checks" visuales del menú de forma segura
        if hasattr(self.view, 'action_lang_es'):
            self.view.action_lang_es.blockSignals(True)
            self.view.action_lang_en.blockSignals(True)
            self.view.action_lang_gl.blockSignals(True)

            self.view.action_lang_es.setChecked(lang == "es")
            self.view.action_lang_en.setChecked(lang == "en")
            self.view.action_lang_gl.setChecked(lang == "gl")

            self.view.action_lang_es.blockSignals(False)
            self.view.action_lang_en.blockSignals(False)
            self.view.action_lang_gl.blockSignals(False)

        # 3. Guardar la elección en la persistencia del sistema (QSettings)
        if hasattr(self, 'settings'):
            self.settings.setValue("language", lang)

        self.view.status_bar.showMessage(f"Idioma cambiado a: {lang.upper()}", 3000)
    def on_filter_changed(self, t): pass
    def toggle_playback(self):
        from PyQt6.QtMultimedia import QMediaPlayer
        if self.view.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.view.media_player.pause()
        else:
            self.view.media_player.play()

    def on_media_position_changed(self, position):
        self.view.slider_progress.blockSignals(True)
        self.view.slider_progress.setValue(position)
        self.view.slider_progress.blockSignals(False)
        self.update_time_label()

    def on_media_duration_changed(self, duration):
        self.view.slider_progress.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        pos = self.view.media_player.position() // 1000
        dur = self.view.media_player.duration() // 1000
        pos_str = f"{pos//60:02}:{pos%60:02}"
        dur_str = f"{dur//60:02}:{dur%60:02}"
        self.view.lbl_time.setText(f"{pos_str} / {dur_str}")

    def on_playback_state_changed(self, state):
        from PyQt6.QtMultimedia import QMediaPlayer
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.view.btn_play.setIcon(QIcon.fromTheme("media-playback-pause"))
        else:
            self.view.btn_play.setIcon(QIcon.fromTheme("media-playback-start"))

    def handle_media_error(self, error, error_string):
        """Captura errores internos de FFmpeg/GStreamer para evitar cuelgues."""
        from PyQt6.QtMultimedia import QMediaPlayer
        import logging
        import os

        # Ignoramos si es un falso positivo
        if error == QMediaPlayer.Error.NoError:
            return

        nombre_archivo = "el archivo"
        try:
            # Intentamos extraer el nombre del vídeo que causó el problema
            if self.view.media_player.source().isLocalFile():
                nombre_archivo = os.path.basename(self.view.media_player.source().toLocalFile())
        except Exception:
            pass

        # 1. Detenemos la reproducción DE INMEDIATO para liberar a la gráfica
        self.view.media_player.stop()

        # 2. Vaciamos el visor gráfico para que no se quede congelado el último frame
        self.view.media_player.setSource(QUrl())

        # 3. Avisamos al usuario sin molestar (barra inferior)
        mensaje = f"⚠️ Vídeo omitido ({nombre_archivo}): Códec no soportado o dañado."
        self.view.status_bar.showMessage(mensaje, 5000)

        # 4. Registramos el error técnico en el archivo .log silenciosamente
        logging.warning(f"Multimedia Error [{error}]: {error_string} en {nombre_archivo}")

    def on_video_size_changed(self, size):
        if size.isEmpty() or size.width() <= 0 or size.height() <= 0:
            return
        self.view.video_item.setSize(QSizeF(size))
        self.apply_zoom(self.view.slider_zoom.value())

    def apply_zoom(self, value):
        self.view.lbl_zoom.setText(f"Zoom: {value}%")
        self.view.graphics_view.resetTransform()
        
        # Seguro contra Zero-Division
        if not self.view.video_item.nativeSize().isEmpty():
            self.view.graphics_view.fitInView(self.view.video_item, Qt.AspectRatioMode.KeepAspectRatio)
            
        factor = value / 100.0
        self.view.graphics_view.scale(factor, factor)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.view.btn_fullscreen.setIcon(QIcon.fromTheme("view-fullscreen"))
            self.view.splitter.widget(0).setVisible(True)
            self.view.splitter.widget(2).setVisible(True)
        else:
            self.showFullScreen()
            self.view.btn_fullscreen.setIcon(QIcon.fromTheme("view-restore"))
            self.view.splitter.widget(0).setVisible(False)
            self.view.splitter.widget(2).setVisible(False)
        
        QTimer.singleShot(100, lambda: self.apply_zoom(self.view.slider_zoom.value()))

    def toggle_mute(self):
        is_muted = self.view.audio_output.isMuted()
        self.view.audio_output.setMuted(not is_muted)
        if not is_muted:
            self.view.btn_mute.setIcon(QIcon.fromTheme("audio-volume-muted"))
        else:
            self.view.btn_mute.setIcon(QIcon.fromTheme("audio-volume-high"))

    def change_volume(self, value):
        self.view.audio_output.setVolume(value / 100.0)

    def take_screenshot(self):
        import os
        from datetime import datetime
        try:
            # Capturamos la vista gráfica (el visor de video)
            pixmap = self.view.graphics_view.grab()
            
            # Carpeta de capturas
            screenshots_dir = os.path.join(self.engine.directory, "Screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Capture_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            if pixmap.save(filepath, "PNG"):
                self.view.status_bar.showMessage(f"Captura guardada: {filename}", 5000)
            else:
                self.view.status_bar.showMessage("Error al guardar captura.", 5000)
        except Exception as e:
            self.view.status_bar.showMessage(f"Error: {str(e)}", 5000)

    def on_mode_changed(self, i):
        # Ocultar todos los paneles
        self.view.pane_format.hide()
        self.view.pane_replace.hide()
        self.view.pane_add.hide()
        self.view.pane_advanced.hide()
        
        # Mostrar el seleccionado
        if i == 0: self.view.pane_format.show()
        elif i == 1: self.view.pane_replace.show()
        elif i == 2: self.view.pane_add.show()
        elif i == 3: self.view.pane_advanced.show()
        
        self.update_preview()

    def on_reset_rules(self):
        self.view.edit_template.setText("Video_###")
        self.view.edit_start_at.setText("1")
        self.view.edit_search.clear()
        self.view.edit_replace.clear()
        self.view.edit_add_text.clear()
        self.update_preview()

    def on_clear_batch(self):
        self.engine.batch_state = []
        self.update_preview()
        self.view.status_bar.showMessage("Cola de renombrado vaciada.", 3000)
    def table_drag_enter(self, event):
        if event.source() == self.view.list_files:
            event.accept()
        else:
            event.ignore()

    def table_drop(self, event):
        if event.source() == self.view.list_files:
            items = self.view.list_files.selectedItems()
            added = False
            for item in items:
                name = item.text()
                file_info = next((f for f in self.engine.files_state if f['current'] == name), None)
                if file_info:
                    if not any(b['current'] == name for b in self.engine.batch_state):
                        self.engine.batch_state.append(file_info.copy())
                        added = True
            if added:
                self.update_preview()
            event.accept()
        else:
            event.ignore()

    def show_batch_context_menu(self, pos):
        menu = QMenu()
        remove_action = menu.addAction(QIcon.fromTheme("list-remove"), "Quitar de la lista")
        clear_action = menu.addAction(QIcon.fromTheme("edit-clear-all"), "Vaciar todo")
        
        action = menu.exec(self.view.table_batch.mapToGlobal(pos))
        if action == remove_action:
            rows = sorted(set(index.row() for index in self.view.table_batch.selectedIndexes()), reverse=True)
            for row in rows:
                if 0 <= row < len(self.engine.batch_state):
                    self.engine.batch_state.pop(row)
            self.update_preview()
        elif action == clear_action:
            self.on_clear_batch()

    def on_batch_reordered(self, p, s, e, d, r):
        # Sincronizar el estado del motor tras arrastrar filas en la tabla
        if s != r:
            item = self.engine.batch_state.pop(s)
            self.engine.batch_state.insert(r, item)
            self.update_preview()
    
    def on_show_history(self):
        if not self.engine.history_log:
            QMessageBox.information(self, "Historial", "No hay registros de renombrado en esta sesión.")
            return
            
        history_text = ""
        for entry in self.engine.history_log:
            history_text += f"[{entry['timestamp']}]\n DE: {entry['old']}\n A:  {entry['new']}\n{'-'*40}\n"
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Historial de Renombrado")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        
        viewer = QTextEdit()
        viewer.setReadOnly(True)
        viewer.setText(history_text)
        layout.addWidget(viewer)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.exec()

    def show_context_menu(self, pos):
        menu = QMenu()
        open_action = menu.addAction(QIcon.fromTheme("document-open"), "Abrir / Reproducir")
        add_batch_action = menu.addAction(QIcon.fromTheme("list-add"), "Añadir a cola de renombrado")
        menu.addSeparator()
        copy_name_action = menu.addAction(QIcon.fromTheme("edit-copy"), "Copiar nombre")
        menu.addSeparator()
        # --- NUEVO: Acción de Papelera ---
        delete_action = menu.addAction(QIcon.fromTheme("user-trash"), "Mover a la papelera")
        
        action = menu.exec(self.view.list_files.mapToGlobal(pos))
        
        if action == open_action:
            item = self.view.list_files.itemAt(pos)
            if item: self.on_item_double_clicked(item)
        elif action == add_batch_action:
            items = self.view.list_files.selectedItems()
            added = False
            for item in items:
                name = item.text()
                file_info = next((f for f in self.engine.files_state if f['current'] == name), None)
                if file_info and not any(b['current'] == name for b in self.engine.batch_state):
                    self.engine.batch_state.append(file_info.copy())
                    added = True
            if added: self.update_preview()
        elif action == copy_name_action:
            item = self.view.list_files.itemAt(pos)
            if item: QApplication.clipboard().setText(item.text())
        elif action == delete_action:
            item = self.view.list_files.itemAt(pos)
            if item: self.on_delete_file(item)

    def on_delete_file(self, item):
        import os
        from PyQt6.QtCore import QFile
        
        file_name = item.text()
        
        # 1. Pedir confirmación para no borrar por accidente
        reply = QMessageBox.question(
            self, 
            "Confirmar Borrado", 
            f"¿Estás seguro de que deseas enviar este archivo a la papelera?\n\n{file_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            carpeta = getattr(self.engine, 'current_dir', 
                      getattr(self.engine, 'directory', 
                      getattr(self.engine, 'current_directory', '')))
            
            ruta_completa = os.path.join(carpeta, file_name)
            
            # Detener el reproductor por si está leyendo ese mismo archivo
            self.view.media_player.stop()
            
            # 2. Enviar a la papelera del sistema (KDE/Wayland nativo)
            if QFile.moveToTrash(ruta_completa):
                # 3. Limpiarlo de las listas internas del motor
                self.engine.files_state = [f for f in self.engine.files_state if f['current'] != file_name]
                self.engine.batch_state = [b for b in self.engine.batch_state if b['current'] != file_name]
                
                # 4. Actualizar la interfaz
                self.refresh_ui_list()
                self.update_preview()
                self.view.status_bar.showMessage(f"Enviado a la papelera: {file_name}", 5000)
            else:
                QMessageBox.critical(self, "Error", f"No se pudo mover el archivo a la papelera.\nVerifica los permisos de: {ruta_completa}")

    def on_clear_list(self):
        self.engine.files_state = []
        self.engine.batch_state = []
        self.refresh_ui_list()
        self.update_preview()
        self.view.status_bar.showMessage("Lista de archivos vaciada.", 3000)

if __name__ == "__main__":
    # La aplicación debe crearse ANTES que el Splash para inicializar el motor gráfico
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 🌟 EXTRAER E INYECTAR LA FUENTE NATIVA DE KDE PLASMA
    system_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
    app.setFont(system_font)

    # 1. Lanzar Splash profesional
    splash = ReyLagSplash()
    splash.show()
    app.processEvents()  # Forzar dibujado inicial

    try:
        # 2. Inicializar la ventana (sin mostrarla aún)
        window = MainWindow()

        def finalizar_arranque():
            # Cerramos el splash con elegancia y mostramos la ventana
            splash.finish(window)
            window.show()

            # 3. Lanzar el diálogo de restauración DESPUÉS de que la ventana sea visible
            # Esto evita que los diálogos aparezcan flotando sobre el Splash
            QTimer.singleShot(100, window.restore_settings)

        # Esperamos 2.5 segundos para dar presencia de marca y estabilizar drivers
        QTimer.singleShot(2500, finalizar_arranque)

        sys.exit(app.exec())
    except Exception as e:
        print(f"Error crítico en el arranque: {e}")
        sys.exit(1)
