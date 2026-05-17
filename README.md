# 🎬 ReyLag Rename Studio (V2.0.0)

**ReyLag Rename Studio** es una suite profesional de escritorio diseñada específicamente para editores de vídeo, realizadores audiovisuales y archivistas. Su objetivo es resolver uno de los mayores cuellos de botella en la postproducción: **la visualización, clasificación y renombrado masivo de cientos de clips de vídeo.**

Olvídate de abrir y cerrar reproductores externos o pelear con el explorador de archivos. ReyLag Rename Studio unifica un reproductor multimedia de alto rendimiento con un motor de renombrado avanzado en una sola interfaz limpia, optimizada y multilingüe.

---

## 🚀 ¿Por qué usar ReyLag Rename Studio?

Cuando llegas de un rodaje, un evento o una sesión de grabación, te enfrentas a carpetas llenas de archivos con nombres genéricos (`0001.mp4`, `DSC_0594.mov`). Renombrarlos uno a uno para tu software de edición (Premiere, DaVinci, Final Cut) es lento y propenso a errores. 

Esta herramienta te permite:
* **Previsualizar** cada toma al instante y sin latencia de carga.
* **Aplicar nombres descriptivos** a la velocidad del rayo mediante atajos de teclado y autocompletado.
* **Ejecutar cambios masivos** en lote con total seguridad para tu almacenamiento.

---

## ✨ Características Principales

* **🖥️ Visor Integrado de Alto Rendimiento:** Basado en Qt6 y FFmpeg, reproduce tus clips al instante. Incluye control de volumen, línea de tiempo interactiva y un potente **Zoom en vivo (hasta 400%)** para comprobar el foco de tus tomas críticas sin salir de la app.
* **🧠 Diccionario Inteligente y Autocompletado:** El programa aprende de ti. Cada vez que confirmas un término (ej. *Toma_Exterior*, *Entrevista_Plano_Corto*), se guarda en un diccionario persistente local. Al teclear unas pocas letras en el futuro, te sugerirá la frase completa.
* **🛡️ Escudo Anticolisiones:** Nunca sobrescribirás un archivo por accidente. El sistema detecta si estás intentando asignar un nombre que ya existe en el directorio y bloquea la operación para proteger el material original.
* **⏪ Sistema de Deshacer Completo (Undo/Redo):** ¿Te equivocaste al renombrar un lote entero de archivos? Pulsa `Ctrl+Z` y todo el disco volverá a su estado original de inmediato.
* **🗑️ Gestión Segura de Descartes:** Limpia tus tomas falsas directamente desde la aplicación. Envíalas a la papelera del sistema de forma segura mediante el menú contextual, sin borrados destructivos directos.
* **📸 Capturas de Pantalla Nativas:** Extrae fotogramas clave en alta resolución con un solo clic. Ideal para la creación rápida de *storyboards*, miniaturas o referencias de color.

---

## ⚡ Flujo de Trabajo Ninja (Atajos de Teclado)

La interfaz está diseñada estratégicamente para que puedas catalogar y procesar cientos de clips sin necesidad de despegar las manos del teclado:

| Atajo | Acción |
| :--- | :--- |
| <kbd>Space</kbd> | Reproducir / Pausar el vídeo actual. |
| <kbd>Enter</kbd> | Aplica el nombre, lo guarda en el historial y **salta al siguiente vídeo** reproduciéndolo al instante. |
| <kbd>Ctrl + Z</kbd> | Deshacer el último renombrado (tanto individual como procesamiento por lotes). |
| <kbd>Ctrl + S</kbd> | Tomar una captura de pantalla del fotograma actual en reproducción. |
| <kbd>Ctrl + 1</kbd> al <kbd>4</kbd> | Inyectar "Etiquetas Rápidas" personalizables directamente en la caja de texto. |

---

## ⚙️ Modos de Renombrado en Lote

Además del flujo de trabajo individual, la suite cuenta con un motor secundario para procesar colas de trabajo masivas:

1. **Formato Secuencial:** Renombra con numeración automática (ej. `Proyecto_Final_001`, `Proyecto_Final_002`).
2. **Reemplazar Cadena:** Busca una palabra o prefijo erróneo en decenas de archivos y lo sustituye de golpe.
3. **Añadir Texto:** Inserta prefijos o sufijos en bloque (ej. añadir el tag `_PROXY` o `_4K` a todos los elementos seleccionados).
4. **Limpieza Avanzada:** Normalización automática de espacios dobles, eliminación de caracteres especiales incompatibles y control estricto de capitalización (Mayúsculas/Minúsculas).

---

## 🛠️ Requisitos e Instalación (Arch Linux)

ReyLag Rename Studio está optimizado para integrarse de forma nativa en sistemas Linux modernos (Wayland/X11) bajo el entorno de escritorio **KDE Plasma**. 

> ⚠️ **Nota sobre entornos gestionados:** Debido a las directivas de seguridad de las distribuciones Linux actuales (PEP 668), **no se debe utilizar `pip install` de forma global**, ya que rompería el gestor de paquetes. La instalación se realiza de manera nativa e impecable a través de `pacman`.

### 📦 1. Dependencias del Sistema
El núcleo multimedia y gráfico se apoya directamente en las librerías oficiales de tu distribución. Asegúrate de tenerlas instaladas ejecutando:
```bash
sudo pacman -S python qt6-multimedia qt6-base ffmpeg
