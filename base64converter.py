#!/usr/bin/env python3

import base64
import binascii
import os
import subprocess
import sys
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Tamaño de los bloques utilizados para archivos grandes.
# 1 MiB = 1.048.576 bytes
CHUNK_SIZE = 1024 * 1024


# ============================================================
# COLORES
# ============================================================

# Colores ANSI.
# Funcionan en Linux, Termux y versiones modernas de Windows.

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
GRAY = "\033[90m"
WHITE = "\033[97m"


# ============================================================
# UTILIDADES GENERALES
# ============================================================

def limpiar_pantalla():
    """Limpia la terminal."""

    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "cls"],
            check=False
        )
    else:
        subprocess.run(
            ["clear"],
            check=False
        )


def pausa():
    """Espera a que el usuario pulse ENTER."""

    input(
        f"\n{GRAY}Pulsa ENTER para continuar...{RESET}"
    )


# ============================================================
# UTILIDADES
# ============================================================

def pedir_ruta_archivo(mensaje: str) -> Path | None:
    """
    Solicita una ruta de archivo al usuario.

    Se aceptan rutas con o sin comillas.

    Introducir 0 permite volver al menú principal.
    """

    while True:

        ruta = input(
            f"{mensaje}\n"
            f"{GRAY}(Introduce 0 para volver al menú){RESET}\n"
            f"> "
        ).strip()

        # ----------------------------------------------------
        # VOLVER AL MENÚ
        # ----------------------------------------------------

        if ruta == "0":
            return None

        # ----------------------------------------------------
        # QUITAR COMILLAS DOBLES
        # ----------------------------------------------------

        if (
            len(ruta) >= 2
            and ruta[0] == '"'
            and ruta[-1] == '"'
        ):
            ruta = ruta[1:-1]

        # ----------------------------------------------------
        # QUITAR COMILLAS SIMPLES
        # ----------------------------------------------------

        if (
            len(ruta) >= 2
            and ruta[0] == "'"
            and ruta[-1] == "'"
        ):
            ruta = ruta[1:-1]

        # ----------------------------------------------------
        # COMPROBAR VACÍO
        # ----------------------------------------------------

        if not ruta:
            print(
                f"{RED}No has introducido ninguna ruta.{RESET}"
            )
            continue

        ruta = Path(ruta).expanduser()

        # ----------------------------------------------------
        # COMPROBAR EXISTENCIA
        # ----------------------------------------------------

        if not ruta.exists():
            print(
                f"{RED}El archivo o ruta no existe:{RESET}\n"
                f"{ruta}"
            )
            continue

        # ----------------------------------------------------
        # COMPROBAR QUE SEA ARCHIVO
        # ----------------------------------------------------

        if not ruta.is_file():
            print(
                f"{RED}La ruta indicada no corresponde "
                f"a un archivo.{RESET}"
            )
            continue

        return ruta


def pedir_si_no(mensaje: str) -> bool | None:
    """
    Pregunta algo cuya respuesta debe ser sí, no o 0.

    Devuelve:
        True  -> sí
        False -> no
        None  -> volver al menú
    """

    while True:

        respuesta = input(
            f"{mensaje}\n"
            f"{GRAY}[s/n] — 0 para volver al menú{RESET}: "
        ).strip().lower()

        if respuesta == "0":
            return None

        if respuesta in (
            "s",
            "si",
            "sí",
            "y",
            "yes"
        ):
            return True

        if respuesta in (
            "n",
            "no"
        ):
            return False

        print(
            f"{YELLOW}"
            f"Introduce 's' para sí, 'n' para no "
            f"o '0' para volver al menú."
            f"{RESET}"
        )


def pedir_nombre_txt() -> str | None:
    """
    Pide el nombre que tendrá el archivo Base64.

    Introducir 0 permite volver al menú principal.
    """

    while True:

        nombre = input(
            f"Introduce el nombre del archivo Base64:\n"
            f"{GRAY}(Introduce 0 para volver al menú){RESET}\n"
            f"> "
        ).strip()

        # ----------------------------------------------------
        # VOLVER AL MENÚ
        # ----------------------------------------------------

        if nombre == "0":
            return None

        # ----------------------------------------------------
        # QUITAR COMILLAS
        # ----------------------------------------------------

        if (
            len(nombre) >= 2
            and nombre[0] == '"'
            and nombre[-1] == '"'
        ):
            nombre = nombre[1:-1]

        # ----------------------------------------------------
        # COMPROBAR VACÍO
        # ----------------------------------------------------

        if not nombre:
            print(
                f"{RED}El nombre no puede estar vacío.{RESET}"
            )
            continue

        # ----------------------------------------------------
        # EVITAR RUTAS
        # ----------------------------------------------------

        if "/" in nombre or "\\" in nombre:
            print(
                f"{RED}"
                f"Introduce solamente el nombre del archivo, "
                f"no una ruta."
                f"{RESET}"
            )
            continue

        # ----------------------------------------------------
        # AÑADIR .TXT
        # ----------------------------------------------------

        if not nombre.lower().endswith(".txt"):
            nombre += ".txt"

        return nombre


