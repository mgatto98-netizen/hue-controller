#!/bin/sh
# Suprimir warnings de módulos GTK al iniciar

# Suprimir warning "Not loading module 'atk-bridge'"
export NO_AT_BRIDGE=1
unset GTK_MODULES
unset GTK2_MODULES

# Eliminar rutas gtk-2.0 de GTK_PATH para evitar que GTK3 intente cargar módulos GTK2
if [ -n "$GTK_PATH" ]; then
    _new=""
    _ifs="$IFS"
    IFS=":"
    for _d in $GTK_PATH; do
        case "$_d" in
            *gtk-2.0*) ;;
            *) [ -n "$_d" ] && _new="${_new:+$_new:}$_d" ;;
        esac
    done
    IFS="$_ifs"
    export GTK_PATH="$_new"
fi

exec "$SNAP/bin/pupu" "$@"
