# 🎬 ReyLag Rename Studio (V2.0.0)

**ReyLag Rename Studio** es una suite profesional de escritorio diseñada específicamente para editores de vídeo, realizadores audiovisuales y archivistas. Su objetivo es resolver uno de los mayores cuellos de botella en la postproducción: **la visualización, clasificación y renombrado masivo de cientos de clips de vídeo.**

Olvídate de abrir y cerrar reproductores externos o pelear con el explorador de archivos. ReyLag Rename Studio unifica un reproductor multimedia de alto rendimiento con un motor de renombrado avanzado en una sola interfaz limpia, optimizada y multilingüe.

---

## 📸 Vista de la Aplicación

![Interfaz de ReyLag Rename Studio](https://raw.githubusercontent.com/Alager27/reylag-rename-studio/main/screenshot.png)

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

## ⚙️ Modos de Renombrado en Lote (Procesamiento Masivo)

Además del flujo de trabajo manual e individual, la aplicación incorpora un potente motor secundario automatizado para procesar colas de trabajo masivas sobre múltiples archivos simultáneamente:

* **🔢 Formato Secuencial (Numeración):** Permite renombrar colecciones enteras aplicando un prefijo común y un índice numérico correlativo configurable (ej. transformar una ráfaga en `Boda_Postigo_001.mp4`, `Boda_Postigo_002.mp4`, `Boda_Postigo_003.mp4`).
* **🔄 Reemplazar Texto / Cadenas:** Escanea los nombres de los archivos seleccionados, localiza un patrón de texto específico, un error o un tag molesto y lo sustituye por la palabra que decidas de una sola pasada.
* **➕ Añadir Texto (Prefijos y Sufijos):** Inyecta texto de manera masiva al inicio o al final de los nombres existentes sin alterar el resto del identificador (ej. añadir el sufijo `_PROXY` o el prefijo `4K_` a 50 clips a la vez).
* **🧹 Limpieza Avanzada de Strings:** Corrección automatizada que purga de golpe espacios dobles o huérfanos, elimina caracteres especiales incompatibles con sistemas de archivos y ofrece control estricto de capitalización (convertir todo a Mayúsculas, Minúsculas o formato Tipo Título).

---

## 🛠️ Requisitos e Instalación (Arch Linux)

ReyLag Rename Studio está optimizado para integrarse de forma nativa en sistemas Linux modernos (Wayland/X11) bajo el entorno de escritorio **KDE Plasma**. 

> ⚠️ **Nota sobre entornos gestionados:** Debido a las directivas de seguridad de las distribuciones Linux actuales (PEP 668), **no se debe utilizar `pip install` de forma global**, ya que rompería el gestor de paquetes. La instalación se realiza de manera nativa e impecable a través de `pacman`.

### 📦 1. Dependencias del Sistema
El núcleo multimedia y gráfico se apoya directamente en las librerías oficiales de tu distribución. Asegúrate de tenerlas instaladas ejecutando:
```bash
sudo pacman -S python qt6-multimedia qt6-base ffmpeg

🔨 2. Compilación y Empaquetado Nativo

El repositorio incluye un entorno de empaquetado oficial optimizado con soporte para los menús del sistema e iconos en alta resolución.
Bash

# Entra en la carpeta del empaquetador oficial donde reside el PKGBUILD
cd reylag-rename-studio/arch-package

# Compila el paquete nativo, resuelve dependencias e instala limpiando conflictos previos
makepkg -fsi

🖥️ Cómo Ejecutar la Aplicación

Una vez completado el paso de pacman, la aplicación queda completamente integrada en la jerarquía de tu sistema operativo:

    Desde el Escritorio: Pulsa la tecla Super (o abre tu lanzador KRunner), escribe ReyLag Rename Studio y haz clic sobre su icono oficial para iniciar la interfaz gráfica.

    Desde la Terminal: Invoca la aplicación de forma global desde cualquier ruta ejecutando:
    Bash

    reylag-rename-studio
