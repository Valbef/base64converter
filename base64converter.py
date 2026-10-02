#!/usr/bin/env python3

import base64
import binascii
import os
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

# Intentamos utilizar colores ANSI.
# Funcionan en Linux, Termux y versiones modernas de Windows.

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
GRAY = "\033[90m"


def limpiar_pantalla():
    """Limpia la terminal."""

    os.system("cls" if os.name == "nt" else "clear")


def pausa():
    """Espera a que el usuario pulse ENTER."""

    input(f"\n{GRAY}Pulsa ENTER para continuar...{RESET}")


# ============================================================
# UTILIDADES
# ============================================================

def pedir_ruta_archivo(mensaje):
    """
    Solicita una ruta de archivo al usuario.

    Se aceptan rutas con o sin comillas.
    """

    while True:

        ruta = input(mensaje).strip()

        # Permitir que el usuario pegue:
        # "C:\Users\Usuario\archivo.pdf"
        if (
            len(ruta) >= 2
            and ruta[0] == '"'
            and ruta[-1] == '"'
        ):
            ruta = ruta[1:-1]

        # También aceptamos comillas simples.
        if (
            len(ruta) >= 2
            and ruta[0] == "'"
            and ruta[-1] == "'"
        ):
            ruta = ruta[1:-1]

        if not ruta:
            print(f"{RED}No has introducido ninguna ruta.{RESET}")
            continue

        ruta = Path(ruta).expanduser()

        if not ruta.exists():
            print(
                f"{RED}El archivo o ruta no existe:{RESET}\n"
                f"{ruta}"
            )
            continue

        if not ruta.is_file():
            print(
                f"{RED}La ruta indicada no corresponde a un archivo.{RESET}"
            )
            continue

        return ruta


def pedir_si_no(mensaje):
    """Pregunta algo cuya respuesta debe ser sí o no."""

    while True:

        respuesta = input(
            f"{mensaje} {GRAY}[s/n]{RESET}: "
        ).strip().lower()

        if respuesta in ("s", "si", "sí", "y", "yes"):
            return True

        if respuesta in ("n", "no"):
            return False

        print(
            f"{YELLOW}Introduce 's' para sí o 'n' para no.{RESET}"
        )


def pedir_nombre_txt():
    """
    Pide el nombre que tendrá el archivo Base64.

    El usuario puede escribir:
        archivo
        archivo.txt

    Siempre terminaremos con .txt
    """

    while True:

        nombre = input(
            "Introduce el nombre del archivo Base64: "
        ).strip()

        # Quitar comillas si el usuario las pega.
        if (
            len(nombre) >= 2
            and nombre[0] == '"'
            and nombre[-1] == '"'
        ):
            nombre = nombre[1:-1]

        if not nombre:
            print(
                f"{RED}El nombre no puede estar vacío.{RESET}"
            )
            continue

        # Evitar rutas.
        if "/" in nombre or "\\" in nombre:
            print(
                f"{RED}Introduce solamente el nombre del archivo, "
                f"no una ruta.{RESET}"
            )
            continue

        if not nombre.lower().endswith(".txt"):
            nombre += ".txt"

        return nombre


def pedir_nombre_archivo(extension):
    """
    Pide el nombre del archivo que se va a reconstruir.

    Ejemplo:
        extensión: pdf
        nombre: documento

    Resultado:
        documento.pdf
    """

    extension = extension.strip()

    if not extension:
        raise ValueError("La extensión no puede estar vacía.")

    if not extension.startswith("."):
        extension = "." + extension

    # La extensión solo puede contener texto de nombre.
    if "/" in extension or "\\" in extension:
        raise ValueError(
            "La extensión no puede contener rutas."
        )

    nombre = input(
        f"Nombre del archivo de salida "
        f"(sin necesidad de escribir {extension}): "
    ).strip()

    if (
        len(nombre) >= 2
        and nombre[0] == '"'
        and nombre[-1] == '"'
    ):
        nombre = nombre[1:-1]

    if not nombre:
        raise ValueError(
            "El nombre del archivo no puede estar vacío."
        )

    if "/" in nombre or "\\" in nombre:
        raise ValueError(
            "Introduce solamente el nombre del archivo."
        )

    # Si ya tiene la extensión, no la duplicamos.
    if not nombre.lower().endswith(extension.lower()):
        nombre += extension

    return nombre


