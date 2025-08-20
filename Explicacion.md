# Explicación de la Función `SMA`

La función `SMA` es el componente central del proyecto de análisis de arquitectura muscular para la versión 1.7.1. Ha sido diseñada para simplificar el proceso de análisis, eliminando la necesidad de una interfaz gráfica y permitiendo su uso directo en scripts de Python.

## Descripción General

La función `SMA` toma la ruta de una imagen de ultrasonido de un músculo y realiza un análisis para detectar las aponeurosis (las membranas de tejido conectivo que recubren el músculo) y calcular una serie de parámetros clave de la arquitectura muscular.

El proceso incluye los siguientes pasos:
1.  **Pre-procesamiento de la imagen:** Mejora de la calidad de la imagen para facilitar la detección de características.
2.  **Detección de aponeurosis:** Identificación de las aponeurosis superior e inferior.
3.  **Cálculo de parámetros:** Medición del grosor muscular, ángulo de penación, longitud de los fascículos, etc.
4.  **Generación de resultados:** Guarda una imagen de máscara con las aponeurosis detectadas y, opcionalmente, un archivo CSV con los parámetros calculados.

## Uso de la Función

La función se encuentra en el módulo `analysis_171.py` y se puede importar y utilizar como se muestra a continuación.

### Firma de la Función

```python
SMA(input_image_path, output_path, analysis_params=None, csv_output=False, general_config=None)
```

### Argumentos de Entrada

| Argumento | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| `input_image_path` | `str` | Ruta completa de la imagen de ultrasonido que se va a analizar. | Sí |
| `output_path` | `str` | Ruta del directorio donde se guardarán los archivos de salida (la máscara y el CSV). Si el directorio no existe, se creará. | Sí |
| `analysis_params` | `dict` | Un diccionario opcional para especificar los parámetros de análisis. Si no se proporciona, se usarán los valores por defecto. | No |
| `csv_output` | `bool` | Un booleano que, si se establece en `True`, guardará los resultados numéricos en un archivo CSV en el `output_path`. | No |
| `general_config` | `dict` | Un diccionario para configuraciones generales. Actualmente no se utiliza en esta versión. | No |

### Parámetros de Análisis (`analysis_params`)

El diccionario `analysis_params` permite ajustar el comportamiento del análisis. Los parámetros más importantes son:

-   `cropping` (str): Define el método de recorte de la imagen.
    -   `"Automatic"` (por defecto): El sistema intenta encontrar el contorno del músculo y recorta la imagen automáticamente.
    -   `"Manual"`: No realiza ningún recorte (útil si la imagen ya está preparada).
-   `Osigma` (str): El valor de "sigma" para el filtro del tensor de estructura, que se utiliza para determinar la orientación de los fascículos musculares. Un valor típico es `"4"`.

### Valores de Retorno

La función `SMA` devuelve una tupla con dos elementos:

1.  **`results` (dict):** Un diccionario que contiene los parámetros de arquitectura muscular calculados. Las claves incluyen:
    -   `thickness`: El grosor del músculo.
    -   `pennation_angle`: El ángulo de penación.
    -   `fascicle_length`: La longitud de los fascículos.
    -   `fascicle_angle_alpha`: El ángulo de los fascículos (alfa).
    -   `aponeurosis_angle_beta`: El ángulo de la aponeurosis (beta).
2.  **`output_mask` (numpy.ndarray):** Una imagen (en formato de array de NumPy) que muestra las líneas de las aponeurosis detectadas sobre un fondo negro.

Si el análisis falla (por ejemplo, si no se pueden detectar las aponeurosis), la función devolverá `(None, None)`.

### Ejemplo de Uso

El siguiente código muestra cómo llamar a la función `SMA` para analizar una imagen y procesar los resultados.

```python
import os
from sma_python.SMA_python_171.analysis_171 import SMA

# --- 1. Configuración de rutas ---
# Define la ruta de la imagen de entrada y el directorio de salida.
input_image = "sma_python/GM_telemedLS_sample_A/GM_T_1.png"
output_directory = "sma_python/output_results"

# Crea el directorio de salida si no existe.
os.makedirs(output_directory, exist_ok=True)


# --- 2. (Opcional) Definir parámetros de análisis ---
# Si quieres usar valores diferentes a los predeterminados.
custom_params = {
    "cropping": "Automatic",
    "Osigma": "4"
}


# --- 3. Llamar a la función SMA ---
# Se activa la opción de guardar el archivo CSV.
results, mask = SMA(
    input_image_path=input_image,
    output_path=output_directory,
    analysis_params=custom_params,
    csv_output=True
)


# --- 4. Procesar los resultados ---
if results and mask is not None:
    print("El análisis se ha completado con éxito.")
    print("\nResultados calculados:")
    for param, value in results.items():
        print(f"- {param}: {value:.2f}")

    # La máscara y el CSV ya han sido guardados por la función.
    print(f"\nLa imagen de la máscara y el archivo CSV se han guardado en: {output_directory}")
else:
    print("El análisis no pudo completarse.")

```

Este ejemplo demuestra el flujo de trabajo completo: configurar las rutas, llamar a la función con parámetros personalizados y gestionar la salida.