def pedir_nombre_archivo(
    extension: str
) -> str | None:
    """
    Pide el nombre del archivo que se va a reconstruir.

    Introducir 0 permite volver al menú principal.
    """

    extension = extension.strip()

    # --------------------------------------------------------
    # COMPROBAR EXTENSIÓN
    # --------------------------------------------------------

    if not extension:
        raise ValueError(
            "La extensión no puede estar vacía."
        )

    # --------------------------------------------------------
    # AÑADIR PUNTO
    # --------------------------------------------------------

    if not extension.startswith("."):
        extension = "." + extension

    # --------------------------------------------------------
    # EVITAR RUTAS EN LA EXTENSIÓN
    # --------------------------------------------------------

    if "/" in extension or "\\" in extension:
        raise ValueError(
            "La extensión no puede contener rutas."
        )

    # --------------------------------------------------------
    # PEDIR NOMBRE
    # --------------------------------------------------------

    nombre = input(
        f"Nombre del archivo de salida "
        f"(sin necesidad de escribir {extension}):\n"
        f"{GRAY}(Introduce 0 para volver al menú){RESET}\n"
        f"> "
    ).strip()

    # --------------------------------------------------------
    # VOLVER AL MENÚ
    # --------------------------------------------------------

    if nombre == "0":
        return None

    # --------------------------------------------------------
    # QUITAR COMILLAS
    # --------------------------------------------------------

    if (
        len(nombre) >= 2
        and nombre[0] == '"'
        and nombre[-1] == '"'
    ):
        nombre = nombre[1:-1]

    # --------------------------------------------------------
    # COMPROBAR VACÍO
    # --------------------------------------------------------

    if not nombre:
        raise ValueError(
            "El nombre del archivo no puede estar vacío."
        )

    # --------------------------------------------------------
    # EVITAR RUTAS
    # --------------------------------------------------------

    if "/" in nombre or "\\" in nombre:
        raise ValueError(
            "Introduce solamente el nombre del archivo."
        )

    # --------------------------------------------------------
    # AÑADIR EXTENSIÓN
    # --------------------------------------------------------

    if not nombre.lower().endswith(
        extension.lower()
    ):
        nombre += extension

    return nombre


def confirmar_sobrescritura(ruta):
    """Pregunta antes de sobrescribir un archivo existente."""

    if ruta.exists():

        respuesta = pedir_si_no(
            f"{RED}"
            f"El archivo '{ruta}' ya existe."
            f"{RESET} "
            f"{YELLOW}"
            f"¿Quieres sobrescribirlo?"
            f"{RESET}"
        )

        return respuesta

    return True


def mostrar_tamano(tamano):
    """Convierte bytes a una unidad legible."""

    unidades = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
        "PB"
    ]

    valor = float(tamano)

    for unidad in unidades:

        if valor < 1024:
            return f"{valor:.2f} {unidad}"

        valor /= 1024

    return f"{valor:.2f} PB"


# ============================================================
# ARCHIVO → BASE64
# ============================================================

def convertir_archivo_a_base64(ruta):
    """
    Convierte un archivo a Base64.

    Devuelve una cadena Base64.

    Esta función se utiliza cuando el usuario quiere
    visualizar el resultado directamente en la terminal.
    """

    with open(
        ruta,
        "rb"
    ) as archivo:

        datos = archivo.read()

    return base64.b64encode(
        datos
    ).decode("ascii")


