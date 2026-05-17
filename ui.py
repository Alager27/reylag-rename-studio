#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QLineEdit, QComboBox, QSplitter, QGroupBox, QFormLayout,
    QFrame, QSlider, QToolButton, QStatusBar, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QCompleter, QSizePolicy, QGraphicsScene, QGraphicsView,
    QDialog, QInputDialog, QMessageBox, QTextEdit
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtGui import QIcon, QFont, QPainter, QColor, QPen, QBrush, QPixmap, QTextCursor, QTextDocument
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt, QSize, QStringListModel, QTimer



class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.pos().x()) / self.width()
            self.setValue(int(val))
            self.sliderMoved.emit(int(val))
        super().mousePressEvent(event)

class VideoRenamerUI:
    """
    Vista / Frontend: Construye la interfaz y sus widgets.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        
        # Inicialización fantasma para evitar errores de traducción prematuros
        from PyQt6.QtWidgets import QLabel
        self.lbl_step1 = QLabel()
        self.lbl_step2 = QLabel()
        self.lbl_step3 = QLabel()
        
        self.translations = {
            "es": {
                "step1": "1. EXPLORADOR", "step2": "2. VISOR VIDEO", "step3": "3. ACCIÓN REAL",
                "open_dir": "Abrir Carpeta", "filter": "🔍 Filtrar archivos...",
                "group_edit": "Edición de Nombre Seleccionado", "btn_apply": " Actualizar Nombre en la Lista",
                "group_rules": "Reglas de Renombrado", "execute": "EJECUTAR EN DISCO",
                "btn_reset": " Limpiar Reglas", "preview_lbl": "Previsualización:",
                "menu_file": "&Archivo", "menu_edit": "&Editar", "menu_pref": "&Preferencias", "lang": "Idioma",
                "refresh": "Actualizar lista"
            },
            "en": {
                "step1": "1. EXPLORER", "step2": "2. VIDEO VIEWER", "step3": "3. EXECUTE ACTION",
                "open_dir": "Open Folder", "filter": "🔍 Filter files...",
                "group_edit": "Selected Item Metadata", "btn_apply": " Update Name in List",
                "group_rules": "Renaming Rules", "execute": "RUN RENAMER",
                "btn_reset": " Reset Rules", "preview_lbl": "Preview:",
                "menu_file": "&File", "menu_edit": "&Edit", "menu_pref": "&Preferences", "lang": "Language",
                "refresh": "Refresh list"
            },
            "gl": {
                "step1": "1. EXPLORADOR", "step2": "2. VISOR VIDEO", "step3": "3. ACCIÓN REAL",
                "open_dir": "Abrir Carpeta", "filter": "🔍 Filtrar arquivos...",
                "group_edit": "Edición de Nome Seleccionado", "btn_apply": " Actualizar Nome na Lista",
                "group_rules": "Regras de Renomeado", "execute": "EXECUTAR EN DISCO",
                "btn_reset": " Limpar Regras", "preview_lbl": "Previsualización:",
                "menu_file": "&Archivo", "menu_edit": "&Editar", "menu_pref": "&Preferencias", "lang": "Idioma",
                "refresh": "Actualizar lista"
            }
        }
        self.setup_ui()

    def create_menu_bar(self):
        self.menu_bar = self.main_window.menuBar()

        # Menú Archivo
        self.file_menu = self.menu_bar.addMenu("&Archivo")
        self.action_open_dir = self.file_menu.addAction(QIcon.fromTheme("folder-open"), "Abrir Carpeta...")
        self.action_open_file = self.file_menu.addAction(QIcon.fromTheme("document-open"), "Abrir Archivo...")
        self.file_menu.addSeparator()
        self.action_history = self.file_menu.addAction(QIcon.fromTheme("view-history"), "Historial de Modificaciones")
        self.file_menu.addSeparator()
        self.action_exit = self.file_menu.addAction(QIcon.fromTheme("application-exit"), "Salir")

        # Menú Editar
        self.edit_menu = self.menu_bar.addMenu("&Editar")
        self.action_undo = self.edit_menu.addAction(QIcon.fromTheme("edit-undo"), "Deshacer renombrado")
        self.action_redo = self.edit_menu.addAction(QIcon.fromTheme("edit-redo"), "Rehacer")
        self.edit_menu.addSeparator()
        self.action_clear = self.edit_menu.addAction(QIcon.fromTheme("edit-clear-list"), "Limpiar lista")

        # Menú Preferencias
        self.pref_menu = self.menu_bar.addMenu("&Preferencias")
        self.lang_menu = self.pref_menu.addMenu(QIcon.fromTheme("preferences-desktop-locale"), "Idioma")

        self.action_lang_es = self.lang_menu.addAction("Español")
        self.action_lang_en = self.lang_menu.addAction("English")
        self.action_lang_gl = self.lang_menu.addAction("Galego")

        for action in [self.action_lang_es, self.action_lang_en, self.action_lang_gl]:
            action.setCheckable(True)
        self.action_lang_es.setChecked(True)

    def setup_ui(self):
        # Inicializamos las etiquetas de pasos para que el traductor las encuentre siempre
        self.lbl_step1 = QLabel()
        self.lbl_step2 = QLabel()
        self.lbl_step3 = QLabel()
        
        self.create_menu_bar()
        self.central_widget = QWidget()
        self.main_window.setCentralWidget(self.central_widget)

        # 1. Crear el layout principal y el splitter primero
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 2. CREAR LOS CONTENEDORES (WIDGETS) DE IZQUIERDA A DERECHA
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. Panel de Explorador ---
        self.lbl_step1 = QLabel("1. EXPLORADOR")
        group_explorer = QGroupBox()
        layout_explorer = QVBoxLayout(group_explorer)
        layout_explorer.addWidget(self.lbl_step1)

        layout_botones_carpeta = QHBoxLayout()
        self.btn_open = QPushButton(QIcon.fromTheme("folder-open"), " Abrir Carpeta")
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_refresh = QPushButton(QIcon.fromTheme("view-refresh"), "")
        self.btn_refresh.setFixedWidth(40)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setToolTip("Actualizar lista de archivos")
        
        layout_botones_carpeta.addWidget(self.btn_open)
        layout_botones_carpeta.addWidget(self.btn_refresh)
        layout_explorer.addLayout(layout_botones_carpeta)

        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText("🔍 Filtrar archivos...")
        self.edit_filter.setClearButtonEnabled(True)
        layout_explorer.addWidget(self.edit_filter)
        
        self.list_files = QListWidget()
        self.list_files.setAlternatingRowColors(True)
        self.list_files.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_files.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_files.setDragEnabled(True)
        layout_explorer.addWidget(self.list_files)

        # 3. AHORA SÍ: Añadir el grupo al layout que ya existe
        self.left_layout.addWidget(group_explorer)

        # --- COLUMNA 2: REPRODUCTOR ---
        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)

        self.lbl_step2 = QLabel("<b>2. VISOR VIDEO</b>")

        self.video_container = QFrame()
        self.video_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.video_container.setStyleSheet("background-color: #000; border-radius: 4px;")
        video_vbox = QVBoxLayout(self.video_container)
        video_vbox.setContentsMargins(0,0,0,0)

        self.graphics_scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.graphics_view.setStyleSheet("background-color: #000; border: none;")
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.video_item = QGraphicsVideoItem()
        self.graphics_scene.addItem(self.video_item)

        video_vbox.addWidget(self.graphics_view)

        # Barra de progreso y tiempo (ocupa el 100% del ancho)
        progress_layout = QHBoxLayout()
        self.slider_progress = ClickableSlider(Qt.Orientation.Horizontal)
        
        # --- NUEVO: Estilo visual de la barra de progreso ---
        self.slider_progress.setStyleSheet("""
            QSlider::groove:horizontal {
                border-radius: 2px;
                height: 4px;
                background: #333333;
            }
            QSlider::sub-page:horizontal {
                background: #3DAEE9; /* Azul característico de KDE/Qt */
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3DAEE9;
                width: 12px;
                height: 12px;
                margin: -4px 0; /* Centra la bolita en la línea */
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #61C0F0; /* Azul más claro al pasar el ratón */
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)
        # ---------------------------------------------------
        
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setStyleSheet("font-family: monospace;")
        progress_layout.addWidget(self.slider_progress)
        progress_layout.addWidget(self.lbl_time)
        video_vbox.addLayout(progress_layout)

        # --- Controles Multimedia (Solo Botones) ---
        media_ctrl_layout = QHBoxLayout()
        
        self.btn_prev = QToolButton()
        self.btn_prev.setIcon(QIcon.fromTheme("media-skip-backward"))
        self.btn_prev.setFixedSize(40, 40)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setToolTip("Archivo Anterior")

        self.btn_play = QToolButton()
        self.btn_play.setIcon(QIcon.fromTheme("media-playback-start"))
        self.btn_play.setFixedSize(40, 40)
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_next = QToolButton()
        self.btn_next.setIcon(QIcon.fromTheme("media-skip-forward"))
        self.btn_next.setFixedSize(40, 40)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip("Siguiente Archivo")

        self.btn_mute = QToolButton()
        self.btn_mute.setIcon(QIcon.fromTheme("audio-volume-high"))
        self.btn_mute.setFixedSize(40, 40)

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(70)
        self.slider_volume.setFixedWidth(100)

        self.btn_screenshot = QToolButton()
        self.btn_screenshot.setIcon(QIcon.fromTheme("camera-photo"))
        self.btn_screenshot.setFixedSize(40, 40)

        # Zoom and Fullscreen
        zoom_layout = QHBoxLayout()
        self.lbl_zoom = QLabel("Zoom: 100%")
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(100, 400)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(120)
        
        self.btn_fullscreen = QToolButton()
        self.btn_fullscreen.setIcon(QIcon.fromTheme("view-fullscreen"))
        self.btn_fullscreen.setFixedSize(40, 40)
        self.btn_fullscreen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fullscreen.setToolTip("Pantalla Completa")

        zoom_layout.addWidget(self.lbl_zoom)
        zoom_layout.addWidget(self.slider_zoom)
        zoom_layout.addWidget(self.btn_fullscreen)

        # Añadimos TODOS los botones al layout de controles
        media_ctrl_layout.addWidget(self.btn_prev)
        media_ctrl_layout.addWidget(self.btn_play)
        media_ctrl_layout.addWidget(self.btn_next)
        media_ctrl_layout.addWidget(self.btn_mute)
        media_ctrl_layout.addWidget(self.slider_volume)
        media_ctrl_layout.addWidget(self.btn_screenshot)
        media_ctrl_layout.addLayout(zoom_layout)

        self.group_edit = QGroupBox("Edición de Nombre Seleccionado")
        self.edit_form = QFormLayout()

        # Campo de texto + botón del gestor de diccionario, agrupados en fila
        self.name_input_layout = QHBoxLayout()
        self.edit_name = QLineEdit()
        self.edit_name.setMinimumHeight(30)
        self.edit_name.setPlaceholderText("Escribe el nuevo nombre...")

        self.btn_dict = QToolButton()
        self.btn_dict.setText("📖")
        self.btn_dict.setFixedHeight(30)
        self.btn_dict.setToolTip("Abrir Gestor del Diccionario")

        self.name_input_layout.addWidget(self.edit_name)
        self.name_input_layout.addWidget(self.btn_dict)

        self.completer_model = QStringListModel()
        self.completer = QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.edit_name.setCompleter(self.completer)

        self.edit_form.addRow("Nuevo Nombre:", self.name_input_layout)
        self.btn_apply_name = QPushButton(" Actualizar Nombre en la Lista")
        self.btn_apply_name.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        self.btn_apply_name.setMinimumHeight(40)
        self.edit_form.addRow(self.btn_apply_name)
        self.group_edit.setLayout(self.edit_form)

        center_layout.addWidget(self.lbl_step2)
        center_layout.addWidget(self.video_container, stretch=1)
        center_layout.addLayout(media_ctrl_layout)
        center_layout.addWidget(self.group_edit)

        # --- COLUMNA 3: MOTOR ---
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_step3 = QLabel("<b>3. ACCIÓN REAL</b>")
        self.group_rules = QGroupBox("Reglas de Renombrado")
        rules_layout = QVBoxLayout()

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Formato (Dolphin ###)", "Reemplazar texto", "Añadir texto", "Caso / Limpieza Avanzada"])
        self.combo_mode.setMinimumHeight(35)

        # Paneles de Reglas
        self.pane_format = QWidget()
        format_form = QFormLayout(self.pane_format)
        self.edit_template = QLineEdit("Video_###")
        self.edit_start_at = QLineEdit("1")
        format_form.addRow("Plantilla:", self.edit_template)
        format_form.addRow("Inicio:", self.edit_start_at)

        self.pane_replace = QWidget()
        replace_form = QFormLayout(self.pane_replace)
        self.edit_search = QLineEdit()
        self.edit_replace = QLineEdit()
        replace_form.addRow("Buscar:", self.edit_search)
        replace_form.addRow("Por:", self.edit_replace)
        self.pane_replace.hide()

        self.pane_add = QWidget()
        add_form = QFormLayout(self.pane_add)
        self.edit_add_text = QLineEdit()
        self.combo_pos = QComboBox()
        self.combo_pos.addItems(["Prefijo", "Sufijo"])
        add_form.addRow("Texto:", self.edit_add_text)
        add_form.addRow("Posición:", self.combo_pos)
        self.pane_add.hide()

        self.pane_advanced = QWidget()
        adv_layout = QVBoxLayout(self.pane_advanced)
        self.combo_case = QComboBox()
        self.combo_case.addItems(["Sin cambios", "Minúsculas", "MAYÚSCULAS", "Title Case"])
        self.check_clean_special = QCheckBox("Eliminar símbolos extra")
        self.check_clean_spaces = QCheckBox("Limpiar espacios dobles")
        adv_layout.addWidget(QLabel("Transformación de Caso:"))
        adv_layout.addWidget(self.combo_case)
        adv_layout.addWidget(self.check_clean_special)
        adv_layout.addWidget(self.check_clean_spaces)
        self.pane_advanced.hide()

        rules_layout.addWidget(self.combo_mode)
        rules_layout.addWidget(self.pane_format)
        rules_layout.addWidget(self.pane_replace)
        rules_layout.addWidget(self.pane_add)
        rules_layout.addWidget(self.pane_advanced)
        self.group_rules.setLayout(rules_layout)

        self.lbl_preview = QLabel("<b>Previsualización:</b>")
        self.table_batch = QTableWidget(0, 2)
        self.table_batch.setHorizontalHeaderLabels(["Original", "Nuevo Nombre"])
        self.table_batch.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_batch.setAlternatingRowColors(True)
        self.table_batch.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_batch.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_batch.setAcceptDrops(True)
        self.table_batch.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.table_batch.setStyleSheet("font-family: 'JetBrains Mono', 'Monospace'; font-size: 9pt;")

        self.btn_clear_batch = QPushButton(" Quitar todos")
        self.btn_clear_batch.setIcon(QIcon.fromTheme("edit-delete"))

        self.btn_reset = QPushButton(" Limpiar Reglas")
        self.btn_reset.setIcon(QIcon.fromTheme("edit-clear"))

        self.btn_execute = QPushButton(" EJECUTAR EN DISCO")
        self.btn_execute.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        self.btn_execute.setMinimumHeight(60)
        self.btn_execute.setFont(QFont("Noto Sans", 11, QFont.Weight.Bold))
        self.btn_execute.setCursor(Qt.CursorShape.PointingHandCursor)

        right_layout.addWidget(self.lbl_step3)
        right_layout.addWidget(self.group_rules)
        right_layout.addWidget(self.btn_reset)
        right_layout.addWidget(self.lbl_preview)
        right_layout.addWidget(self.table_batch)
        right_layout.addWidget(self.btn_clear_batch)
        right_layout.addWidget(self.btn_execute)

        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.center_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(1, 2)
        self.main_layout.addWidget(self.splitter)

        self.status_bar = QStatusBar()
        self.main_window.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para organizar.", 5000)

        # Setup Multimedia
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_item)

    def retranslate_ui(self, lang):
        # Aseguramos soporte para Gallego ("gl"), si no está, cae en Español ("es")
        t = self.translations.get(lang, self.translations.get('es'))

        # 1. Mapeo exacto de etiquetas de pasos (Pasamos de los fantasmas a los reales si existen)
        if hasattr(self, 'lbl_step1') and self.lbl_step1:
            self.lbl_step1.setText(f"<b>{t.get('step1', '1. EXPLORADOR')}</b>")
        if hasattr(self, 'lbl_step2') and self.lbl_step2:
            self.lbl_step2.setText(f"<b>{t.get('step2', '2. VISOR VIDEO')}</b>")
        if hasattr(self, 'lbl_step3') and self.lbl_step3:
            self.lbl_step3.setText(f"<b>{t.get('step3', '3. ACCIÓN REAL')}</b>")

        # 2. Mapeo de Botones y Campos de la interfaz real
        if hasattr(self, 'btn_open'):
            self.btn_open.setText(f" {t.get('open_dir', ' Abrir Carpeta')}")
        if hasattr(self, 'btn_execute'):
            self.btn_execute.setText(t.get('execute', ' EJECUTAR EN DISCO'))
        if hasattr(self, 'btn_refresh'):
            self.btn_refresh.setToolTip(t.get('refresh', 'Actualizar lista de archivos'))

        if hasattr(self, 'edit_filter'):
            self.edit_filter.setPlaceholderText(t.get("filter", "🔍 Filtrar archivos..."))
        if hasattr(self, 'group_edit'):
            self.group_edit.setTitle(t.get("group_edit", "Edición de Nombre Seleccionado"))
        if hasattr(self, 'btn_apply_name'):
            self.btn_apply_name.setText(t.get("btn_apply", " Actualizar Nombre en la Lista"))
        if hasattr(self, 'group_rules'):
            self.group_rules.setTitle(t.get("group_rules", "Reglas de Renombrado"))
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setText(t.get("btn_reset", " Limpiar Reglas"))
        if hasattr(self, 'lbl_preview'):
            self.lbl_preview.setText(f"<b>{t.get('preview_lbl', 'Previsualización:')}</b>")

        # 3. Mapeo de la Barra de Menús Superior
        if hasattr(self, 'file_menu'): self.file_menu.setTitle(t.get("menu_file", "&Archivo"))
        if hasattr(self, 'edit_menu'): self.edit_menu.setTitle(t.get("menu_edit", "&Editar"))
        if hasattr(self, 'pref_menu'): self.pref_menu.setTitle(t.get("menu_pref", "&Preferencias"))
        if hasattr(self, 'lang_menu'): self.lang_menu.setTitle(t.get("lang", "Idioma"))


