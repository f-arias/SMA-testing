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

Debe ejecutar cada versión desde su respectivo directorio.

**Para ejecutar la versión 2.3.3:**
```bash
cd SMA_python_233
python main_233.py
```

**Para ejecutar la versión 1.7.1:**
```bash
cd SMA_python_171
python main_171.py
```
Ambos comandos abrirán una interfaz gráfica de usuario (GUI) específica para esa versión donde podrá configurar los parámetros del análisis.

## Salida del Programa

Ambas versiones generan un archivo de resultados en formato `.csv` con los parámetros calculados. Sin embargo, la imagen de salida es diferente.

### Salida v2.3.3
-   **Imágenes Procesadas:** Por cada imagen de entrada, se guarda una nueva imagen con el prefijo `processed_`. Esta imagen muestra la foto original con las **aponeurosis detectadas** y una representación del **fascículo promedio** superpuestas.
-   **Archivo de Resultados (`resultados.csv`):** Un único archivo CSV con los datos de todas las imágenes procesadas.

### Salida v1.7.1
-   **Máscara Binaria:** Por cada imagen de entrada, se guarda una nueva imagen con el prefijo `processed_mask_`. Esta imagen es una máscara en blanco y negro, donde las **aponeurosis detectadas se muestran en blanco** sobre un fondo negro.
-   **Archivo de Resultados (`resultados_171.csv`):** Un único archivo CSV con los datos de todas las imágenes procesadas por esta versión.
