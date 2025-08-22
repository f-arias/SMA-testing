# SMA - Análisis de Arquitectura Muscular Simple (Versión en Python)

Este proyecto es una conversión a Python del macro de ImageJ "Simple Muscle Architecture (SMA)" original, desarrollado por O. R. Seynnes y N. J. Cronin. El objetivo de esta versión es proporcionar una herramienta equivalente que pueda ser ejecutada en un entorno de Python estándar, sin necesidad de ImageJ/Fiji.

La referencia al trabajo original es:
*Seynnes, O. R., & Cronin, N. J. (2020). Simple Muscle Architecture Analysis (SMA): An ImageJ macro tool to automate measurements in B-mode ultrasound scans. PloS One, 15(2), e0229034.*

## Requisitos

Para ejecutar este programa, necesita tener Python 3 instalado, así como las siguientes bibliotecas:

- opencv-python-headless
- scikit-image
- numpy
- scipy
- matplotlib

Todos los requisitos se encuentran en el archivo `requirements.txt`.

## Instalación

1.  **Clonar el repositorio o descargar los archivos**.
2.  **Navegar al directorio `sma_python`** en su terminal.
3.  **(Recomendado) Crear un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```
4.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Versiones

Este proyecto contiene dos versiones de la herramienta, organizadas en subdirectorios:

-   **Versión 2.3.3 (`SMA_python_233/`):** La implementación más moderna y con más funcionalidades.
-   **Versión 1.7.1 (`SMA_python_171/`):** Una implementación basada en una versión anterior y más simple del macro.

## Uso

Cada versión se puede ejecutar de dos maneras: como un script principal que procesa un directorio de imágenes o como una biblioteca que puede importar en su propio código.

### Ejecución como Script

Para procesar rápidamente un directorio de imágenes, puede ejecutar el script `main` de cada versión.

**Para la versión 2.3.3:**
```bash
cd SMA_python_233
python main_233.py
```

**Para la versión 1.7.1:**
```bash
cd SMA_python_171
python main_171.py
```
El script `main_171.py` ha sido actualizado para servir como un ejemplo claro de cómo usar la función `SMA` y sus configuraciones.

### Uso como Biblioteca (v1.7.1)

Puede importar la funcionalidad de SMA en sus propios scripts de Python para un control más granular. Esto es especialmente útil si desea integrar el análisis en un flujo de trabajo más grande.

#### Funciones Principales

-   `SMA(input_image_path, output_path, analysis_params, general_config)`: La función principal que ejecuta el análisis en una sola imagen.
-   `get_default_sma_parameters()`: Devuelve un diccionario con los parámetros de análisis por defecto.
-   `get_default_general_config()`: Devuelve un diccionario con las configuraciones generales por defecto (como guardar archivos o mostrar mensajes).

#### Ejemplo de Uso

A continuación, se muestra un ejemplo de cómo importar y utilizar la función `SMA`.

```python
from SMA_python_171.analysis_171 import (
    SMA,
    get_default_sma_parameters,
    get_default_general_config
)

# 1. Cargar las configuraciones por defecto
analysis_params = get_default_sma_parameters()
general_config = get_default_general_config()

# El usuario puede inspeccionar los parámetros por defecto
print("Parámetros por defecto:", analysis_params)
# En una variable X, se le asigne el diccionario por defecto
X = analysis_params

# 2. (Opcional) Personalizar las configuraciones
analysis_params['Osigma'] = '5'  # Cambiar un parámetro de análisis
general_config['save_csv'] = False  # No guardar el archivo CSV

# 3. Definir rutas de entrada y salida
input_image = 'ruta/a/su/imagen.png'
output_dir = 'ruta/de/salida'

# 4. Ejecutar el análisis
results, mask = SMA(
    input_image_path=input_image,
    output_path=output_dir,
    analysis_params=analysis_params,
    general_config=general_config
)

if results:
    print("Análisis completado:")
    print(results)

```

## Salida del Programa

Ambas versiones generan un archivo de resultados en formato `.csv` con los parámetros calculados. Sin embargo, la imagen de salida es diferente.

### Salida v2.3.3
-   **Imágenes Procesadas:** Por cada imagen de entrada, se guarda una nueva imagen con el prefijo `processed_`. Esta imagen muestra la foto original con las **aponeurosis detectadas** y una representación del **fascículo promedio** superpuestas.
-   **Archivo de Resultados (`resultados.csv`):** Un único archivo CSV con los datos de todas las imágenes procesadas.

### Salida v1.7.1
-   **Máscara Binaria:** Por cada imagen de entrada, se guarda una nueva imagen con el prefijo `processed_mask_`. Esta imagen es una máscara en blanco y negro, donde las **aponeurosis detectadas se muestran en blanco** sobre un fondo negro.
-   **Archivo de Resultados (`resultados_171.csv`):** Un único archivo CSV con los datos de todas las imágenes procesadas por esta versión.
