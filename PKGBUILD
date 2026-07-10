# Maintainer: Antonio Jose Lage Rey (Tony) <tony@reylag.studio>
pkgname=reylag-rename-studio
pkgver=2.1.4
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
    # Usamos $startdir para apuntar con precisión láser a la carpeta donde lanzaste makepkg
    REAL_DIST="$startdir/dist/reylag-rename-studio"

    # Comprobación de seguridad estricta
    if [ ! -d "$REAL_DIST" ]; then
        echo "ERROR CRÍTICO: No se encontró la carpeta compilada en $REAL_DIST"
        echo "Asegúrate de haber ejecutado primero el comando de PyInstaller."
        exit 1
    fi

    # 1. Crear directorios en la jerarquía segura del sistema
    install -d "$pkgdir/opt/reylag-rename-studio"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps"

    # 2. Copiar el binario compilado por PyInstaller
    cp -r "$REAL_DIST"/* "$pkgdir/opt/reylag-rename-studio/"

    # 3. Crear el enlace simbólico global para que funcione en la terminal
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