def confirmar_sobrescritura(ruta):
    """Pregunta antes de sobrescribir un archivo existente."""

    if ruta.exists():
        return pedir_si_no(
            f"{YELLOW}El archivo '{ruta}' ya existe. "
            f"¿Quieres sobrescribirlo?{RESET}"
        )

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

    with open(ruta, "rb") as archivo:

        datos = archivo.read()

    return base64.b64encode(datos).decode("ascii")


def guardar_archivo_como_base64(ruta_entrada, ruta_salida):
    """
    Convierte un archivo a Base64 y lo guarda directamente
    en un archivo .txt.

    Se procesa por bloques para soportar archivos grandes.
    """

    tamaño_total = ruta_entrada.stat().st_size
    procesados = 0

    # CHUNK_SIZE debe ser múltiplo de 3 para que cada bloque
    # pueda convertirse independientemente a Base64.
    tamaño_bloque = (CHUNK_SIZE // 3) * 3

    with open(ruta_entrada, "rb") as origen, \
         open(ruta_salida, "w", encoding="ascii") as destino:

        while True:

            bloque = origen.read(tamaño_bloque)

            if not bloque:
                break

            resultado = base64.b64encode(bloque).decode("ascii")

            destino.write(resultado)

            procesados += len(bloque)

            mostrar_progreso(
                procesados,
                tamaño_total
            )


def mostrar_progreso(actual, total):
    """Muestra una barra de progreso."""

    if total <= 0:
        porcentaje = 100
    else:
        porcentaje = actual / total * 100

    porcentaje = min(porcentaje, 100)

    ancho = 30

    completado = int(
        ancho * porcentaje / 100
    )

    barra = (
        "█" * completado
        + "░" * (ancho - completado)
    )

    print(
        f"\r[{barra}] {porcentaje:6.2f}%",
        end="",
        flush=True
    )


def opcion_archivo_a_base64():
    """Gestiona todo el flujo Archivo → Base64."""

    limpiar_pantalla()

    print(f"{CYAN}{BOLD}")
    print("==============================================")
    print("             ARCHIVO → BASE64")
    print("==============================================")
    print(RESET)

    ruta = pedir_ruta_archivo(
        "\nIntroduce la ruta del archivo: "
    )

    tamaño = ruta.stat().st_size

    print()
    print(
        f"{GRAY}Archivo:{RESET} {ruta}"
    )
    print(
        f"{GRAY}Tamaño:{RESET}  {mostrar_tamano(tamaño)}"
    )

    print()
    print("¿Qué quieres hacer?")
    print()
    print("1. Ver el Base64 en la terminal")
    print("2. Guardar directamente en un archivo .txt")
    print()

    while True:

        opcion = input(
            "Selecciona una opción [1/2]: "
        ).strip()

        if opcion in ("1", "2"):
            break

        print(
            f"{YELLOW}Opción no válida.{RESET}"
        )

    # --------------------------------------------------------
    # MOSTRAR EN TERMINAL
    # --------------------------------------------------------

    if opcion == "1":

        print()
        print(
            f"{BLUE}Generando Base64...{RESET}"
        )

        try:

            resultado = convertir_archivo_a_base64(
                ruta
            )

        except MemoryError:

            print(
                f"\n{RED}El archivo es demasiado grande "
                f"para mostrarlo completo en memoria.{RESET}"
            )

            pausa()
            return

        print()
        print()
        print(
            f"{CYAN}========== BASE64 =========={RESET}"
        )
        print()

        print(resultado)

        print()
        print(
            f"{CYAN}============================{RESET}"
        )

        # Después de mostrarlo, preguntamos si quiere guardarlo.
        print()

        if pedir_si_no(
            "¿Quieres guardar este Base64 en un archivo .txt?"
        ):

            nombre = pedir_nombre_txt()

            ruta_salida = ruta.parent / nombre

            if ruta_salida.exists():

                if not confirmar_sobrescritura(
                    ruta_salida
                ):
                    print(
                        f"{YELLOW}No se ha guardado el archivo.{RESET}"
                    )
                    pausa()
                    return

            try:

                with open(
                    ruta_salida,
                    "w",
                    encoding="ascii"
                ) as archivo:

                    archivo.write(resultado)

                print(
                    f"\n{GREEN}✓ Archivo guardado correctamente:{RESET}"
                )
                print(ruta_salida)

            except Exception as error:

                print(
                    f"\n{RED}Error al guardar:{RESET} "
                    f"{error}"
                )

    # --------------------------------------------------------
    # GUARDAR DIRECTAMENTE
    # --------------------------------------------------------

    elif opcion == "2":

        print()

        nombre = pedir_nombre_txt()

        ruta_salida = ruta.parent / nombre

        if ruta_salida.exists():

            if not confirmar_sobrescritura(
                ruta_salida
            ):
                print(
                    f"{YELLOW}Operación cancelada.{RESET}"
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
                f"{GREEN}✓ Base64 guardado correctamente:{RESET}"
            )
            print(ruta_salida)

        except Exception as error:

            print()
            print(
                f"{RED}Error:{RESET} {error}"
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

    return "".join(texto.split())


def validar_base64(texto):
    """
    Comprueba que el contenido sea Base64 válido.
    """

    if not texto:
        raise ValueError(
            "El contenido Base64 está vacío."
        )

    try:

        base64.b64decode(
            texto,
            validate=True
        )

    except (binascii.Error, ValueError):

        raise ValueError(
            "El texto introducido no es un Base64 válido."
        )


def pedir_datos_base64_desde_txt():
    """
    Solicita la ruta de un archivo .txt y devuelve
    su contenido Base64.
    """

    ruta = pedir_ruta_archivo(
        "\nIntroduce la ruta del archivo .txt con Base64: "
    )

    try:

        with open(
            ruta,
            "r",
            encoding="ascii"
        ) as archivo:

            contenido = archivo.read()

    except UnicodeDecodeError:

        raise ValueError(
            "El archivo no parece ser un archivo Base64 "
            "de texto válido."
        )

    return limpiar_base64(contenido)


def pedir_datos_base64_manual():
    """
    Permite introducir Base64 directamente.

    Se pueden pegar varias líneas.
    Una línea vacía finaliza la entrada.
    """

    print()
    print(
        f"{CYAN}Introduce el Base64.{RESET}"
    )
    print(
        f"{GRAY}Puedes pegarlo en una o varias líneas.{RESET}"
    )
    print(
        f"{GRAY}Cuando termines, pulsa ENTER en una línea vacía.{RESET}"
    )
    print()

    lineas = []

    while True:

        try:
            linea = input()

        except EOFError:
            break

        if linea == "":
            break

        lineas.append(linea)

    contenido = "".join(lineas)

    return limpiar_base64(contenido)


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

    except (binascii.Error, ValueError):

        raise ValueError(
            "El contenido introducido no es Base64 válido."
        )

    with open(ruta_salida, "wb") as archivo:

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

    tamaño_total = ruta_entrada.stat().st_size
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

            procesados += len(bloque)

            # Eliminar espacios y saltos de línea.
            bloque = b"".join(
                bloque.split()
            )

            if not bloque:
                mostrar_progreso(
                    procesados,
                    tamaño_total
                )
                continue

            bloque = pendiente + bloque

            # Base64 funciona en grupos de 4 caracteres.
            cantidad = (
                len(bloque) // 4
            ) * 4

            parte = bloque[:cantidad]

            pendiente = bloque[cantidad:]

            if parte:

                try:

                    datos = base64.b64decode(
                        parte,
                        validate=True
                    )

                except (binascii.Error, ValueError):

                    raise ValueError(
                        "El archivo contiene Base64 inválido."
                    )

                destino.write(datos)

            mostrar_progreso(
                procesados,
                tamaño_total
            )

        # Procesar el último fragmento.
        if pendiente:

            try:

                datos = base64.b64decode(
                    pendiente,
                    validate=True
                )

            except (binascii.Error, ValueError):

                raise ValueError(
                    "El Base64 está incompleto o es inválido."
                )

            destino.write(datos)


def opcion_base64_a_archivo():
    """Gestiona todo el flujo Base64 → archivo."""

    limpiar_pantalla()

    print(f"{CYAN}{BOLD}")
    print("==============================================")
    print("             BASE64 → ARCHIVO")
    print("==============================================")
    print(RESET)

    print("¿Dónde está el Base64?")
    print()
    print("1. En un archivo .txt")
    print("2. Quiero introducirlo directamente")
    print()

    while True:

        opcion = input(
            "Selecciona una opción [1/2]: "
        ).strip()

        if opcion in ("1", "2"):
            break

        print(
            f"{YELLOW}Opción no válida.{RESET}"
        )

    # --------------------------------------------------------
    # BASE64 DESDE TXT
    # --------------------------------------------------------

    if opcion == "1":

        try:

            ruta_base64 = pedir_ruta_archivo(
                "\nIntroduce la ruta del archivo .txt: "
            )

            extension = input(
                "\n¿Qué extensión tendrá el archivo recuperado? "
                "(ejemplo: pdf, png, zip): "
            ).strip()

            if not extension:
                raise ValueError(
                    "La extensión no puede estar vacía."
                )

            nombre = pedir_nombre_archivo(
                extension
            )

            ruta_salida = ruta_base64.parent / nombre

            if ruta_salida.exists():

                if not confirmar_sobrescritura(
                    ruta_salida
                ):
                    print(
                        f"{YELLOW}Operación cancelada.{RESET}"
                    )
                    pausa()
                    return

            print()
            print(
                f"{BLUE}Decodificando...{RESET}"
            )

            decodificar_txt_base64(
                ruta_base64,
                ruta_salida
            )

            print()
            print()
            print(
                f"{GREEN}✓ Archivo recuperado correctamente:{RESET}"
            )
            print(ruta_salida)

        except Exception as error:

            print()
            print(
                f"{RED}Error:{RESET} {error}"
            )

    # --------------------------------------------------------
    # BASE64 INTRODUCIDO MANUALMENTE
    # --------------------------------------------------------

    elif opcion == "2":

        try:

            contenido = pedir_datos_base64_manual()

            validar_base64(contenido)

            print()

            extension = input(
                "¿Qué extensión tendrá el archivo recuperado? "
                "(ejemplo: pdf, png, zip): "
            ).strip()

            if not extension:
                raise ValueError(
                    "La extensión no puede estar vacía."
                )

            nombre = pedir_nombre_archivo(
                extension
            )

            # Como no tenemos un directorio de entrada,
            # guardamos en el directorio actual.
            ruta_salida = Path.cwd() / nombre

            if ruta_salida.exists():

                if not confirmar_sobrescritura(
                    ruta_salida
                ):
                    print(
                        f"{YELLOW}Operación cancelada.{RESET}"
                    )
                    pausa()
                    return

            print()
            print(
                f"{BLUE}Decodificando...{RESET}"
            )

            decodificar_base64_en_memoria(
                contenido,
                ruta_salida
            )

            print()
            print(
                f"{GREEN}✓ Archivo recuperado correctamente:{RESET}"
            )
            print(ruta_salida)

        except Exception as error:

            print()
            print(
                f"{RED}Error:{RESET} {error}"
            )

    pausa()


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def mostrar_menu():

    limpiar_pantalla()

    print(f"{CYAN}{BOLD}")
    print("==============================================")
    print("                BASE64CONVERTER")
    print("==============================================")
    print(RESET)

    print(
        "Herramienta para convertir cualquier archivo "
        "a/desde Base64."
    )

    print()
    print(f"{BOLD}1.{RESET} Archivo → Base64")
    print(f"{BOLD}2.{RESET} Base64 → Archivo")
    print(f"{BOLD}3.{RESET} Salir")
    print()


def main():

    while True:

        mostrar_menu()

        opcion = input(
            "Selecciona una opción: "
        ).strip()

        if opcion == "1":

            opcion_archivo_a_base64()

        elif opcion == "2":

            opcion_base64_a_archivo()

        elif opcion == "3":

            limpiar_pantalla()

            print(
                f"{GREEN}Hasta luego.{RESET}"
            )

            break

        else:

            print()
            print(
                f"{YELLOW}Opción no válida.{RESET}"
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
            f"{YELLOW}Programa cancelado por el usuario.{RESET}"
        )

        sys.exit(0)
