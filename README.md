# 🎬 ReyLag Rename Studio

**ReyLag Rename Studio** es una suite profesional de escritorio diseñada específicamente para editores de vídeo, realizadores audiovisuales y archivistas. Su objetivo es resolver uno de los mayores cuellos de botella en la postproducción: **la visualización, clasificación y renombrado masivo de cientos de clips de vídeo.**

Olvídate de abrir y cerrar reproductores externos o pelear con el explorador de archivos. ReyLag Rename Studio unifica un reproductor multimedia de alto rendimiento con un motor de renombrado avanzado en una sola interfaz limpia y optimizada.

## 🚀 ¿Por qué usar ReyLag Rename Studio?

Cuando llegas de un rodaje, un evento o una sesión de grabación, te enfrentas a carpetas llenas de archivos con nombres genéricos (`0001.mp4`, `DSC_0594.mov`). Renombrarlos uno a uno para tu software de edición (Premiere, DaVinci, Final Cut) es lento y propenso a errores. 

Esta herramienta te permite previsualizar cada toma al instante, aplicar nombres descriptivos a la velocidad del rayo mediante atajos de teclado y autocompletado, y ejecutar cambios masivos en lote con total seguridad.

## ✨ Características Principales

* **🖥️ Visor Integrado de Alto Rendimiento:** Basado en Qt6 y FFmpeg, reproduce tus clips al instante sin latencia. Incluye herramientas de análisis visual como control de volumen, línea de tiempo y un potente **Zoom en vivo (hasta 400%)** para comprobar el foco de tus tomas sin salir de la app.
* **🧠 Diccionario Inteligente y Autocompletado:** El programa "aprende" de ti. Cada vez que escribes un término (ej. "Toma_Exterior", "Entrevista_Plano_Corto"), se guarda en un diccionario persistente. Al teclear unas pocas letras en el futuro, te sugerirá la frase completa.
* **🛡️ Escudo Anticolisiones:** Nunca sobrescribirás un archivo por accidente. El sistema detecta si estás intentando asignar un nombre que ya existe y bloquea la operación para proteger tus datos.
* **⏪ Sistema de Deshacer (Undo/Redo):** ¿Te equivocaste al renombrar 50 archivos? Pulsa `Ctrl+Z` y todo volverá a su estado original al instante.
* **🗑️ Gestión Segura de Archivos:** Limpia tus tomas falsas directamente desde la aplicación. Envíalas a la papelera del sistema de forma segura con un clic derecho, sin borrados destructivos.
* **📸 Capturas de Pantalla Nativas:** Extrae fotogramas clave con un solo clic. Ideal para crear *storyboards* o miniaturas.

## ⚡ Flujo de Trabajo Ninja (Atajos de Teclado)

La interfaz está diseñada para que puedas editar cientos de clips sin tocar el ratón:

| Atajo | Acción |
| :--- | :--- |
| **Space** | Reproducir / Pausar el vídeo actual. |
| **Enter** | Aplica el nuevo nombre, guarda en el historial y **salta automáticamente al siguiente vídeo** reproduciéndolo al instante. |
| **Ctrl + Z** | Deshacer el último renombrado (individual o masivo). |
| **Ctrl + S** | Tomar una captura de pantalla del fotograma actual. |
| **Ctrl + 1 al 4** | Inyectar "Etiquetas Rápidas" personalizables directamente en el nombre del archivo. |

## ⚙️ Modos de Renombrado en Lote

Además del renombrado individual manual, ReyLag Rename Studio cuenta con un motor para procesar colas de trabajo:
1. **Formato:** Renombra secuencialmente (ej. `Boda_Madrid_001`, `Boda_Madrid_002`).
2. **Reemplazar:** Busca una palabra en decenas de archivos y cámbiala por otra.
3. **Añadir Texto:** Inserta prefijos o sufijos (ej. añadir `_PROXY` a todos los vídeos seleccionados).
4. **Avanzado:** Limpieza automática de espacios, caracteres especiales y capitalización.

## 🛠️ Requisitos e Instalación

ReyLag Rename Studio está construido sobre Python y PyQt6, con soporte nativo para entornos modernos de Linux (Wayland/X11), Windows y macOS.

**Dependencias:**
```bash
pip install PyQt6
```

(Nota para usuarios de Linux: Se recomienda tener instalados los paquetes multimedia base del sistema, como ffmpeg y los plugins de Qt6).

**Ejecución:**
```bash
python main.py
```
