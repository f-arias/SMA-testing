import os
import cv2
import csv
import numpy as np
from skimage.feature import structure_tensor
from skimage.filters import sato

def bandpass_filter(image, filter_small, filter_large):
    """
    Aplica un filtro de paso de banda utilizando una Diferencia de Gaussianas (DoG).

    Este método simula el filtro de paso de banda de ImageJ, que es eficaz para
    eliminar ruido de baja frecuencia (variaciones de fondo) y de alta frecuencia
    (ruido fino), conservando las estructuras de interés en una banda de
    frecuencia intermedia.

    Args:
        image (numpy.ndarray):
            La imagen de entrada en escala de grises.
        filter_small (float):
            El sigma (desviación estándar) para el Gaussiano más pequeño. Este
            valor controla la eliminación de las estructuras de alta frecuencia
            (ruido más fino). Un valor más alto suaviza más.
        filter_large (float):
            El sigma para el Gaussiano más grande. Este valor controla la
            eliminación de las estructuras de baja frecuencia (fondo). Un valor
            más alto elimina variaciones de fondo más grandes.

    Returns:
        numpy.ndarray:
            La imagen filtrada, resultado de la resta del Gaussiano grande al
            Gaussiano pequeño.
    """
    # Asegurarse de que los tamaños del kernel sean impares, como requiere cv2.GaussianBlur
    k_small = int(2 * round(float(filter_small)) + 1)
    k_large = int(2 * round(float(filter_large)) + 1)

    # Aplicar los dos desenfoques Gaussianos
    img_blur_small = cv2.GaussianBlur(image, (k_small, k_small), filter_small)
    img_blur_large = cv2.GaussianBlur(image, (k_large, k_large), filter_large)

    # La Diferencia de Gaussianas es la resta de las dos imágenes desenfocadas
    img_dog = cv2.subtract(img_blur_small, img_blur_large)

    return img_dog

def fft_filter_and_threshold(image, percentile=99.9):
    """
    Filtra una imagen en el dominio de la frecuencia usando la FFT y umbraliza el espectro.

    Este proceso es clave para aislar las aponeurosis, que aparecen como señales
    fuertes y orientadas en el espectro de frecuencia. Pasos:
    1. Calcula la Transformada Rápida de Fourier (FFT) de la imagen.
    2. Calcula el espectro de magnitud y lo umbraliza para conservar solo las
       frecuencias más fuertes (las que superan un percentil alto).
    3. Crea una máscara para eliminar las componentes de frecuencia débiles y
       también un artefacto común en el centro del espectro (el componente DC).
    4. Aplica la máscara y realiza la FFT inversa para reconstruir la imagen.
    El resultado es una imagen donde solo las estructuras más dominantes y
    periódicas (idealmente, las aponeurosis) permanecen.

    Args:
        image (numpy.ndarray):
            La imagen de entrada en escala de grises.
        percentile (float, optional):
            El percentil utilizado para determinar el umbral en el espectro de
            magnitud. Solo las frecuencias con una magnitud por encima de este
            percentil se conservarán. Por defecto es 99.9.

    Returns:
        numpy.ndarray:
            La imagen filtrada y normalizada a 8 bits (0-255). En esta imagen,
            las aponeurosis deberían aparecer como líneas nítidas sobre un fondo
            oscuro.
    """
    # 1. Calcular la FFT y centrar el espectro
    fft_img = np.fft.fft2(image)
    fft_shifted = np.fft.fftshift(fft_img)
    magnitude_spectrum = np.log(np.abs(fft_shifted) + 1) # Usar escala logarítmica para visualización/análisis

    hist, bin_edges = np.histogram(magnitude_spectrum.ravel(), bins=256)
    cdf = np.cumsum(hist)
    cdf_normalized = cdf / cdf.max()

    threshold_idx = np.searchsorted(cdf_normalized, percentile / 100.0)
    threshold = bin_edges[threshold_idx]

    mask = magnitude_spectrum >= threshold

    h, w = image.shape
    center_h, center_w = h // 2, w // 2
    mask[center_h-2:center_h+2, :] = 0
    mask[:, center_w-2:center_w+2] = 0

    fft_shifted_filtered = fft_shifted * mask
    fft_ifft_shifted = np.fft.ifftshift(fft_shifted_filtered)
    img_back = np.fft.ifft2(fft_ifft_shifted)
    img_back = np.abs(img_back)

    img_back_norm = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    return img_back_norm

