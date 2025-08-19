import tkinter as tk
from tkinter import ttk, filedialog

class SMAGUI171:
    """
    Esta clase crea la interfaz gráfica de usuario para la versión 1.7.1 de SMA.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("SMA v1.7.1 - Análisis de Arquitectura Muscular Simple")

        # Variables para almacenar los valores de los widgets
        self.flip = tk.BooleanVar(value=False)
        self.analysis = tk.StringVar(value="Image")
        self.param = tk.BooleanVar(value=True)
        self.inputDir = tk.StringVar()
        self.outputDir = tk.StringVar()
        self.extension = tk.StringVar(value=".tif")
        self.cropping = tk.StringVar(value="Automatic")
        self.Tsigma = tk.IntVar(value=10)
        self.extrapolate_from = tk.StringVar(value="100%")
        self.ROIn = tk.IntVar(value=3)
        self.ROIwidth = tk.IntVar(value=60)
        self.ROIheight = tk.IntVar(value=90)
        self.autThresh = tk.BooleanVar(value=True)
        self.manThresh = tk.IntVar(value=175)
        self.Osigma = tk.StringVar(value="4")
        self.Pa = tk.StringVar(value="max")
        self.scaling = tk.BooleanVar(value=False)
        self.depth = tk.IntVar(value=5)
        self.inputFile = tk.StringVar() # Para análisis de imagen única

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Frame de Configuración General ---
        general_frame = ttk.LabelFrame(main_frame, text="Configuración General", padding="10")
        general_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Checkbutton(general_frame, text="Voltear imagen horizontalmente", variable=self.flip).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(general_frame, text="Imprimir parámetros de análisis", variable=self.param).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(general_frame, text="Medidas escaladas", variable=self.scaling, command=self.toggle_scaling_depth).grid(row=2, column=0, sticky=tk.W)

        self.depth_label = ttk.Label(general_frame, text="Profundidad de escaneo (cm):")
        self.depth_scale = ttk.Scale(general_frame, from_=3, to=7, variable=self.depth, orient=tk.HORIZONTAL)
        self.depth_value_label = ttk.Label(general_frame, textvariable=self.depth)

        # --- Frame de Análisis ---
        analysis_frame = ttk.LabelFrame(main_frame, text="Tipo de Análisis", padding="10")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(analysis_frame, text="Imagen Única", variable=self.analysis, value="Image", command=self.update_analysis_options).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(analysis_frame, text="Carpeta", variable=self.analysis, value="Folder", command=self.update_analysis_options).grid(row=0, column=1, sticky=tk.W)

        self.file_frame = ttk.Frame(analysis_frame)
        self.file_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.input_file_label = ttk.Label(self.file_frame, text="Archivo de entrada:")
        self.input_file_entry = ttk.Entry(self.file_frame, textvariable=self.inputFile, width=40)
        self.input_file_button = ttk.Button(self.file_frame, text="...", command=self.browse_file, width=3)

        self.folder_frame = ttk.Frame(analysis_frame)
        self.folder_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.input_dir_label = ttk.Label(self.folder_frame, text="Directorio de entrada:")
        self.input_dir_entry = ttk.Entry(self.folder_frame, textvariable=self.inputDir, width=40)
        self.input_dir_button = ttk.Button(self.folder_frame, text="...", command=self.browse_input_dir, width=3)
        self.output_dir_label = ttk.Label(self.folder_frame, text="Directorio de salida:")
        self.output_dir_entry = ttk.Entry(self.folder_frame, textvariable=self.outputDir, width=40)
        self.output_dir_button = ttk.Button(self.folder_frame, text="...", command=self.browse_output_dir, width=3)
        self.ext_label = ttk.Label(self.folder_frame, text="Extensión:")
        self.ext_combo = ttk.Combobox(self.folder_frame, textvariable=self.extension, values=[".bmp", ".BMP", ".jpg", ".tif", ".png"], width=8)

        # --- Frame de Parámetros de Análisis ---
        params_frame = ttk.LabelFrame(main_frame, text="Parámetros de Análisis", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(params_frame, text="Recorte:").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(params_frame, text="Automático", variable=self.cropping, value="Automatic").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(params_frame, text="Manual", variable=self.cropping, value="Manual").grid(row=0, column=2, sticky=tk.W)

        ttk.Label(params_frame, text="Sigma de Tubeness:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.Tsigma, width=5).grid(row=1, column=1)

        ttk.Label(params_frame, text="Extrapolar desde:").grid(row=2, column=0, sticky=tk.W)
        ttk.Combobox(params_frame, textvariable=self.extrapolate_from, values=["100%", "50%"], width=8).grid(row=2, column=1)

        ttk.Label(params_frame, text="Número de ROIs:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.ROIn, width=5).grid(row=3, column=1)

        ttk.Label(params_frame, text="Ancho de ROI (%):").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.ROIwidth, width=5).grid(row=4, column=1)

        ttk.Label(params_frame, text="Alto de ROI (%):").grid(row=5, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.ROIheight, width=5).grid(row=5, column=1)

        ttk.Checkbutton(params_frame, text="Umbral automático", variable=self.autThresh, command=self.toggle_manual_thresh).grid(row=6, column=0, sticky=tk.W)
        self.man_thresh_label = ttk.Label(params_frame, text="Umbral manual:")
        self.man_thresh_entry = ttk.Entry(params_frame, textvariable=self.manThresh, width=5)

        ttk.Label(params_frame, text="LoG (sigma):").grid(row=7, column=0, sticky=tk.W)
        ttk.Combobox(params_frame, textvariable=self.Osigma, values=["0", "1", "2", "3", "4", "5", "6", "7", "Test"], width=8).grid(row=7, column=1)

        ttk.Label(params_frame, text="Método Orientación Principal:").grid(row=8, column=0, sticky=tk.W)
        ttk.Combobox(params_frame, textvariable=self.Pa, values=["max", "median", "mean (not recommended)"], width=25).grid(row=8, column=1, columnspan=2)

        # --- Botones de Acción ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=3, column=0, columnspan=2, sticky=tk.E)
        ttk.Button(action_frame, text="Ejecutar Análisis", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.root.quit).pack(side=tk.LEFT)

        self.update_analysis_options()
        self.toggle_manual_thresh()
        self.toggle_scaling_depth()

    def toggle_scaling_depth(self):
        if self.scaling.get():
            self.depth_label.grid(row=3, column=0, sticky=tk.W)
            self.depth_scale.grid(row=3, column=1, sticky=tk.W+tk.E)
            self.depth_value_label.grid(row=3, column=2)
        else:
            self.depth_label.grid_remove()
            self.depth_scale.grid_remove()
            self.depth_value_label.grid_remove()

    def toggle_manual_thresh(self):
        if self.autThresh.get():
            self.man_thresh_label.grid_remove()
            self.man_thresh_entry.grid_remove()
        else:
            self.man_thresh_label.grid(row=6, column=1, sticky=tk.W)
            self.man_thresh_entry.grid(row=6, column=2)

    def update_analysis_options(self):
        if self.analysis.get() == "Image":
            self.folder_frame.grid_remove()
            self.input_file_label.grid(row=0, column=0)
            self.input_file_entry.grid(row=0, column=1)
            self.input_file_button.grid(row=0, column=2)
        else: # Folder
            self.input_file_label.grid_remove()
            self.input_file_entry.grid_remove()
            self.input_file_button.grid_remove()
            self.folder_frame.grid()
            self.input_dir_label.grid(row=0, column=0)
            self.input_dir_entry.grid(row=0, column=1)
            self.input_dir_button.grid(row=0, column=2)
            self.output_dir_label.grid(row=1, column=0)
            self.output_dir_entry.grid(row=1, column=1)
            self.output_dir_button.grid(row=1, column=2)
            self.ext_label.grid(row=2, column=0)
            self.ext_combo.grid(row=2, column=1)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.inputFile.set(filename)

    def browse_input_dir(self):
        self.inputDir.set(filedialog.askdirectory())

    def browse_output_dir(self):
        self.outputDir.set(filedialog.askdirectory())

    def set_run_analysis_callback(self, callback):
        self.run_analysis_callback = callback

    def get_params(self):
        return {k: v.get() for k, v in self.__dict__.items() if isinstance(v, tk.Variable)}

    def run_analysis(self):
        if hasattr(self, 'run_analysis_callback') and self.run_analysis_callback:
            self.run_analysis_callback(self.get_params())
        self.root.quit()
