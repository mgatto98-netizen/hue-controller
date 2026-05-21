#!/bin/bash
echo "========================================="
echo "  Configurando entorno para Briefcase"
echo "========================================="
echo ""

# Configurar PKG_CONFIG_PATH
export PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH
export PKG_CONFIG_PATH=/usr/share/pkgconfig:$PKG_CONFIG_PATH

# Configurar otras variables
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH

# Variables para meson
export PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH

echo "✅ Variables configuradas:"
echo "   PKG_CONFIG_PATH: $PKG_CONFIG_PATH"
echo ""

echo "=== Verificación de paquetes ==="
echo -n "gobject-introspection-1.0: "
pkg-config --modversion gobject-introspection-1.0 2>/dev/null || echo "No encontrado"
echo -n "gobject-2.0: "
pkg-config --modversion gobject-2.0 2>/dev/null || echo "No encontrado"
echo -n "gtk+-3.0: "
pkg-config --modversion gtk+-3.0 2>/dev/null || echo "No encontrado"
echo -n "cairo: "
pkg-config --modversion cairo 2>/dev/null || echo "No encontrado"
echo ""

echo "=== Archivos .pc disponibles ==="
ls /usr/lib/x86_64-linux-gnu/pkgconfig/ | grep -E "(gobject|gtk|cairo)" | head -10
echo ""

echo "✅ Entorno configurado correctamente"
