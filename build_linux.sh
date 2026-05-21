#!/bin/bash
# build_linux.sh — Compila app_hue12.6 compatible con cualquier Linux moderno
# Requiere Docker instalado: sudo apt install docker.io

set -e

APP_PY="app_hue12.6.py"
APP_NAME="app_hue12.6"

echo "======================================"
echo "  Compilando $APP_NAME con Docker"
echo "  Base: Ubuntu 20.04 (GLIBC 2.31)"
echo "======================================"

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no está instalado."
    echo "Instalá con: sudo apt install docker.io && sudo usermod -aG docker \$USER"
    exit 1
fi

if [ ! -f "$APP_PY" ]; then
    echo "ERROR: No se encuentra $APP_PY en el directorio actual."
    exit 1
fi

echo ""
echo "[0/4] Corrigiendo configuración de credenciales de Docker..."
mkdir -p ~/.docker
if [ -f ~/.docker/config.json ]; then
    python3 -c "
import json
path = '$HOME/.docker/config.json'
with open(path) as f:
    cfg = json.load(f)
cfg.pop('credsStore', None)
cfg.pop('credStore', None)
with open(path, 'w') as f:
    json.dump(cfg, f, indent=2)
print('  config.json limpio')
" 2>/dev/null || echo '{}' > ~/.docker/config.json
else
    echo '{}' > ~/.docker/config.json
fi
echo "  ✓ Credenciales corregidas"

echo ""
echo "[1/4] Construyendo imagen Docker con Ubuntu 20.04..."
docker build -t hue-builder - << 'DOCKERFILE'
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    libgtk-3-0 \
    libcairo2 \
    libglib2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgirepository-1.0-1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pyinstaller requests pycairo

WORKDIR /build
DOCKERFILE

echo ""
echo "[2/4] Compilando dentro del contenedor..."
mkdir -p dist_compat
docker run --rm \
    -v "$(pwd)/$APP_PY:/build/$APP_PY:ro" \
    -v "$(pwd)/dist_compat:/build/dist" \
    hue-builder \
    bash -c "
        pyinstaller \
            --onefile \
            --name '$APP_NAME' \
            --hidden-import gi \
            --hidden-import gi.repository.Gtk \
            --hidden-import gi.repository.GLib \
            --hidden-import gi.repository.Gdk \
            --hidden-import gi.repository.GdkPixbuf \
            --hidden-import cairo \
            --hidden-import requests \
            --hidden-import urllib3 \
            --hidden-import certifi \
            --hidden-import charset_normalizer \
            --hidden-import idna \
            '$APP_PY' && \
        cp dist/'$APP_NAME' /build/dist/
    "

echo ""
echo "[3/4] Verificando el binario generado..."
if [ -f "dist_compat/$APP_NAME" ]; then
    chmod +x "dist_compat/$APP_NAME"
    SIZE=$(du -sh "dist_compat/$APP_NAME" | cut -f1)
    echo "  ✓ Binario: dist_compat/$APP_NAME ($SIZE)"
else
    echo "ERROR: No se generó el binario."
    exit 1
fi

echo ""
echo "[4/4] Listo!"
echo ""
echo "  Ejecutable: $(pwd)/dist_compat/$APP_NAME"
echo ""
echo "  Para distribuir, solo copiá ese archivo y en la PC destino:"
echo "    chmod +x $APP_NAME"
echo "    ./$APP_NAME"
echo ""
echo "  Compatible con: Ubuntu 20.04+, Debian 11+, Fedora 33+,"
echo "  Linux Mint 20+, Pop!_OS 20.04+ y cualquier distro con GLIBC >= 2.31"
