#!/bin/sh
# Evitar warnings de módulos GTK2 en GTK3
unset GTK_MODULES
unset GTK2_MODULES
exec "$SNAP/bin/sistema-hue" "$@"
