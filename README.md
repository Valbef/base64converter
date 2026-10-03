Base64Converter

Herramienta sencilla de terminal escrita en Python para convertir archivos a Base64 y recuperar archivos originales a partir de texto Base64.

Funciona en:

Windows

Linux

Termux / Android

No utiliza interfaz gráfica ni librerías externas.

Características

Convertir cualquier archivo a Base64.

Mostrar el Base64 directamente en la terminal.

Guardar el Base64 en un archivo .txt.

Recuperar un archivo desde un .txt que contenga Base64.

Introducir Base64 directamente desde la terminal.

Detectar automáticamente el formato del archivo recuperado cuando sea posible.

Si el formato no puede detectarse, solicitar la extensión manualmente.

No se almacenan metadatos del archivo original en el Base64.

Procesamiento por bloques para archivos Base64 grandes.

Evita sobrescribir archivos accidentalmente.

Requisitos

El único requisito es:

Python 3.8 o superior


No es necesario instalar paquetes mediante pip.

El programa utiliza únicamente módulos incluidos en la biblioteca estándar de Python.


==========================

Instalación:

==========================

Windows

Descarga o copia el proyecto en una carpeta.


Abre una terminal en esa carpeta y ejecuta:

python main.py

-------------------------------------------------------

Linux

descarga o copia el proyecto en una carpeta:

git clone https://github.com/Valbef/base64converter.git


ejecuta:
cd base64converter

python3 base64converter.py


También puedes utilizar:

python base64converter.py

--------------------------------------------------------------------------

Termux

Instala Python:

pkg update
pkg install python


Descargar:

git clone https://github.com/Valbef/base64converter.git

Después, entra en la carpeta del proyecto:

cd base64converter


Y ejecuta:

python3 base64converter.py


Si quieres acceder a los archivos del almacenamiento interno de Android desde Termux, puedes ejecutar:

termux-setup-storage


Después tendrás disponible el almacenamiento compartido normalmente mediante:

~/storage/shared/

podrás introducir una ruta como:

/storage/emulated/0/Download/archivo.pdf

Uso

Al ejecutar el programa aparecerá el menú principal:

                BASE64CONVERTER

Conversor de archivos a/desde Base64.

1. Archivo → Base64
   
2. Base64 → Archivo
   
3. Salir


Selecciona:

"1"

y pulsa Enter


El programa solicitará la ruta del archivo:

Introduce la ruta del archivo: /ruta/al/archivo.pdf


Después podrás elegir:

1. Ver el Base64 en la terminal

2. Guardar directamente en un archivo .txt


Si eliges guardar, el archivo .txt se crea en el mismo directorio que el archivo original.

Por ejemplo:

archivo.pdf

archivo_base64.txt


Si introduces:

archivo_base64


el programa añadirá automáticamente:

.txt

2. Base64 → Archivo

Selecciona:

2


El programa permite utilizar dos métodos:

1. En un archivo .txt
   
2. Introducir el Base64 directamente

Desde un archivo .txt

Introduce la ruta:

Introduce la ruta del archivo .txt con Base64:


El programa decodificará el contenido e intentará detectar automáticamente el formato.

Por ejemplo:

Formato detectado: PNG
Extensión: .png


Después solamente tendrás que introducir el nombre:

Introduce el nombre del archivo de salida: imagen_recuperada


El resultado será:

imagen_recuperada.png


No es necesario introducir la extensión cuando el formato se detecta automáticamente.

Formato desconocido

Si el programa no puede identificar el formato:

"No se ha podido identificar automáticamente el formato."

Introduce la extensión del archivo:


Por ejemplo:

pdf


Después:

Introduce el nombre del archivo de salida: archivo


El resultado será:

archivo.pdf


-----------------------

Formatos

El programa puede reconocer automáticamente numerosos formatos mediante sus firmas binarias.

Entre ellos:

PNG, JPEG, GIF, WEBP, BMP, TIFF, ICO, PSD, HEIC/HEIF, PDF, RTF, ZIP, DOCX, XLSX, PPTX, ODT, ODS, ODP,

EPUB, APK, JARRAR, 7Z, GZIP, BZIP2, XZ, MP3, WAV, FLAC, OGG, MIDI, AIFF, MP4, MOV, AVI, MKV, WebM, FLV, MPEG,

EXE, DLL, ELF, Java .class, WebAssembly, ISO, TrueType, OpenType, WOFF, WOFF2, SQLite, JSON, XML, HTML

La detección automática no puede identificar de forma fiable todos los formatos existentes.

Algunos archivos no contienen una firma que permita distinguirlos de otros archivos.

Cuando esto ocurre, el programa solicita manualmente la extensión.


----------------------------------------------------------------------

Base64 y metadatos

El programa utiliza una conversión Base64 estándar.

El Base64 generado contiene únicamente la representación de los bytes del archivo original.

No se añade:

Nombre del archivo.

Extensión.

Ruta original.

Fecha de creación.

Fecha de modificación.

Tamaño como metadato adicional.

Información del sistema.

Otros metadatos creados por el programa.

Por este motivo, si un formato no puede identificarse a partir de sus propios bytes, 

el programa no puede saber cuál era originalmente su extensión.