def guardar_archivo_como_base64(
    ruta_entrada,
    ruta_salida
):
    """
    Convierte un archivo a Base64 y lo guarda directamente
    en un archivo .txt.

    Se procesa por bloques para soportar archivos grandes.
    """

    tamaño_total = ruta_entrada.stat().st_size
    procesados = 0

    # CHUNK_SIZE debe ser múltiplo de 3 para que cada bloque
    # pueda convertirse independientemente a Base64.
    tamaño_bloque = (
        CHUNK_SIZE // 3
    ) * 3

    with open(
        ruta_entrada,
        "rb"
    ) as origen, open(
        ruta_salida,
        "w",
        encoding="ascii"
    ) as destino:

        while True:

            bloque = origen.read(
                tamaño_bloque
            )

            if not bloque:
                break

            resultado = base64.b64encode(
                bloque
            ).decode("ascii")

            destino.write(resultado)

            procesados += len(bloque)

            mostrar_progreso(
                procesados,
                tamaño_total
            )


def mostrar_progreso(
    actual,
    total
):
    """Muestra una barra de progreso."""

    if total <= 0:
        porcentaje = 100
    else:
        porcentaje = (
            actual / total * 100
        )

    porcentaje = min(
        porcentaje,
        100
    )

    ancho = 30

    completado = int(
        ancho * porcentaje / 100
    )

    barra = (
        "█" * completado
        + "░" * (
            ancho - completado
        )
    )

    print(
        f"\r[{barra}] "
        f"{porcentaje:6.2f}%",
        end="",
        flush=True
    )


def opcion_archivo_a_base64():
    """Gestiona todo el flujo Archivo → Base64."""

    limpiar_pantalla()

    print(f"{GREEN}")
    print("==============================================")
    print("             ARCHIVO → BASE64")
    print("==============================================")
    print(RESET)

    # --------------------------------------------------------
    # PEDIR ARCHIVO
    # --------------------------------------------------------

    ruta = pedir_ruta_archivo(
        "\nIntroduce la ruta del archivo: "
    )

    if ruta is None:
        return

    tamaño = ruta.stat().st_size

    print()
    print(
        f"{GRAY}Archivo:{RESET} {ruta}"
    )

    print(
        f"{GRAY}Tamaño:{RESET}  "
        f"{mostrar_tamano(tamaño)}"
    )

    # --------------------------------------------------------
    # OPCIONES
    # --------------------------------------------------------

    print()
    print("¿Qué quieres hacer?")
    print()
    print("1. Ver el Base64 en la terminal")
    print("2. Guardar directamente en un archivo .txt")
    print(
        f"{GRAY}0. Volver al menú principal{RESET}"
    )
    print()

    while True:

        opcion = input(
            "Selecciona una opción [1/2]: "
        ).strip()

        if opcion == "0":
            return

        if opcion in (
            "1",
            "2"
        ):
            break

        print(
            f"{RED}Opción no válida.{RESET}"
        )

    # ========================================================
    # MOSTRAR EN TERMINAL
    # ========================================================

    if opcion == "1":

        print()

        print(
            f"{BLUE}Generando Base64...{RESET}"
        )

        try:

            resultado = (
                convertir_archivo_a_base64(
                    ruta
                )
            )

        except MemoryError:

            print(
                f"\n{RED}"
                f"El archivo es demasiado grande "
                f"para mostrarlo completo en memoria."
                f"{RESET}"
            )

            pausa()
            return

        print()
        print()

        print(
            f"{GREEN}"
            f"========== BASE64 =========="
            f"{RESET}"
        )

        print()

        print(resultado)

        print()

        print(
            f"{GREEN}"
            f"============================"
            f"{RESET}"
        )

        print()

        # ----------------------------------------------------
        # PREGUNTAR SI QUIERE GUARDAR
        # ----------------------------------------------------

        respuesta = pedir_si_no(
            f"{YELLOW}"
            f"¿Quieres guardar este Base64 "
            f"en un archivo .txt?"
            f"{RESET}"
        )

        if respuesta is None:
            return

        if respuesta:

            nombre = pedir_nombre_txt()

            if nombre is None:
                return

            ruta_salida = (
                ruta.parent / nombre
            )

            if ruta_salida.exists():

                respuesta = (
                    confirmar_sobrescritura(
                        ruta_salida
                    )
                )

                if respuesta is None:
                    return

                if not respuesta:

                    print(
                        f"{RED}"
                        f"No se ha guardado el archivo."
                        f"{RESET}"
                    )

                    pausa()
                    return

            try:

                with open(
                    ruta_salida,
                    "w",
                    encoding="ascii"
                ) as archivo:

                    archivo.write(
                        resultado
                    )

                print(
                    f"\n{GREEN}"
                    f"✓ Archivo guardado correctamente:"
                    f"{RESET}"
                )

                print(ruta_salida)

            except Exception as error:

                print(
                    f"\n{RED}"
                    f"Error al guardar:"
                    f"{RESET} {error}"
                )

    # ========================================================
    # GUARDAR DIRECTAMENTE
    # ========================================================

    elif opcion == "2":

        print()

        nombre = pedir_nombre_txt()

        if nombre is None:
            return

        ruta_salida = (
            ruta.parent / nombre
        )

        if ruta_salida.exists():

            respuesta = (
                confirmar_sobrescritura(
                    ruta_salida
                )
            )

            if respuesta is None:
                return

            if not respuesta:

                print(
                    f"{YELLOW}"
                    f"Operación cancelada."
                    f"{RESET}"
                )

                pausa()
                return

        print()

        print(
            f"{BLUE}Convirtiendo...{RESET}"
        )

        try:

            guardar_archivo_como_base64(
                ruta,
                ruta_salida
            )

            print()
            print()

            print(
                f"{GREEN}"
                f"✓ Base64 guardado correctamente:"
                f"{RESET}"
            )

            print(ruta_salida)

        except Exception as error:

            print()
            print(
                f"{RED}"
                f"Error:"
                f"{RESET} {error}"
            )

    pausa()


