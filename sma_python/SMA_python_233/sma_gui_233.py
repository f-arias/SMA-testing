import tkinter as tk
from tkinter import ttk, filedialog

class SMAGUI:
    """
    Esta clase crea la interfaz gráfica de usuario para el análisis de arquitectura muscular simple (SMA).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("SMA v2.3.3 - Análisis de Arquitectura Muscular Simple")

        # Variables para almacenar los valores de los widgets
        self.flip = tk.BooleanVar(value=False)
        self.pano = tk.BooleanVar(value=False)
        self.geometry = tk.StringVar(value="Straight")
        self.analysis = tk.StringVar(value="Current file")
        self.cropping = tk.StringVar(value="Automatic (requires identical scan depth)")
        self.scaling = tk.StringVar(value="None")
        self.Tsigma = tk.IntVar(value=8)
        self.clahe_ap = tk.BooleanVar(value=False)
        self.apLength = tk.IntVar(value=80)
        self.extrapolate_from = tk.StringVar(value="100%")
        self.apo_test = tk.BooleanVar(value=False)
        self.ROIheight = tk.IntVar(value=50)
        self.ROIwidth = tk.IntVar(value=60)
        self.clahe_fasc = tk.BooleanVar(value=False)
        self.Osigma = tk.StringVar(value="1")
        self.param = tk.BooleanVar(value=True)
        self.disp_fasc = tk.BooleanVar(value=True)
        self.dev = tk.BooleanVar(value=False)
        self.pano_crop = tk.BooleanVar(value=False)
        self.inputFile = tk.StringVar()
        self.inputDir = tk.StringVar()
        self.outputDir = tk.StringVar()
        self.extension = tk.StringVar(value=".tif")

        self.create_widgets()

    def create_widgets(self):
        """
        Crea y organiza todos los widgets en la ventana principal.
        """
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Frame de Configuración General ---
        general_frame = ttk.LabelFrame(main_frame, text="Configuración General", padding="10")
        general_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Checkbutton(general_frame, text="Voltear imagen horizontalmente", variable=self.flip).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(general_frame, text="Escaneo panorámico", variable=self.pano).grid(row=1, column=0, sticky=tk.W)

        ttk.Label(general_frame, text="Modelo de fascículo:").grid(row=2, column=0, sticky=tk.W, pady=(10,0))
        ttk.Radiobutton(general_frame, text="Recto", variable=self.geometry, value="Straight").grid(row=3, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(general_frame, text="Curvo (spline)", variable=self.geometry, value="Curved_spline").grid(row=4, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(general_frame, text="Curvo (círculo)", variable=self.geometry, value="Curved_circle").grid(row=5, column=0, sticky=tk.W, padx=20)

        # --- Frame de Análisis y Recorte ---
        analysis_frame = ttk.LabelFrame(main_frame, text="Análisis y Recorte", padding="10")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(analysis_frame, text="Tipo de análisis:").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(analysis_frame, text="Archivo actual", variable=self.analysis, value="Current file", command=self.update_analysis_options).grid(row=1, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(analysis_frame, text="Abrir archivo", variable=self.analysis, value="Open file", command=self.update_analysis_options).grid(row=2, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(analysis_frame, text="Abrir carpeta", variable=self.analysis, value="Open folder", command=self.update_analysis_options).grid(row=3, column=0, sticky=tk.W, padx=20)

        self.file_frame = ttk.Frame(analysis_frame)
        self.file_frame.grid(row=1, column=1, rowspan=3, sticky=tk.W, padx=10)
        self.input_file_label = ttk.Label(self.file_frame, text="Archivo de entrada:")
        self.input_file_entry = ttk.Entry(self.file_frame, textvariable=self.inputFile, width=40)
        self.input_file_button = ttk.Button(self.file_frame, text="...", command=self.browse_file, width=3)

        self.folder_frame = ttk.Frame(analysis_frame)
        self.folder_frame.grid(row=1, column=1, rowspan=3, sticky=tk.W, padx=10)
        self.input_dir_label = ttk.Label(self.folder_frame, text="Directorio de entrada:")
        self.input_dir_entry = ttk.Entry(self.folder_frame, textvariable=self.inputDir, width=40)
        self.input_dir_button = ttk.Button(self.folder_frame, text="...", command=self.browse_input_dir, width=3)
        self.output_dir_label = ttk.Label(self.folder_frame, text="Directorio de salida:")
        self.output_dir_entry = ttk.Entry(self.folder_frame, textvariable=self.outputDir, width=40)
        self.output_dir_button = ttk.Button(self.folder_frame, text="...", command=self.browse_output_dir, width=3)
        self.ext_label = ttk.Label(self.folder_frame, text="Extensión de archivo:")
        self.ext_combo = ttk.Combobox(self.folder_frame, textvariable=self.extension, values=[".bmp", ".BMP", ".jpg", ".tif", ".png", ".dcm", ""])

        ttk.Label(analysis_frame, text="Recorte de imagen:").grid(row=4, column=0, sticky=tk.W, pady=(10,0))
        ttk.Radiobutton(analysis_frame, text="Automático", variable=self.cropping, value="Automatic (requires identical scan depth)").grid(row=5, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(analysis_frame, text="Manual", variable=self.cropping, value="Manual").grid(row=6, column=0, sticky=tk.W, padx=20)

        ttk.Label(analysis_frame, text="Escalado de píxeles:").grid(row=7, column=0, sticky=tk.W, pady=(10,0))
        ttk.Radiobutton(analysis_frame, text="Ninguno", variable=self.scaling, value="None").grid(row=8, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(analysis_frame, text="Automático (requiere metadatos)", variable=self.scaling, value="Automatic (requires metadata)").grid(row=9, column=0, sticky=tk.W, padx=20)
        ttk.Radiobutton(analysis_frame, text="Manual", variable=self.scaling, value="Manual").grid(row=10, column=0, sticky=tk.W, padx=20)

        # --- Frame de Aponeurosis ---
        apo_frame = ttk.LabelFrame(main_frame, text="Aponeurosis", padding="10")
        apo_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N), pady=5, padx=5)

        ttk.Label(apo_frame, text="Sigma de Tubeness:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(apo_frame, from_=2, to=14, variable=self.Tsigma, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=tk.W+tk.E)
        ttk.Label(apo_frame, textvariable=self.Tsigma).grid(row=0, column=2)

        ttk.Checkbutton(apo_frame, text="Mejorar filtro de aponeurosis (CLAHE)", variable=self.clahe_ap).grid(row=1, column=0, columnspan=3, sticky=tk.W)

        ttk.Label(apo_frame, text="Longitud (% de FoV):").grid(row=2, column=0, sticky=tk.W)
        ttk.Scale(apo_frame, from_=40, to=95, variable=self.apLength, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=tk.W+tk.E)
        ttk.Label(apo_frame, textvariable=self.apLength).grid(row=2, column=2)

        ttk.Label(apo_frame, text="Extrapolar desde:").grid(row=3, column=0, sticky=tk.W)
        ttk.Combobox(apo_frame, textvariable=self.extrapolate_from, values=["100%", "50%"]).grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E)

        ttk.Checkbutton(apo_frame, text="Test de detección de aponeurosis", variable=self.apo_test).grid(row=4, column=0, columnspan=3, sticky=tk.W)

        # --- Frame de Fascículos ---
        fasc_frame = ttk.LabelFrame(main_frame, text="Fascículos", padding="10")
        fasc_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N), pady=5, padx=5)

        ttk.Label(fasc_frame, text="Altura de ROI (%):").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(fasc_frame, from_=40, to=90, variable=self.ROIheight, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=tk.W+tk.E)
        ttk.Label(fasc_frame, textvariable=self.ROIheight).grid(row=0, column=2)

        ttk.Label(fasc_frame, text="Ancho de ROI (%):").grid(row=1, column=0, sticky=tk.W)
        ttk.Scale(fasc_frame, from_=40, to=90, variable=self.ROIwidth, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.W+tk.E)
        ttk.Label(fasc_frame, textvariable=self.ROIwidth).grid(row=1, column=2)

        ttk.Checkbutton(fasc_frame, text="Mejorar filtro de fascículos (CLAHE)", variable=self.clahe_fasc).grid(row=2, column=0, columnspan=3, sticky=tk.W)

        ttk.Label(fasc_frame, text="Laplaciano de Gauss (sigma):").grid(row=3, column=0, sticky=tk.W)
        ttk.Combobox(fasc_frame, textvariable=self.Osigma, values=["0", "1", "2", "3", "4", "5", "6", "7"]).grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E)

        # --- Frame de Otros ---
        other_frame = ttk.LabelFrame(main_frame, text="Otros", padding="10")
        other_frame.grid(row=2, column=2, sticky=(tk.W, tk.E), pady=5, padx=5)

        ttk.Checkbutton(other_frame, text="Imprimir parámetros de análisis", variable=self.param).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(other_frame, text="Mostrar contorno de fascículos detectados", variable=self.disp_fasc).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(other_frame, text="Modo desarrollador", variable=self.dev).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(other_frame, text="Pre-recortar imagen panorámica", variable=self.pano_crop).grid(row=3, column=0, sticky=tk.W)

        # --- Botones de Acción ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=3, column=0, columnspan=3, sticky=tk.E)

        ttk.Button(action_frame, text="Ejecutar Análisis", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.root.quit).pack(side=tk.LEFT)

        self.update_analysis_options()

    def update_analysis_options(self):
        analysis_type = self.analysis.get()
        if analysis_type == "Open file":
            self.folder_frame.grid_remove()
            self.file_frame.grid()
            self.input_file_label.grid(row=0, column=0, sticky=tk.W)
            self.input_file_entry.grid(row=0, column=1, sticky=tk.W)
            self.input_file_button.grid(row=0, column=2, sticky=tk.W)
        elif analysis_type == "Open folder":
            self.file_frame.grid_remove()
            self.folder_frame.grid()
            self.input_dir_label.grid(row=0, column=0, sticky=tk.W)
            self.input_dir_entry.grid(row=0, column=1, sticky=tk.W)
            self.input_dir_button.grid(row=0, column=2, sticky=tk.W)
            self.output_dir_label.grid(row=1, column=0, sticky=tk.W)
            self.output_dir_entry.grid(row=1, column=1, sticky=tk.W)
            self.output_dir_button.grid(row=1, column=2, sticky=tk.W)
            self.ext_label.grid(row=2, column=0, sticky=tk.W)
            self.ext_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        else: # "Current file"
            self.file_frame.grid_remove()
            self.folder_frame.grid_remove()

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.inputFile.set(filename)

    def browse_input_dir(self):
        directory = filedialog.askdirectory()
        self.inputDir.set(directory)

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        self.outputDir.set(directory)

    def set_run_analysis_callback(self, callback):
        self.run_analysis_callback = callback

    def get_params(self):
        return {
            "flip": self.flip.get(),
            "pano": self.pano.get(),
            "geometry": self.geometry.get(),
            "analysis": self.analysis.get(),
            "inputFile": self.inputFile.get(),
            "inputDir": self.inputDir.get(),
            "outputDir": self.outputDir.get(),
            "extension": self.extension.get(),
            "cropping": self.cropping.get(),
            "scaling": self.scaling.get(),
            "Tsigma": self.Tsigma.get(),
            "clahe_ap": self.clahe_ap.get(),
            "apLength": self.apLength.get(),
            "extrapolate_from": self.extrapolate_from.get(),
            "apo_test": self.apo_test.get(),
            "ROIheight": self.ROIheight.get(),
            "ROIwidth": self.ROIwidth.get(),
            "clahe_fasc": self.clahe_fasc.get(),
            "Osigma": self.Osigma.get(),
            "param": self.param.get(),
            "disp_fasc": self.disp_fasc.get(),
            "dev": self.dev.get(),
            "pano_crop": self.pano_crop.get(),
        }

    def run_analysis(self):
        if self.run_analysis_callback:
            params = self.get_params()
            self.run_analysis_callback(params)
        self.root.quit()
