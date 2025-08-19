import os
import cv2
import numpy as np
from skimage.feature import structure_tensor

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
    Procesa una única imagen según la lógica de la v1.7.1.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error al leer la imagen: {image_path}")
        return None, None

    # Reutilizar funciones de análisis_233 requiere que estén en el mismo directorio o en el path de python.
    # Por simplicidad, copiaremos las funciones necesarias aquí.
    img_cropped = perform_cropping(img, params["cropping"])

    kernel_bg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
    background = cv2.morphologyEx(img_cropped, cv2.MORPH_OPEN, kernel_bg)
    img_no_bg = cv2.subtract(img_cropped, background)
    img_denoised = cv2.fastNlMeansDenoising(img_no_bg, h=15)

    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(36,36))
    img_clahe = clahe.apply(img_denoised)

    img_fft_filtered = fft_filter_and_threshold(img_clahe, percentile=99.9)
    edges = cv2.Canny(image=img_fft_filtered, threshold1=50, threshold2=150)

    WFoV = img_cropped.shape[1]
    minLength = 0.8 * WFoV
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_long_contours = np.zeros_like(edges)
    for contour in contours:
        if cv2.arcLength(contour, closed=False) >= minLength:
            cv2.drawContours(mask_long_contours, [contour], -1, 255, thickness=cv2.FILLED)

    upper_aponeurosis = find_aponeurosis_line(mask_long_contours, search_from_top=True)
    lower_aponeurosis = find_aponeurosis_line(mask_long_contours, search_from_top=False)

    if not upper_aponeurosis or not lower_aponeurosis:
        print("No se pudieron detectar ambas aponeurosis.")
        return None, None

    upper_points = np.array(upper_aponeurosis)
    lower_points = np.array(lower_aponeurosis)

    lower_fit = np.polyfit(lower_points[:, 0], lower_points[:, 1], 1)
    beta = np.rad2deg(np.arctan(lower_fit[0]))

    y_min_roi = int(np.max(upper_points[:, 1]))
    y_max_roi = int(np.min(lower_points[:, 1]))
    x_min_roi = int(np.min(lower_points[:, 0]))
    x_max_roi = int(np.max(lower_points[:, 0]))

    if y_min_roi >= y_max_roi or x_min_roi >= x_max_roi:
        print("ROI inválido, las aponeurosis podrían haberse cruzado.")
        return None, None

    fascicle_roi = img_cropped[y_min_roi:y_max_roi, x_min_roi:x_max_roi]

    if fascicle_roi.size == 0:
        print("El ROI para el análisis de fascículos está vacío.")
        return None, None

    sigma_orientation = float(params.get("Osigma", 4.0))
    if sigma_orientation == 0: sigma_orientation = 0.1
    Axx, Axy, Ayy = structure_tensor(fascicle_roi, sigma=sigma_orientation, mode='constant')
    orientation_map = np.rad2deg(0.5 * np.arctan2(2 * Axy, Ayy - Axx))
    orientation_map += 90
    alpha = np.nanmean(orientation_map)

    pennation_angle = alpha + beta

    common_x_min = max(np.min(upper_points[:, 0]), np.min(lower_points[:, 0]))
    common_x_max = min(np.max(upper_points[:, 0]), np.max(lower_points[:, 0]))
    common_x = np.linspace(common_x_min, common_x_max, num=int(common_x_max - common_x_min))
    y_interp_upper = np.interp(common_x, upper_points[:, 0], upper_points[:, 1])
    y_interp_lower = np.interp(common_x, lower_points[:, 0], lower_points[:, 1])
    thickness = np.mean(y_interp_lower - y_interp_upper)

    if np.sin(np.deg2rad(pennation_angle)) == 0:
        fascicle_length = float('inf')
    else:
        fascicle_length = thickness / np.sin(np.deg2rad(pennation_angle))

    results = {
        "thickness": thickness,
        "pennation_angle": pennation_angle,
        "fascicle_length": fascicle_length,
        "fascicle_angle_alpha": alpha,
        "aponeurosis_angle_beta": beta,
    }

    output_mask = np.zeros_like(img_cropped, dtype=np.uint8)
    cv2.polylines(output_mask, [upper_points.astype(np.int32)], isClosed=False, color=255, thickness=2)
    cv2.polylines(output_mask, [lower_points.astype(np.int32)], isClosed=False, color=255, thickness=2)

    return results, output_mask

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

def find_aponeurosis_line(binary_mask, search_from_top=True, search_height_ratio=0.4):
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
