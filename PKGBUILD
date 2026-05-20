# Maintainer: Antonio Jose Lage Rey (Tony) <tony@reylag.studio>
pkgname=reylag-rename-studio
pkgver=2.0.1
pkgrel=1
pkgdesc="Herramienta profesional de renombrado de video con visor integrado multimedia, optimizada para entornos Linux."
arch=('x86_64')
url="https://github.com/Alager27/reylag-rename-studio"
license=('GPL3')
depends=('python' 'qt6-multimedia' 'qt6-base' 'ffmpeg')
provides=('reylag-rename-studio')
# Añadido reylag-rename-studio-bin para evitar el bloqueo que sufriste
conflicts=('reylag-rename-studio-git' 'rename-video-kde' 'reylag-rename-studio-bin')
replaces=('rename-video-kde' 'reylag-rename-studio-bin')

source=()

package() {
    BASE_DIR="$srcdir/.."

    # Validar ruta del binario de PyInstaller
    if [ -d "$BASE_DIR/../dist/reylag-rename-studio" ]; then
        REAL_DIST="$BASE_DIR/../dist/reylag-rename-studio"
    else
        REAL_DIST="$BASE_DIR/reylag-rename-studio"
    fi

    # 1. Crear directorios en la jerarquía del sistema
    install -d "$pkgdir/opt/reylag-rename-studio"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps" # Directorio global para iconos

    # 2. Copiar el binario compilado
    cp -r "$REAL_DIST"/* "$pkgdir/opt/reylag-rename-studio/"

    # 3. Crear el enlace simbólico global
    ln -s /opt/reylag-rename-studio/reylag-rename-studio "$pkgdir/usr/bin/reylag-rename-studio"

    # 4. INSTALAR EL ICONO PROPIO (Busca el png que tienes en la carpeta actual)
    if [ -f "$BASE_DIR/reylag_icon.png" ]; then
        install -m644 "$BASE_DIR/reylag_icon.png" "$pkgdir/usr/share/pixmaps/reylag-rename-studio.png"
    fi

    # 5. Crear el lanzador .desktop apuntando al icono empaquetado
    cat <<EOF> "$pkgdir/usr/share/applications/reylag-rename-studio.desktop"
[Desktop Entry]
Name=ReyLag Rename Studio
Exec=reylag-rename-studio
Icon=reylag-rename-studio
Type=Application
Categories=AudioVideo;Video;Utility;
Comment=Renombrado inteligente de archivos de video con previsualización en tiempo real.
Terminal=false
StartupNotify=true
EOF
}
