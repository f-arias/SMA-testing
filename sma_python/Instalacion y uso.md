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

**Para la versión 1.7.1 (Traducción Fiel):**
```bash
cd SMA_python_171
python main_171.py
```
El script `main_171.py` ejecutará el análisis en un directorio de ejemplo utilizando el pipeline completo y fiel al macro de Fiji.

### Uso como Biblioteca (v1.7.1)

Puede importar la funcionalidad de SMA en sus propios scripts de Python para un control más granular.

#### Ejemplo de Uso

A continuación, se muestra un ejemplo de cómo importar y utilizar la función `SMA`.

```python
from SMA_python_171.analysis_171 import SMA

# 1. (Opcional) Personalizar parámetros de análisis
# Se puede pasar un diccionario vacío para usar los valores por defecto
# o especificar solo los parámetros a cambiar.
analysis_params = {
    "Tsigma": 8,
    "Osigma": "5"
}

# 2. Definir rutas de entrada y salida
input_image = 'ruta/a/su/imagen.png'
output_dir = 'ruta/de/salida'

# 3. Ejecutar el análisis
# La función ahora sigue fielmente el pipeline del macro de Fiji.
results, mask = SMA(
    input_image_path=input_image,
    output_path=output_dir,
    analysis_params=analysis_params
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
