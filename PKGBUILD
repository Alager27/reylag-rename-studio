# Maintainer: Antonio Jose Lage Rey (Tony) <tony@reylag.studio>
pkgname=reylag-rename-studio
pkgver=2.0.0
pkgrel=1
pkgdesc="Herramienta profesional de renombrado de video con visor integrado multimedia, optimizada para entornos Linux."
arch=('x86_64')
url="https://github.com/Alager27/reylag-rename-studio"
license=('GPL3')
depends=('python' 'qt6-multimedia' 'qt6-base' 'ffmpeg')
provides=('reylag-rename-studio')
conflicts=('reylag-rename-studio-git' 'rename-video-kde' 'reylag-rename-studio-bin')
replaces=('rename-video-kde' 'reylag-rename-studio-bin')

# Colocamos el icono en las fuentes del paquete (debe estar en la misma carpeta que este PKGBUILD al empaquetar)
source=("reylag_icon.png")
sha256sums=('7c972a28f98f7d9aa911f7da8f5e87729e4b055feaa3ef39cb312664df398c40')

package() {
    # Buscamos la carpeta dist de PyInstaller.
    # Dependiendo de tu entorno de construcción, estará un nivel atrás o directamente en srcdir
    if [ -d "$srcdir/../dist/reylag-rename-studio" ]; then
        REAL_DIST="$srcdir/../dist/reylag-rename-studio"
    elif [ -d "$srcdir/dist/reylag-rename-studio" ]; then
        REAL_DIST="$srcdir/dist/reylag-rename-studio"
    else
        # Si ejecutas makepkg en la raíz del proyecto
        REAL_DIST="$srcdir/reylag-rename-studio"
    fi

    # 1. Crear directorios en la jerarquía segura del sistema
    install -d "$pkgdir/opt/reylag-rename-studio"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps"

    # 2. Copiar el binario compilado por PyInstaller
    if [ -d "$REAL_DIST" ]; then
        cp -r "$REAL_DIST"/* "$pkgdir/opt/reylag-rename-studio/"
    else
        echo "ERROR: No se encontró el directorio de distribución en $REAL_DIST"
        exit 1
    fi

    # 3. Crear el enlace simbólico global
    ln -s /opt/reylag-rename-studio/reylag-rename-studio "$pkgdir/usr/bin/reylag-rename-studio"

    # 4. Instalar el icono propio desde las fuentes seguras del sandbox
    if [ -f "$srcdir/reylag_icon.png" ]; then
        install -m644 "$srcdir/reylag_icon.png" "$pkgdir/usr/share/pixmaps/reylag-rename-studio.png"
    fi

    # 5. Crear el lanzador .desktop apuntando al binario y al icono globales
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
