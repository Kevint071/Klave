# Klave

Klave es una aplicación hecha con Flet para registrar canciones y clasificarlas según su tono, carácter y ritmo. Está pensada para llevar un repertorio simple, editable y fácil de filtrar desde una sola interfaz.

## Qué hace el proyecto

Con Klave puedes:

- Agregar canciones.
- Editar canciones existentes.
- Eliminar canciones.
- Asignar a cada canción un tono o nota musical.
- Asignar uno o varios caracteres a una canción.
- Clasificar canciones por ritmo.
- Buscar por nombre.
- Filtrar por tono, carácter y ritmo.
- Personalizar la lista de caracteres disponibles.
- Guardar los datos localmente en un archivo JSON.

## Funcionalidades reales

Las funcionalidades implementadas actualmente en el proyecto son estas:

- Registro de canciones con título, tono, carácter y tempo.
- Soporte para múltiples caracteres por canción.
- Filtros por tono musical, incluyendo sostenido y menor cuando aplica.
- Filtros por carácter de la canción.
- Filtros por ritmo o tempo.
- Búsqueda por texto sobre el título.
- Pantalla de configuración para cambiar entre tema claro y oscuro.
- Pantalla para agregar o eliminar caracteres personalizados.
- Persistencia local de datos en `src/assets/user_data.json`.

## Tecnologías

- Python
- Flet

## Requisitos

- Python 3.10, 3.11 o 3.12

## Instalación

1. Crea el entorno virtual con `uv`:

    ```bash
    uv venv .venv
    ```

2. Actívalo según tu sistema operativo:

    ```bash
    # Linux / macOS
    source .venv/bin/activate

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

    # Windows CMD
    .venv\Scripts\activate.bat
    ```

3. Instala las dependencias:

    ```bash
    uv sync
    ```

## Ejecución

Para iniciar la aplicación se ejecuta con Flet:

```bash
flet run src/main.py
```

## Estructura básica

```text
src/
 main.py              Punto de entrada de la aplicación
 models/              Lógica y persistencia de datos
 views/               Pantallas principales
 components/          Componentes reutilizables de interfaz
 assets/user_data.json Datos guardados por la aplicación
```

## Datos y almacenamiento

Klave no usa nube ni sincronización remota. La información se guarda localmente en un archivo JSON dentro de los assets de la aplicación.

Esto incluye:

- Canciones registradas.
- Caracteres personalizados.
- Preferencia de tema.

## Estado actual

Este repositorio está orientado a una app local para organizar canciones por criterios musicales y prácticos de uso. No implementa listas de reproducción, catálogo en la nube ni búsqueda por artista o álbum, porque esos datos no forman parte del modelo actual.
