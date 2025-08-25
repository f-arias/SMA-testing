import os
import cv2
import csv
import numpy as np
from skimage.feature import structure_tensor
from skimage.filters import sato

def bandpass_filter(image, filter_small, filter_large):
    """
    Replica el filtro de paso de banda de ImageJ mediante la Diferencia de Gaussianas.
    """
    # Asegurarse de que los tamaños del kernel sean impares
    k_small = int(2 * round(float(filter_small)) + 1)
    k_large = int(2 * round(float(filter_large)) + 1)

    img_blur_small = cv2.GaussianBlur(image, (k_small, k_small), filter_small)
    img_blur_large = cv2.GaussianBlur(image, (k_large, k_large), filter_large)

    # Diferencia de Gaussianas
    img_dog = cv2.subtract(img_blur_small, img_blur_large)

    return img_dog

def fft_filter_and_threshold(image, percentile=99.9):
    """
    Realiza un filtrado y umbralización basado en FFT como en el macro.
    """
    fft_img = np.fft.fft2(image)
    fft_shifted = np.fft.fftshift(fft_img)
    magnitude_spectrum = np.log(np.abs(fft_shifted) + 1)

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
    Procesa una única imagen para el análisis de arquitectura muscular,
    siguiendo fielmente la secuencia de procesamiento del macro de Fiji.
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
    H, W = image.shape[:2]
    if cropping_type == "Manual":
        # La lógica para obtener el ROI manual estaría en la GUI
        return image # Placeholder
    else:
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
    height, width = binary_mask.shape
    mid_x = width // 2
    search_region_y = (0, int(height * search_height_ratio)) if search_from_top else (int(height * (1-search_height_ratio)), height)
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
    path = []
    height, width = image.shape
    current_y = y
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
