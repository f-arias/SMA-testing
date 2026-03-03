# Explicación del Framework de Análisis y Testeo de SMA

Este documento proporciona una explicación detallada de la función `SMA` y el conjunto de herramientas de testeo desarrolladas para analizar y validar el proceso de detección de la arquitectura muscular.

## 1. La Función Principal `SMA`

La función `SMA` es el componente central del proyecto. Ha sido diseñada para analizar una imagen de ultrasonido de un músculo, detectar sus aponeurosis y calcular parámetros clave de su arquitectura.

### Proceso de Análisis
1.  **Pre-procesamiento:** Se aplican una serie de filtros para mejorar la calidad de la imagen y reducir el ruido.
2.  **Detección de Aponeurosis:** Se utiliza un filtro de "tubeness" (controlado por `Tsigma`) para realzar las aponeurosis, seguido de un filtrado de contornos para aislarlas.
3.  **Cálculo de Parámetros:** Si las aponeurosis se detectan correctamente, se miden el grosor muscular, el ángulo de penación, la longitud de los fascículos, etc.
4.  **Generación de Resultados:** La función devuelve los resultados numéricos, una máscara de la detección y un estado detallado del proceso.

### Firma de la Función

La función se encuentra en `sma_python/SMA_python_171/analysis_171.py`.

```python
SMA(input_image_path, output_path, analysis_params=None, csv_output=True)
```

### Argumentos de Entrada

| Argumento | Tipo | Descripción |
|---|---|---|
| `input_image_path` | `str` | Ruta de la imagen de ultrasonido a analizar. |
| `output_path` | `str` | Directorio donde se guardarán los archivos de salida. |
| `analysis_params` | `dict` | (Opcional) Diccionario para anular los parámetros por defecto. |
| `csv_output` | `bool` | (Opcional) Si es `True`, guarda un CSV con los resultados. |

### Parámetros de Análisis (`analysis_params`)

-   `Tsigma` (int): **Parámetro crítico.** Define la "escala" o grosor de las aponeurosis que el filtro "tubeness" intentará detectar. El testeo intensivo ha demostrado que **`Tsigma = 2` es el valor óptimo** para el conjunto de imágenes de muestra.
-   `Osigma` (str): Sigma para el tensor de estructura, usado para el análisis de orientación de los fascículos.
-   `cropping` (str): `"Automatic"` (por defecto) o `"Manual"`.

### Valores de Retorno

La función `SMA` devuelve una tupla con tres elementos:

1.  **`results` (dict):** Un diccionario con los parámetros de arquitectura muscular calculados (`thickness`, `pennation_angle`, etc.). Es `None` si el análisis falla.
2.  **`output_mask` (numpy.ndarray):** Una imagen de máscara con las aponeurosis detectadas. Es `None` si el análisis falla.
3.  **`detection_status` (dict):** Un diccionario con información detallada sobre el éxito del proceso de detección. Sus claves son:
    -   `upper_found` (bool): `True` si se detectó la aponeurosis superficial.
    -   `lower_found` (bool): `True` si se detectó la aponeurosis profunda.
    -   `both_found` (bool): `True` si ambas se detectaron.
    -   `failure_reason` (str): Un mensaje que describe la causa del fallo si el análisis no fue exitoso.

### Ejemplo de Uso Actualizado

```python
import os
from sma_python.SMA_python_171.analysis_171 import SMA

# --- 1. Configuración ---
input_image = "sma_python/GM_telemedLS_sample_A/GM_T_1.png"
output_directory = "sma_python/output_results"
os.makedirs(output_directory, exist_ok=True)

# --- 2. Llamar a la función SMA ---
results, mask, status = SMA(
    input_image_path=input_image,
    output_path=output_directory,
    analysis_params={"Tsigma": 2}, # Usar el valor óptimo
    csv_output=True
)

# --- 3. Procesar los resultados ---
if status["both_found"]:
    print("Análisis completado con éxito.")
    print("\nResultados calculados:")
    for param, value in results.items():
        if isinstance(value, float):
            print(f"- {param}: {value:.2f}")
        else:
            print(f"- {param}: {value}")
else:
    print(f"El análisis falló. Razón: {status['failure_reason']}")

```

---

## 2. Framework de Testeo y Análisis

Para validar la función `SMA` y optimizar el parámetro `Tsigma`, se ha desarrollado un conjunto de scripts de Python.

### `test_intensive_sma171.py`
Este script realiza un testeo exhaustivo de la función `SMA`.
-   Itera sobre todas las imágenes de los directorios de muestra.
-   Prueba un rango de valores de `Tsigma` (de 1 a 12).
-   Guarda los resultados detallados de cada ejecución en `Tsigma_test_results.csv`.

**Para ejecutar el test:**
```bash
python3 test_intensive_sma171.py
```

### `analyze_results.py`
Este script lee el archivo `Tsigma_test_results.csv` y realiza un análisis de rendimiento.
-   Calcula la tasa de éxito para la detección de la aponeurosis superior, inferior y ambas, para cada valor de `Tsigma`.
-   Imprime una tabla resumen en la consola.
-   Genera un gráfico (`Tsigma_test_results.png`) que visualiza estos resultados e identifica el mejor `Tsigma`.

**Para analizar los resultados del test:**
```bash
python3 analyze_results.py
```

### `summarize_failures.py`
Este script proporciona un análisis más profundo de por qué fallan las detecciones.
-   Analiza las razones de fallo para el valor de `Tsigma` más óptimo.
-   Ofrece una explicación cualitativa de cómo los valores de `Tsigma` (bajos, medios y altos) afectan al proceso de detección.

**Para obtener el resumen de fallos:**
```bash
python3 summarize_failures.py
```

Estos scripts juntos forman un framework robusto para la validación continua y la optimización de la función `SMA`.
