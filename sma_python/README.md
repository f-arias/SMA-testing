# SMA - Análisis de Arquitectura Muscular Simple (Versión en Python)

Este proyecto es una conversión a Python del macro de ImageJ "Simple Muscle Architecture (SMA)" original, desarrollado por O. R. Seynnes y N. J. Cronin. El objetivo de esta versión es proporcionar una herramienta equivalente que pueda ser ejecutada en un entorno de Python estándar, sin necesidad de ImageJ/Fiji.

La referencia al trabajo original es:
*Seynnes, O. R., & Cronin, N. J. (2020). Simple Muscle Architecture Analysis (SMA): An ImageJ macro tool to automate measurements in B-mode ultrasound scans. PloS One, 15(2), e0229034.*

## Filosofía del Proyecto y Flujo de Procesamiento

El módulo `SMA_python_171` busca ser una **transcripción lo más fiel posible** del flujo de trabajo de procesamiento de imágenes del macro original de Fiji (versión 1.7.1). El objetivo es replicar cada paso de filtrado en el mismo orden para validar la implementación en Python y comparar sus resultados con los del software original.

A continuación se detalla el diagrama de flujo exacto que sigue el script para detectar las aponeurosis:

1.  **Inicio: Recorte de la Imagen**
    *   El proceso comienza con el recorte del campo de visión para aislar la región del músculo. Esto puede ser **manual** o **automático**.

2.  **Paso 1: Pre-procesamiento y Reducción de Ruido**
    *   `Subtract Background`: Se elimina el fondo no uniforme para corregir variaciones de brillo.
    *   `Non-local Means Denoising`: Se aplica un filtro de reducción de ruido avanzado.
    *   `Bandpass Filter`: Se utiliza un filtro de paso de banda (implementado como Diferencia de Gaussianas) para eliminar ruido de alta y baja frecuencia.
    *   `Enhance Local Contrast (CLAHE)`: Se mejora el contraste localmente para realzar las estructuras de interés.

3.  **Paso 2: Realce Específico de Aponeurosis (Tubeness)**
    *   Se aplica un filtro **Sato** (equivalente a "Tubeness") para realzar específicamente las estructuras con forma de línea, como las aponeurosis.

4.  **Paso 3: Limpieza mediante Filtrado de Frecuencia (FFT)**
    *   Sobre la imagen ya procesada con el filtro de Tubeness, se aplica una **Transformada Rápida de Fourier (FFT)** para aislar las señales más fuertes y eliminar el ruido restante.

5.  **Paso 4: Detección de Bordes**
    *   Se utiliza el detector de bordes **Canny** sobre la imagen ultra-filtrada para obtener un mapa binario de los bordes de las aponeurosis.

6.  **Paso 5: Filtrado y Trazado de Líneas**
    *   Se miden todos los bordes detectados y se eliminan los que son demasiado cortos, quedándose únicamente con las líneas largas que representan las aponeurosis.
    *   Finalmente, se trazan las coordenadas de las aponeurosis superior e inferior para su posterior análisis.

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