def process_single_image_171(image_path, params):
    """
    Ejecuta el pipeline completo de análisis de arquitectura muscular en una sola imagen.

    Esta función es el núcleo del análisis y sigue la secuencia de pasos del macro
    original de Fiji para asegurar la consistencia de los resultados. Los pasos incluyen:
    1. Carga y recorte de la imagen.
    2. Pre-procesamiento: sustracción de fondo, reducción de ruido (NL-Means),
       filtro paso de banda y mejora de contraste (CLAHE).
    3. Realce de aponeurosis con el filtro Sato (Tubeness).
    4. Limpieza final mediante filtrado en el dominio de la frecuencia (FFT).
    5. Detección de bordes con Canny.
    6. Filtrado de contornos para aislar las aponeurosis.
    7. Trazado y ajuste de las líneas de las aponeurosis.
    8. Cálculo de los parámetros de arquitectura: grosor, ángulo de penación (α),
       ángulo de la aponeurosis (β) y longitud del fascículo.

    Args:
        image_path (str):
            La ruta completa al archivo de imagen que se va a analizar.
        params (dict):
            Un diccionario que contiene todos los parámetros necesarios para el
            análisis, como los sigmas para los filtros, el método de recorte, etc.

    Returns:
        tuple:
            - results (dict or None): Un diccionario con los parámetros de
              arquitectura calculados (grosor, ángulos, longitud del fascículo).
              Es `None` si el análisis falla en un punto crítico.
            - output_mask (numpy.ndarray or None): Una imagen binaria (máscara)
              del mismo tamaño que la imagen recortada, mostrando las aponeurosis
              detectadas. Es `None` si el análisis falla.
            - detection_status (dict): Un diccionario que informa sobre el éxito
              de la detección de las aponeurosis y la razón del fallo si ocurre.
    """
    detection_status = {
        "upper_found": False,
        "lower_found": False,
        "both_found": False,
        "failure_reason": "Analysis not started"
    }

    # Cargar la imagen en escala de grises
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error al leer la imagen: {image_path}")
        detection_status["failure_reason"] = "Error reading image"
        return None, None, detection_status

    # --- Inicio del Flujo de Procesamiento del Macro de Fiji ---

    # PASO 1: Recorte de la Imagen para aislar la región muscular.
    img_cropped = perform_cropping(img, params["cropping"])

    # --- PASO 2: Pre-procesamiento y Reducción de Ruido ---
    # 2.1. Sustraer Fondo: Corrige variaciones de brillo no uniformes en la imagen.
    kernel_bg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
    background = cv2.morphologyEx(img_cropped, cv2.MORPH_OPEN, kernel_bg)
    img_no_bg = cv2.subtract(img_cropped, background)

    # 2.2. Denoise (Non-local Means): Filtro de reducción de ruido avanzado.
    img_denoised = cv2.fastNlMeansDenoising(img_no_bg, h=15)

    # 2.3. Filtro Paso de Banda (Bandpass Filter): Elimina ruido de alta y baja frecuencia.
    img_bandpass = bandpass_filter(img_denoised, params['filter_small'], params['filter_large'])

    # 2.4. Mejora de Contraste (CLAHE): Realza el contraste localmente para destacar estructuras.
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(36,36))
    img_clahe = clahe.apply(img_bandpass)

    # PASO 3: Realce de Aponeurosis (Tubeness).
    # Este es un paso CRÍTICO. El filtro Sato (Tubeness) está diseñado para realzar
    # estructuras con forma de línea, como las aponeurosis. El parámetro 'Tsigma'
    # controla la "escala" o grosor de las líneas a detectar.
    sigma_val = int(params.get("Tsigma", 10))
    if sigma_val == 0: sigma_val = 1
    img_tubeness = sato(img_clahe, sigmas=range(sigma_val, sigma_val + 1), black_ridges=False)
    img_tubeness = cv2.normalize(img_tubeness, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # PASO 4: Limpieza con Transformada Rápida de Fourier (FFT).
    # Se usa la FFT para aislar las señales más fuertes (las aponeurosis) y eliminar
    # el ruido de fondo restante que el filtro Tubeness no eliminó.
    img_fft_filtered = fft_filter_and_threshold(img_tubeness, percentile=99.9)

    # PASO 5: Detección de Bordes (Canny).
    # Sobre la imagen ultra-filtrada, Canny detecta los bordes finos de las aponeurosis.
    edges = cv2.Canny(image=img_fft_filtered, threshold1=50, threshold2=150)

    # PASO 6: Filtrado de Contornos y Trazado de Líneas.
    # Se miden todos los bordes detectados y se descartan los que son demasiado cortos.
    # Solo las líneas largas, que corresponden a las aponeurosis, son conservadas.
    WFoV = img_cropped.shape[1]
    minLength = 0.3 * WFoV
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask_long_contours = np.zeros_like(edges)

    long_contours = [c for c in contours if cv2.arcLength(c, False) > minLength]

    if len(long_contours) < 2:
        msg = f"No se encontraron suficientes contornos largos (se encontraron {len(long_contours)})."
        print(msg)
        detection_status["failure_reason"] = msg
        return None, None, detection_status

    cv2.drawContours(mask_long_contours, long_contours, -1, 255, thickness=cv2.FILLED)

    # Trazar las líneas de las aponeurosis superior e inferior
    upper_aponeurosis = find_aponeurosis_line(mask_long_contours, search_from_top=True)
    lower_aponeurosis = find_aponeurosis_line(mask_long_contours, search_from_top=False)

    if upper_aponeurosis:
        detection_status["upper_found"] = True
    if lower_aponeurosis:
        detection_status["lower_found"] = True

    if not upper_aponeurosis or not lower_aponeurosis:
        msg = "No se pudieron detectar ambas aponeurosis (superior: {}, inferior: {})".format(
            "encontrada" if upper_aponeurosis else "no encontrada",
            "encontrada" if lower_aponeurosis else "no encontrada"
        )
        print(msg)
        detection_status["failure_reason"] = msg
        return None, None, detection_status

    detection_status["both_found"] = True
    upper_points = np.array(upper_aponeurosis)
    lower_points = np.array(lower_aponeurosis)

    # --- Cálculo de Parámetros de Arquitectura Muscular ---
    # Ángulo de la aponeurosis inferior (beta)
    lower_fit = np.polyfit(lower_points[:, 0], lower_points[:, 1], 1)
    beta = np.rad2deg(np.arctan(lower_fit[0]))

    # Definir la región de interés (ROI) para el análisis de fascículos
    y_min_roi = int(np.max(upper_points[:, 1]))
    y_max_roi = int(np.min(lower_points[:, 1]))
    x_min_roi = int(np.min(lower_points[:, 0]))
    x_max_roi = int(np.max(lower_points[:, 0]))

    if y_min_roi >= y_max_roi or x_min_roi >= x_max_roi:
        msg = "ROI inválido, las aponeurosis podrían haberse cruzado."
        print(msg)
        detection_status["failure_reason"] = msg
        return None, None, detection_status

    fascicle_roi = img_cropped[y_min_roi:y_max_roi, x_min_roi:x_max_roi]

    if fascicle_roi.size == 0:
        msg = "El ROI para el análisis de fascículos está vacío."
        print(msg)
        detection_status["failure_reason"] = msg
        return None, None, detection_status

    # Ángulo de los fascículos (alfa) usando el tensor de estructura
    sigma_orientation = float(params.get("Osigma", 4.0))
    if sigma_orientation == 0: sigma_orientation = 0.1
    Axx, Axy, Ayy = structure_tensor(fascicle_roi, sigma=sigma_orientation, mode='constant')
    orientation_map = np.rad2deg(0.5 * np.arctan2(2 * Axy, Ayy - Axx))
    orientation_map += 90  # Ajuste para la orientación de los fascículos
    alpha = np.nanmean(orientation_map)

    # Ángulo de penación
    pennation_angle = alpha + beta

    # Grosor del músculo
    common_x_min = max(np.min(upper_points[:, 0]), np.min(lower_points[:, 0]))
    common_x_max = min(np.max(upper_points[:, 0]), np.max(lower_points[:, 0]))
    common_x = np.linspace(common_x_min, common_x_max, num=int(common_x_max - common_x_min))
    y_interp_upper = np.interp(common_x, upper_points[:, 0], upper_points[:, 1])
    y_interp_lower = np.interp(common_x, lower_points[:, 0], lower_points[:, 1])
    thickness = np.mean(y_interp_lower - y_interp_upper)

    # Longitud del fascículo
    if np.sin(np.deg2rad(pennation_angle)) == 0:
        fascicle_length = float('inf')
    else:
        fascicle_length = thickness / np.sin(np.deg2rad(pennation_angle))

    # --- Preparación de Resultados ---
    results = {
        "thickness": thickness,
        "pennation_angle": pennation_angle,
        "fascicle_length": fascicle_length,
        "fascicle_angle_alpha": alpha,
        "aponeurosis_angle_beta": beta,
    }

    # Creación de la máscara de salida
    output_mask = np.zeros_like(img_cropped, dtype=np.uint8)
    cv2.polylines(output_mask, [upper_points.astype(np.int32)], isClosed=False, color=255, thickness=2)
    cv2.polylines(output_mask, [lower_points.astype(np.int32)], isClosed=False, color=255, thickness=2)

    detection_status["failure_reason"] = "" # Success
    return results, output_mask, detection_status

# --- Funciones de ayuda duplicadas para que el script sea autocontenido ---

def perform_cropping(image, cropping_type, manual_roi=None):
    """
    Recorta la imagen para aislar la región del músculo.

    Puede operar de dos maneras:
    1. "Automatic": Detecta el contorno más grande en la imagen (asumiendo que
       es el transductor de ultrasonido o el músculo principal), calcula su
       cuadro delimitador y lo recorta con un pequeño margen.
    2. "Manual": En un entorno de GUI, usaría un ROI (Región de Interés)
       definido por el usuario. En este script, este modo es un marcador de
       posición y simplemente devuelve la imagen original.

    Args:
        image (numpy.ndarray):
            La imagen de entrada en escala de grises.
        cropping_type (str):
            El método de recorte a utilizar, "Automatic" o "Manual".
        manual_roi (tuple, optional):
            Las coordenadas del ROI para el recorte manual, en formato (x, y, w, h).
            No se utiliza actualmente en el modo no-GUI. Por defecto es None.

    Returns:
        numpy.ndarray:
            La imagen recortada. Si el recorte automático falla o el modo es
            manual (sin GUI), devuelve la imagen original.
    """
    H, W = image.shape[:2]
    if cropping_type == "Manual":
        # En un script sin GUI, el recorte manual no es directamente aplicable.
        # Se podría pasar un ROI, pero por ahora, es un placeholder.
        # Si se proporciona un manual_roi, se podría aplicar aquí.
        if manual_roi:
            x, y, w, h = manual_roi
            return image[y:y+h, x:x+w]
        return image # Devuelve la imagen original si no hay ROI.
    else: # Recorte automático
        # El recorte automático se basa en encontrar el contorno más grande.
        # Funciona mejor con imágenes de 8 bits.
        if image.dtype != np.uint8:
            img_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        else:
            img_8bit = image
        blurred = cv2.GaussianBlur(img_8bit, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: return image
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        Le = int(x + w * 0.005); Up = int(y + h * 0.01)
        width = int(w * 0.98); height = int(h * 0.97)
        return image[Up:Up+height, Le:Le+width]

def find_aponeurosis_line(binary_mask, search_from_top=True, search_height_ratio=0.5):
    """
    Encuentra la línea de una aponeurosis (superior o inferior) en una máscara binaria.

    El proceso funciona de la siguiente manera:
    1. Define una región de búsqueda vertical en el centro de la imagen. Para la
       aponeurosis superior, busca en la mitad superior de la imagen; para la
       inferior, en la mitad inferior.
    2. Identifica todos los puntos de inicio potenciales (píxeles blancos) en
       esa línea vertical central.
    3. Para cada punto de inicio, intenta trazar una línea hacia la izquierda y
       hacia la derecha.
    4. La primera línea combinada (izquierda + centro + derecha) que sea lo
       suficientemente larga (más del 30% del ancho de la imagen) se considera
       la aponeurosis y se devuelve.

    Args:
        binary_mask (numpy.ndarray):
            Una imagen binaria donde los contornos largos (potenciales aponeurosis)
            son píxeles blancos.
        search_from_top (bool, optional):
            Si es `True`, busca la aponeurosis superior en la mitad superior de
            la imagen. Si es `False`, busca la aponeurosis inferior en la mitad
            inferior. Por defecto es `True`.
        search_height_ratio (float, optional):
            La proporción de la altura de la imagen a utilizar para la búsqueda
            inicial. Por defecto es 0.5 (mitad superior o inferior).

    Returns:
        list of tuples or None:
            Una lista de coordenadas (x, y) que representan la línea de la
            aponeurosis encontrada. Devuelve `None` si no se encuentra una línea
            que cumpla con el criterio de longitud.
    """
    height, width = binary_mask.shape
    mid_x = width // 2

    # Definir la región de búsqueda (superior o inferior)
    search_region_y = (0, int(height * search_height_ratio)) if search_from_top else (int(height * (1 - search_height_ratio)), height)
    vertical_profile = binary_mask[search_region_y[0]:search_region_y[1], mid_x]
    potential_starts_y_offset = np.where(vertical_profile > 0)[0]
    if not potential_starts_y_offset.any(): return None
    potential_starts_y = potential_starts_y_offset + search_region_y[0]
    best_line = []
    y_starts_to_check = potential_starts_y if search_from_top else reversed(potential_starts_y)
    for start_y in y_starts_to_check:
        path_right = trace_line(binary_mask, mid_x + 1, start_y, direction=1)
        path_left = trace_line(binary_mask, mid_x - 1, start_y, direction=-1)
        combined_path = path_left[::-1] + [(mid_x, start_y)] + path_right
        if len(combined_path) > width * 0.3:
            best_line = combined_path
            break
    return best_line

def trace_line(image, start_x, y, direction, search_radius=2):
    """
    Traza una línea de píxeles conectados desde un punto de inicio.

    Avanza columna por columna (hacia la izquierda o derecha) desde un punto de
    inicio (start_x, y). En cada columna, busca el siguiente píxel blanco en una
    pequeña ventana vertical (definida por `search_radius`) centrada en la
    posición y del píxel anterior. Este enfoque "voraz" permite seguir una línea
    incluso si tiene pequeñas interrupciones o curvaturas.

    Args:
        image (numpy.ndarray):
            La imagen binaria en la que se trazará la línea.
        start_x (int):
            La coordenada x desde la que comenzar el trazado.
        y (int):
            La coordenada y inicial del trazado.
        direction (int):
            La dirección del trazado: 1 para derecha, -1 para izquierda.
        search_radius (int, optional):
            El radio vertical (en píxeles) para buscar el siguiente punto de la
            línea en la columna adyacente. Por defecto es 2.

    Returns:
        list of tuples:
            Una lista de coordenadas (x, y) que forman la ruta trazada. La lista
            estará vacía si no se puede encontrar ningún píxel inicial.
    """
    path = []
    height, width = image.shape
    current_y = y

    # Determinar el rango de x para el bucle según la dirección
    x_range = range(start_x, width) if direction == 1 else range(start_x, -1, -1)
    for x in x_range:
        y_min = max(0, current_y - search_radius)
        y_max = min(height, current_y + search_radius + 1)
        search_window = image[y_min:y_max, x]
        if np.any(search_window > 0):
            new_y_offset = np.argmax(search_window)
            current_y = y_min + new_y_offset
            path.append((x, current_y))
        else:
            break
    return path

def SMA(input_image_path, output_path, analysis_params=None, csv_output=True):
    """
    Función principal para el análisis de arquitectura muscular (SMA).

    Esta función es una implementación en Python que busca replicar fielmente
    el flujo de trabajo de procesamiento del macro original de Fiji (SMA 1.7.1).
    Aplica una secuencia de filtros (Paso de Banda, CLAHE, Tubeness, FFT) para
    detectar las aponeurosis y calcular los parámetros de la arquitectura muscular.
        Args:
        input_image_path (str):
            Ruta de la imagen de ultrasonido a analizar.
        output_path (str):
            Ruta del directorio donde se guardarán los resultados.
        analysis_params (dict, optional):
            Diccionario para anular los parámetros de análisis por defecto.
            Si es None, se utilizarán los valores por defecto.
        csv_output (bool, optional):
            Si es True, se guardará un archivo CSV con los resultados.
            Defaults to True.
    Returns:
        tuple:
            - results (dict): Diccionario con los parámetros calculados.
            - output_mask (numpy.ndarray): Máscara con las aponeurosis detectadas.
            Retorna (None, None) si el análisis falla.
    """
    # Parámetros de análisis por defecto, replicando la GUI del macro 1.7.1.
    default_params = {
        "cropping": "Automatic", "Osigma": "4", "Tsigma": 10,
        "filter_small": 3, "filter_large": 40, "extrapolate_from": "100%",
        "ROIn": 3, "ROIwidth": 60, "ROIheight": 90, "autThresh": True,
        "manThresh": 175, "Pa": "max",
    }

    params = default_params.copy()
    if analysis_params:
        params.update(analysis_params)

    # Procesar la imagen
    results, output_mask, detection_status = process_single_image_171(input_image_path, params)

    # Si el análisis es exitoso, guardar la máscara y el CSV (si está habilitado)
    if results and output_mask is not None:
        if os.path.isdir(output_path):
            os.makedirs(output_path, exist_ok=True)
            filename, _ = os.path.splitext(os.path.basename(input_image_path))
            output_image_path = os.path.join(output_path, f"processed_mask_{filename}.png")
            cv2.imwrite(output_image_path, output_mask)
            # print(f"Máscara procesada guardada en: {output_image_path}")

        if csv_output:
            results["image_name"] = os.path.basename(input_image_path)
            output_csv_path = os.path.join(output_path, "resultados_171_fiel.csv")
            file_exists = os.path.isfile(output_csv_path)
            with open(output_csv_path, 'a', newline='') as csvfile:
                fieldnames = sorted(results.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(results)
            # print(f"Resultados guardados en: {output_csv_path}")

        return results, output_mask, detection_status

    # Si el análisis falla, devuelve None y el estado de detección con el fallo
    # print(f"El análisis de {os.path.basename(input_image_path)} no pudo completarse.")
    return None, None, detection_status