# ============================================================
# BASE64 → ARCHIVO
# ============================================================

def limpiar_base64(texto):
    """
    Elimina espacios, saltos de línea y tabuladores.

    Esto permite trabajar con Base64 copiado desde:
        - archivos .txt
        - terminales
        - mensajes
        - textos formateados
    """

    return "".join(
        texto.split()
    )


def validar_base64(texto):
    """Comprueba que el contenido sea Base64 válido."""

    if not texto:

        raise ValueError(
            "El contenido Base64 está vacío."
        )

    try:

        base64.b64decode(
            texto,
            validate=True
        )

    except (
        binascii.Error,
        ValueError
    ):

        raise ValueError(
            "El texto introducido "
            "no es un Base64 válido."
        )


def pedir_datos_base64_desde_txt() -> str | None:
    """
    Solicita la ruta de un archivo .txt y devuelve
    su contenido Base64.

    Introducir 0 permite volver al menú.
    """

    ruta = pedir_ruta_archivo(
        "\nIntroduce la ruta del archivo .txt "
        "con Base64: "
    )

    if ruta is None:
        return None

    try:

        with open(
            ruta,
            "r",
            encoding="ascii"
        ) as archivo:

            contenido = archivo.read()

    except UnicodeDecodeError:

        raise ValueError(
            "El archivo no parece ser un archivo "
            "Base64 de texto válido."
        )

    return limpiar_base64(
        contenido
    )


def pedir_datos_base64_manual() -> str | None:
    """
    Permite introducir Base64 directamente.

    Se pueden pegar varias líneas.

    Una línea vacía finaliza la entrada.

    Introducir 0 como primera línea permite
    volver al menú.
    """

    print()

    print(
        f"{CYAN}"
        f"Introduce el Base64."
        f"{RESET}"
    )

    print(
        f"{GRAY}"
        f"Puedes pegarlo en una o varias líneas."
        f"{RESET}"
    )

    print(
        f"{GRAY}"
        f"Cuando termines, pulsa ENTER "
        f"en una línea vacía."
        f"{RESET}"
    )

    print(
        f"{GRAY}"
        f"Introduce 0 para volver al menú."
        f"{RESET}"
    )

    print()

    lineas = []

    while True:

        try:

            linea = input()

        except EOFError:

            break

        # ----------------------------------------------------
        # LÍNEA VACÍA = TERMINAR
        # ----------------------------------------------------

        if linea == "":
            break

        # ----------------------------------------------------
        # 0 COMO PRIMERA LÍNEA = VOLVER
        # ----------------------------------------------------

        if (
            not lineas
            and linea.strip() == "0"
        ):
            return None

        lineas.append(linea)

    contenido = "".join(
        lineas
    )

    return limpiar_base64(
        contenido
    )


def decodificar_base64_en_memoria(
    contenido,
    ruta_salida
):
    """
    Decodifica Base64 y escribe los bytes resultantes
    en el archivo de salida.
    """

    try:

        datos = base64.b64decode(
            contenido,
            validate=True
        )

    except (
        binascii.Error,
        ValueError
    ):

        raise ValueError(
            "El contenido introducido "
            "no es Base64 válido."
        )

    with open(
        ruta_salida,
        "wb"
    ) as archivo:

        archivo.write(datos)