class DictionaryDialog(QDialog):
    """Sub-ventana flotante para gestionar y buscar las palabras del diccionario en tiempo real."""

    def __init__(self, dict_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Diccionario de Videoteca — Editor y Buscador")
        self.resize(600, 700)
        self.dict_path = dict_path

        layout = QVBoxLayout(self)

        # --- 🔍 1. EL BUSCADOR NINJA ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar término, rol, categoría o ciudad...")
        self.search_input.setClearButtonEnabled(True)  # Añade la 'X' para limpiar rápido

        self.btn_next = QPushButton("Siguiente (Enter)")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_next)
        layout.addLayout(search_layout)

        # --- 📝 2. EL EDITOR DE TEXTO ---
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                font-family: monospace; 
                font-size: 13px;
                selection-background-color: #0078D7; /* Azul intenso */
                selection-color: white;
            }
        """)
        layout.addWidget(self.editor)

        # Cargar el archivo de texto en el editor
        self.load_dictionary()

        # --- 💾 3. BOTONES DE ACCIÓN ---
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Guardar y Actualizar")
        self.btn_save.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold;")
        self.btn_cancel = QPushButton("Cancelar")

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        # --- 🔗 4. CONEXIONES DE SEÑALES ---
        # Buscador
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.find_next)
        self.btn_next.clicked.connect(self.find_next)

        # Acciones
        self.btn_save.clicked.connect(self.save_dictionary)
        self.btn_cancel.clicked.connect(self.reject)

    def load_dictionary(self):
        """Carga el texto actual del archivo en el editor."""
        import os
        if os.path.exists(self.dict_path):
            with open(self.dict_path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())

    def on_search_changed(self):
        """Reacciona al texto, pero solo busca si hay 3 o más letras."""
        texto = self.search_input.text()

        # 1. Restauramos el estilo normal (por si estaba en rojo de una búsqueda fallida anterior)
        self.search_input.setStyleSheet("")

        # 2. REGLA NINJA: Mínimo 3 caracteres para empezar a buscar
        if len(texto) < 3:
            # Si hay menos de 3 letras, limpiamos el resaltado azul del texto para no marear
            cursor = self.editor.textCursor()
            cursor.clearSelection()
            self.editor.setTextCursor(cursor)
            return

        # 3. Si ya hay 3 letras o más, rebobinamos al principio y disparamos la búsqueda
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        self.find_next()

    def find_next(self):
        """Busca y resalta subcadenas (contenido) en bucle continuo."""
        texto = self.search_input.text()

        # Doble validación de seguridad
        if len(texto) < 3:
            return

        # find() busca por contenido (subcadena) e ignora mayúsculas/minúsculas
        encontrado = self.editor.find(texto)

        if not encontrado:
            # Si no encuentra más abajo, rebobinamos el cursor al principio
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)

            # Segundo intento desde arriba (Bucle)
            if not self.editor.find(texto):
                # Mantiene el estilo nativo de la caja, pero pone el texto y un borde sutil en rojo
                self.search_input.setStyleSheet("color: #ff4444; border: 1px solid #ff4444;")
                return

        # Si lo ha encontrado, aseguramos que la caja siga con su color normal
        self.search_input.setStyleSheet("")

    def save_dictionary(self):
        """Sobrescribe el archivo y cierra el diálogo con éxito."""
        import os
        # Asegurar que la carpeta existe antes de guardar
        os.makedirs(os.path.dirname(os.path.abspath(self.dict_path)), exist_ok=True)
        with open(self.dict_path, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())
        self.accept()

