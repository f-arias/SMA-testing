import os
import cv2
import numpy as np
from skimage.filters import median
from skimage.morphology import disk
from skimage.feature import structure_tensor

def perform_cropping(image, cropping_type, manual_roi=None):
    """
    Realiza el recorte en una imagen basado en los parámetros de entrada.
    """
    H, W = image.shape[:2]

    if cropping_type == "Manual":
        if manual_roi:
            x, y, w, h = manual_roi
            Le = int(x + W * 0.005)
            Up = int(y + H * 0.01)
            width = int(w * 0.99)
            height = int(h * 0.98)
            return image[Up:Up+height, Le:Le+width]
        else:
            print("Advertencia: Recorte manual seleccionado pero no se proporcionó ROI.")
            return image
    else: # Recorte Automático
        if image.dtype != np.uint8:
            img_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        else:
            img_8bit = image

        blurred = cv2.GaussianBlur(img_8bit, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("Advertencia: No se encontraron contornos para el recorte automático.")
            return image

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        Le = int(x + w * 0.005)
        Up = int(y + h * 0.01)
        width = int(w * 0.98)
        height = int(h * 0.97)

        return image[Up:Up+height, Le:Le+width]

def process_single_image(image_path, params):
    """
    Procesa una única imagen.
    """
    print(f"Procesando imagen (v2.3.3): {image_path}")

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error al leer la imagen: {image_path}")
        return None, None

    img_cropped = perform_cropping(img, params["cropping"])

    kernel_size = 50
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    background = cv2.morphologyEx(img_cropped, cv2.MORPH_OPEN, kernel)
    img_no_bg = cv2.subtract(img_cropped, background)
    img_denoised = cv2.fastNlMeansDenoising(img_no_bg, h=15)

    if params.get("clahe_ap", False):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img_clahe = clahe.apply(img_denoised)
    else:
        img_clahe = img_denoised

    edges = cv2.Canny(image=img_clahe, threshold1=50, threshold2=150)
    WFoV = img_clahe.shape[1]
    minLength = params.get("apLength", 80) / 100.0 * WFoV
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_long_contours = np.zeros_like(edges)
    for contour in contours:
        if cv2.arcLength(contour, closed=False) >= minLength:
            cv2.drawContours(mask_long_contours, [contour], -1, 255, thickness=cv2.FILLED)

    upper_aponeurosis = find_aponeurosis_line(mask_long_contours, search_from_top=True)
    lower_aponeurosis = find_aponeurosis_line(mask_long_contours, search_from_top=False)

    vis_img = cv2.cvtColor(img_cropped, cv2.COLOR_GRAY2BGR)
    if upper_aponeurosis:
        points = np.array(upper_aponeurosis, dtype=np.int32)
        cv2.polylines(vis_img, [points], isClosed=False, color=(0, 255, 0), thickness=2)
    if lower_aponeurosis:
        points = np.array(lower_aponeurosis, dtype=np.int32)
        cv2.polylines(vis_img, [points], isClosed=False, color=(0, 0, 255), thickness=2)

    if upper_aponeurosis and lower_aponeurosis:
        upper_points = np.array(upper_aponeurosis)
        lower_points = np.array(lower_aponeurosis)
        upper_fit = np.polyfit(upper_points[:, 0], upper_points[:, 1], 1)
        lower_fit = np.polyfit(lower_points[:, 0], lower_points[:, 1], 1)
        beta_deep = np.rad2deg(np.arctan(lower_fit[0]))

        (h, w) = img_cropped.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, beta_deep, 1.0)

        upper_points_hom = np.hstack((upper_points, np.ones((upper_points.shape[0], 1))))
        upper_points_rotated = (rotation_matrix @ upper_points_hom.T).T
        lower_points_hom = np.hstack((lower_points, np.ones((lower_points.shape[0], 1))))
        lower_points_rotated = (rotation_matrix @ lower_points_hom.T).T

        y_min_roi = int(np.max(upper_points_rotated[:, 1]))
        y_max_roi = int(np.min(lower_points_rotated[:, 1]))
        x_min_roi = int(np.min(lower_points_rotated[:, 0]))
        x_max_roi = int(np.max(lower_points_rotated[:, 0]))

        roi_height_perc = params.get("ROIheight", 50) / 100.0
        roi_width_perc = params.get("ROIwidth", 60) / 100.0
        roi_h = int((y_max_roi - y_min_roi) * roi_height_perc)
        roi_w = int((x_max_roi - x_min_roi) * roi_width_perc)
        roi_y_start = y_min_roi + (y_max_roi - y_min_roi - roi_h) // 2
        roi_x_start = x_min_roi + (x_max_roi - x_min_roi - roi_w) // 2

        img_rotated = cv2.warpAffine(img_cropped, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        fascicle_roi = img_rotated[roi_y_start:roi_y_start+roi_h, roi_x_start:roi_x_start+roi_w]

        sigma_orientation = float(params.get("Osigma", 1.0))
        if sigma_orientation == 0: sigma_orientation = 0.1
        Axx, Axy, Ayy = structure_tensor(fascicle_roi, sigma=sigma_orientation, mode='constant')
        orientation_map = np.rad2deg(0.5 * np.arctan2(2 * Axy, Ayy - Axx))
        orientation_map += 90
        alpha_deep = np.nanmean(orientation_map)

        results = calculate_muscle_architecture(upper_points, lower_points, alpha_deep, beta_deep)

        theta_rad = np.deg2rad(alpha_deep + beta_deep)
        if np.sin(theta_rad) != 0:
            line_length = results["thickness"] / np.sin(theta_rad)
            mid_idx_lower = len(lower_points) // 2
            center_x = lower_points[mid_idx_lower, 0]
            center_y = lower_points[mid_idx_lower, 1]
            end_x = int(center_x - (line_length / 2) * np.cos(theta_rad))
            end_y = int(center_y - (line_length / 2) * np.sin(theta_rad))
            start_x = int(center_x + (line_length / 2) * np.cos(theta_rad))
            start_y = int(center_y + (line_length / 2) * np.sin(theta_rad))
            cv2.line(vis_img, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)

        return results, vis_img

    return None, None

def calculate_muscle_architecture(upper_aponeurosis_pts, lower_aponeurosis_pts, alpha, beta):
    """
    Calcula los parámetros de la arquitectura muscular.
    """
    x_coords_upper = upper_aponeurosis_pts[:, 0]
    y_coords_upper = upper_aponeurosis_pts[:, 1]
    x_coords_lower = lower_aponeurosis_pts[:, 0]
    y_coords_lower = lower_aponeurosis_pts[:, 1]

    common_x_min = max(np.min(x_coords_upper), np.min(x_coords_lower))
    common_x_max = min(np.max(x_coords_upper), np.max(x_coords_lower))
    num_points = int(common_x_max - common_x_min)
    if num_points <= 0: return {}
    common_x = np.linspace(common_x_min, common_x_max, num=num_points)

    y_interp_upper = np.interp(common_x, x_coords_upper, y_coords_upper)
    y_interp_lower = np.interp(common_x, x_coords_lower, y_coords_lower)
    thickness = np.mean(y_interp_lower - y_interp_upper)
    pennation_angle = alpha + beta

    if np.sin(np.deg2rad(pennation_angle)) == 0:
        fascicle_length = float('inf')
    else:
        fascicle_length = thickness / np.sin(np.deg2rad(pennation_angle))

    return {
        "thickness": thickness,
        "pennation_angle": pennation_angle,
        "fascicle_length": fascicle_length,
        "fascicle_angle_alpha": alpha,
        "aponeurosis_angle_beta": beta,
    }

def trace_line(image, start_x, y, direction, search_radius=2):
    """
    Traza una línea de píxeles brillantes desde un punto de inicio en una dirección.
    """
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

def find_aponeurosis_line(binary_mask, search_from_top=True, search_height_ratio=0.4):
    """
    Encuentra la línea de una aponeurosis (superior o inferior) en una máscara binaria.
    """
    height, width = binary_mask.shape
    mid_x = width // 2

    if search_from_top:
        search_region_y = (0, int(height * search_height_ratio))
    else:
        search_region_y = (int(height * (1 - search_height_ratio)), height)

    vertical_profile = binary_mask[search_region_y[0]:search_region_y[1], mid_x]
    potential_starts_y_offset = np.where(vertical_profile > 0)[0]
    if not potential_starts_y_offset.any():
        return None

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