def decodificar_txt_base64(
    ruta_entrada,
    ruta_salida
):
    """
    Decodifica un archivo Base64 directamente por bloques.

    De esta forma podemos trabajar con archivos Base64
    muy grandes sin cargarlos enteros en memoria.
    """

    pendiente = b""

    tamaño_total = (
        ruta_entrada.stat().st_size
    )

    procesados = 0

    with open(
        ruta_entrada,
        "rb"
    ) as origen, open(
        ruta_salida,
        "wb"
    ) as destino:

        while True:

            bloque = origen.read(
                CHUNK_SIZE
            )

            if not bloque:
                break

            procesados += len(
                bloque
            )

            # ------------------------------------------------
            # ELIMINAR ESPACIOS Y SALTOS
            # ------------------------------------------------

            bloque = b"".join(
                bloque.split()
            )

            if not bloque:

                mostrar_progreso(
                    procesados,
                    tamaño_total
                )

                continue

            bloque = (
                pendiente + bloque
            )

            # ------------------------------------------------
            # BASE64 FUNCIONA EN GRUPOS DE 4
            # ------------------------------------------------

            cantidad = (
                len(bloque) // 4
            ) * 4

            parte = (
                bloque[:cantidad]
            )

            pendiente = (
                bloque[cantidad:]
            )

            if parte:

                try:

                    datos = (
                        base64.b64decode(
                            parte,
                            validate=True
                        )
                    )

                except (
                    binascii.Error,
                    ValueError
                ):

                    raise ValueError(
                        "El archivo contiene "
                        "Base64 inválido."
                    )

                destino.write(
                    datos
                )

            mostrar_progreso(
                procesados,
                tamaño_total
            )

        # ----------------------------------------------------
        # PROCESAR ÚLTIMO FRAGMENTO
        # ----------------------------------------------------

        if pendiente:

            try:

                datos = (
                    base64.b64decode(
                        pendiente,
                        validate=True
                    )
                )

            except (
                binascii.Error,
                ValueError
            ):

                raise ValueError(
                    "El Base64 está incompleto "
                    "o es inválido."
                )

            destino.write(
                datos
            )


def opcion_base64_a_archivo():
    """Gestiona todo el flujo Base64 → archivo."""

    limpiar_pantalla()

    print(f"{GREEN}")
    print("==============================================")
    print("             BASE64 → ARCHIVO")
    print("==============================================")
    print(RESET)

    # --------------------------------------------------------
    # ORIGEN DEL BASE64
    # --------------------------------------------------------

    print("¿Dónde está el Base64?")
    print()
    print("1. En un archivo .txt")
    print("2. Quiero introducirlo directamente")
    print(
        f"{GRAY}0. Volver al menú principal{RESET}"
    )
    print()

    while True:

        opcion = input(
            "Selecciona una opción [1/2]: "
        ).strip()

        if opcion == "0":
            return

        if opcion in (
            "1",
            "2"
        ):
            break

        print(
            f"{RED}Opción no válida.{RESET}"
        )

    # ========================================================
    # BASE64 DESDE TXT
    # ========================================================

    if opcion == "1":

        try:

            ruta_base64 = (
                pedir_ruta_archivo(
                    "\nIntroduce la ruta "
                    "del archivo .txt: "
                )
            )

            if ruta_base64 is None:
                return

            # ------------------------------------------------
            # EXTENSIÓN
            # ------------------------------------------------

            extension = input(
                "\n¿Qué extensión tendrá "
                "el archivo recuperado? "
                "(ejemplo: pdf, png, zip):\n"
                f"{GRAY}"
                "(Introduce 0 para volver al menú)"
                f"{RESET}\n"
                "> "
            ).strip()

            if extension == "0":
                return

            if not extension:

                raise ValueError(
                    "La extensión no puede estar vacía."
                )

            # ------------------------------------------------
            # NOMBRE
            # ------------------------------------------------

            nombre = pedir_nombre_archivo(
                extension
            )

            if nombre is None:
                return

            ruta_salida = (
                ruta_base64.parent / nombre
            )

            # ------------------------------------------------
            # SOBRESCRITURA
            # ------------------------------------------------

            if ruta_salida.exists():

                respuesta = (
                    confirmar_sobrescritura(
                        ruta_salida
                    )
                )

                if respuesta is None:
                    return

                if not respuesta:

                    print(
                        f"{YELLOW}"
                        f"Operación cancelada."
                        f"{RESET}"
                    )

                    pausa()
                    return

            # ------------------------------------------------
            # DECODIFICAR
            # ------------------------------------------------

            print()

            print(
                f"{BLUE}"
                f"Decodificando..."
                f"{RESET}"
            )

            decodificar_txt_base64(
                ruta_base64,
                ruta_salida
            )

            print()
            print()

            print(
                f"{GREEN}"
                f"✓ Archivo recuperado correctamente:"
                f"{RESET}"
            )

            print(ruta_salida)

        except Exception as error:

            print()
            print(
                f"{RED}"
                f"Error:"
                f"{RESET} {error}"
            )

    # ========================================================
    # BASE64 INTRODUCIDO MANUALMENTE
    # ========================================================

    elif opcion == "2":

        try:

            # ------------------------------------------------
            # OBTENER BASE64
            # ------------------------------------------------

            contenido = (
                pedir_datos_base64_manual()
            )

            if contenido is None:
                return

            # ------------------------------------------------
            # VALIDAR BASE64
            # ------------------------------------------------

            validar_base64(
                contenido
            )

            print()

            # ------------------------------------------------
            # EXTENSIÓN
            # ------------------------------------------------

            extension = input(
                "¿Qué extensión tendrá "
                "el archivo recuperado? "
                "(ejemplo: pdf, png, zip):\n"
                f"{GRAY}"
                "(Introduce 0 para volver al menú)"
                f"{RESET}\n"
                "> "
            ).strip()

            if extension == "0":
                return

            if not extension:

                raise ValueError(
                    "La extensión no puede estar vacía."
                )

            # ------------------------------------------------
            # NOMBRE
            # ------------------------------------------------

            nombre = pedir_nombre_archivo(
                extension
            )

            if nombre is None:
                return

            # ------------------------------------------------
            # DIRECTORIO DE SALIDA
            # ------------------------------------------------

            ruta_salida = (
                Path.cwd() / nombre
            )

            # ------------------------------------------------
            # SOBRESCRITURA
            # ------------------------------------------------

            if ruta_salida.exists():

                respuesta = (
                    confirmar_sobrescritura(
                        ruta_salida
                    )
                )

                if respuesta is None:
                    return

                if not respuesta:

                    print(
                        f"{YELLOW}"
                        f"Operación cancelada."
                        f"{RESET}"
                    )

                    pausa()
                    return

            # ------------------------------------------------
            # DECODIFICAR
            # ------------------------------------------------

            print()

            print(
                f"{BLUE}"
                f"Decodificando..."
                f"{RESET}"
            )

            decodificar_base64_en_memoria(
                contenido,
                ruta_salida
            )

            print()

            print(
                f"{GREEN}"
                f"✓ Archivo recuperado correctamente:"
                f"{RESET}"
            )

            print(ruta_salida)

        except Exception as error:

            print()
            print(
                f"{RED}"
                f"Error:"
                f"{RESET} {error}"
            )

    pausa()


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def mostrar_menu():
    """Muestra el menú principal."""

    limpiar_pantalla()

    print(f"{WHITE}")
    print("==============================================")
    print("                BASE64CONVERTER")
    print("==============================================")
    print(RESET)

    print(
        "Herramienta para convertir cualquier archivo "
        "a/desde Base64."
    )

    print()

    print(
        f"{BOLD}1.{RESET} Archivo → Base64"
    )

    print(
        f"{BOLD}2.{RESET} Base64 → Archivo"
    )

    print(
        f"{BOLD}3.{RESET} Salir"
    )

    print()


def main():
    """Función principal del programa."""

    while True:

        mostrar_menu()

        opcion = input(
            "Selecciona una opción: "
        ).strip()

        # ----------------------------------------------------
        # ARCHIVO → BASE64
        # ----------------------------------------------------

        if opcion == "1":

            opcion_archivo_a_base64()

        # ----------------------------------------------------
        # BASE64 → ARCHIVO
        # ----------------------------------------------------

        elif opcion == "2":

            opcion_base64_a_archivo()

        # ----------------------------------------------------
        # SALIR
        # ----------------------------------------------------

        elif opcion == "3":

            limpiar_pantalla()

            print(
                f"{GREEN}"
                f"Hasta luego."
                f"{RESET}"
            )

            break

        # ----------------------------------------------------
        # OPCIÓN NO VÁLIDA
        # ----------------------------------------------------

        else:

            print()

            print(
                f"{RED}"
                f"Opción no válida."
                f"{RESET}"
            )

            pausa()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print()

        print(
            f"{YELLOW}"
            f"Programa cancelado por el usuario."
            f"{RESET}"
        )

        sys.exit(0)
