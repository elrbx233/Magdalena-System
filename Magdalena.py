import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QInputDialog, QMessageBox, QLineEdit,
    QGraphicsDropShadowEffect, QDialog, QStyledItemDelegate, QComboBox
)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QThread, pyqtSignal

#Sistema para Magdalena por Juan Vizhñay

class GuardarDatosThread(QThread):
    progreso = pyqtSignal(str)  #Señal para informar el progreso

    def __init__(self, hotel):
        super().__init__()
        self.hotel = hotel

    def run(self):
        try:
            Habitacion.guardar_datos(self.hotel)
            self.progreso.emit("✅ Datos guardados correctamente.")
        except Exception as e:
            self.progreso.emit(f"⚠ Error al guardar los datos: {e}")

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión - MAGDALENA SYSTEM")
        self.setGeometry(400, 200, 500, 400)  #Tamaño de la ventana de login
        self.setStyleSheet("background-color: #000000;")  #Fondo oscuro

        layout = QVBoxLayout()

        # Imagen del logo
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap(resource_path("logo.png"))

        if self.logo_pixmap.isNull():  
            self.logo_label.setText("⚠ No se encontró el logo")  
            self.logo_label.setStyleSheet("color: red; font-size: 14px;")
        else:  
            self.logo_label.setPixmap(self.logo_pixmap)  
            self.logo_label.setScaledContents(True)  #Ajustar la imagen al tamaño del QLabel  
            self.logo_label.setFixedSize(365, 200)  #Tamaño del logo  

        #Crear un layout horizontal para centrar el logo
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()  #Espacio flexible a la izquierda
        logo_layout.addWidget(self.logo_label)  #Agrega la imagen en el centro
        logo_layout.addStretch()  #Espacio flexible a la derecha

        #Añadir el layout del logo al layout principal
        layout.addLayout(logo_layout)

        #Campo de usuario
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setStyleSheet("background-color: #3A3A3A; color: white; padding: 5px; border-radius: 10px;")
        layout.addWidget(self.username_input)

        #Campo de contraseña
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)  # Ocultar contraseña
        self.password_input.setStyleSheet("background-color: #3A3A3A; color: white; padding: 5px; border-radius: 10px;")
        layout.addWidget(self.password_input)

        #Botón de inicio de sesión
        self.login_button = QPushButton("Ingresar")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #C69C6D;
                color: black;
                font-weight: bold;
                border: 3px solid black;
                border-radius: 13px;
                padding: 8px;
                transition: all 0.3s ease-in-out;
            }
            QPushButton:hover {
                background-color: #D8A878;
                border: 4px solid black;
                padding: 7px;
            }
            QPushButton:pressed {
                background-color: #B88B5A;
                border: 5px solid black;
                padding: 6px;
            }
        """)
        self.login_button.clicked.connect(self.verificar_credenciales)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def verificar_credenciales(self):
        usuario_correcto = "admin"  #Cambia esto por el usuario real
        contrasena_correcta = "1234"  #Cambia esto por la contraseña real

        usuario_ingresado = self.username_input.text()
        contrasena_ingresada = self.password_input.text()

        if usuario_ingresado == usuario_correcto and contrasena_ingresada == contrasena_correcta:
            self.abrir_ventana_principal()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")

    def abrir_ventana_principal(self):
        self.close()  #Cerrar la ventana de login
        self.ventana_principal = HotelApp()
        self.ventana_principal.show()

class Habitacion:
    def __init__(self, numero, tipo, mensaje=""):
        self.numero = numero
        self.disponible = True
        self.tipo = tipo
        self.contador = 0
        self.mensaje = mensaje
        self.tiempo_ocupacion = None
        self.danada = False

    def ocupar(self, noches):
        if self.disponible:
            self.disponible = False
            self.contador = noches
            self.tiempo_ocupacion = datetime.now() + timedelta(hours=noches*24)
    
    def actualizar_disponibilidad(self):
        if self.danada or not self.tiempo_ocupacion:
            return  #No actualizar si la habitación está dañada o no tiene tiempo de ocupación

        if datetime.now() >= self.tiempo_ocupacion:
            self.disponible = True
            self.contador = 0
            self.tiempo_ocupacion = None
    
    def marcar_danada(self, motivo):
        self.disponible = False
        self.tipo = 4
        self.mensaje = motivo
        self.danada = True 
    
    def to_dict(self):
        return {
            "numero": self.numero,
            "disponible": self.disponible,
            "tipo": self.tipo,
            "contador": self.contador,
            "mensaje": self.mensaje,
            "tiempo_ocupacion": self.tiempo_ocupacion.isoformat() if self.tiempo_ocupacion else None,
            "danada": self.danada  #Se agrega esta clave
        }

    @staticmethod
    def guardar_datos(hotel):
        def save_to_file(filename):
            with open(resource_path(filename), "w", encoding="utf-8") as file:
                json.dump(hotel, file, indent=4, sort_keys=True, ensure_ascii=False)

        try:
            save_to_file("hotel_data.json")  #Guardar datos principales
            save_to_file("hotel_data_backup.json")  #Guardar respaldo
            print("✅ Datos guardados y backup actualizado")
        except Exception as e:
            print(f"⚠ Error al guardar los datos: {e}")

    @staticmethod
    def cargar_datos():
        def load_from_file(filename):
            with open(resource_path(filename), "r", encoding="utf-8") as file:
                return json.load(file)

        try:
            datos = load_from_file("hotel_data.json")  #Intentar cargar datos principales
            if isinstance(datos, list):
                for piso in datos:
                    for habitacion in piso:
                        habitacion.setdefault("danada", False)
                        habitacion.setdefault("tiempo_ocupacion", None)
                return datos
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠ Error al cargar datos. Intentando cargar desde backup...")
            try:
                return load_from_file("hotel_data_backup.json")  #Intentar cargar desde respaldo
            except Exception as e:
                print(f"❌ Error al cargar backup: {e}")
        return []  #Devuelve una lista vacía si no se pudo cargar nada

class HotelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAGDALENA SYSTEM")
        self.setGeometry(100, 100, 800, 600)
        self.showMaximized()  #Iniciar en pantalla completa
        self.setStyleSheet("background-color: #000000;")
        self.aplicar_estilo_dialogos()
        self.hotel = Habitacion.cargar_datos()
        self.initUI()
        self.iniciar_actualizacion_automatica()
        self.iniciar_auto_guardado()

    def aplicar_estilo_dialogos(self):
        estilo = """
            QLabel { color: white; }
            QDialog { background-color: #000000; }
            QMessageBox { background-color: #000000; }
            QInputDialog { background-color: #000000; }
            QLineEdit { background-color: #000000; color: white; }
            QPushButton { background-color: #C69C6D; color: black; font-weight: bold; }
        """
        self.setStyleSheet(estilo + "QMainWindow { background-color: #000000; } QWidget { background-color: #000000; }")

    def initUI(self):
        layout = QVBoxLayout()
        
        # Crear el título con fondo negro
        self.label = QLabel("MAGDALENA SYSTEM")
        self.label.setFont(QFont("Lucida Calligraphy", 16, QFont.Bold))
        self.label.setStyleSheet("color: #C69C6D;")
        self.label.setAlignment(Qt.AlignCenter)

        titulo_container = QWidget()
        titulo_container.setStyleSheet("background-color: #000000;")  # Fondo negro
        titulo_layout = QVBoxLayout(titulo_container)
        titulo_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes
        titulo_layout.addWidget(self.label)

        layout.addWidget(titulo_container)  # Añadir el contenedor al layout principal
        
        self.table = QTableWidget()
        self.delegate = CustomDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Número", "Tipo", "Disponibilidad", "Tiempo restante (horas)", "Detalles"])
        self.table.cellDoubleClicked.connect(self.editar_celda)
        self.table.setStyleSheet("color: white; background-color: #000000;")
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #C69C6D; color: black; font-weight: bold; }")
        self.table.setColumnWidth(2, 230)  #Ajusta el ancho de la columna "Disponibildiad" a 300 píxeles
        self.table.setColumnWidth(3, 265)  #Tiempo restante 
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        self.load_data()

        # Crear los botones con fondo #0E0E0E
        botones_container = QWidget()
        botones_container.setStyleSheet("background-color: #0E0E0E;")  # Fondo oscuro
        botones_layout = QHBoxLayout(botones_container)
        botones_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes
        
        self.button_ocupar = QPushButton("Ocupar Habitación")
        self.button_ocupar.setStyleSheet("""
            QPushButton {
                background-color: #C69C6D;
                color: black;
                font-weight: bold;
                border: 3px solid black;  /* ⬅ Borde más grueso */
                border-radius: 13px;  /* ⬅ Bordes redondeados */
                padding: 8px;  /* ⬅ Espaciado interno */
                transition: all 0.3s ease-in-out;  /* ⬅ TRANSICIÓN SUAVE */
            }
            QPushButton:hover {
                background-color: #D8A878; /* ⬅ Cambio de color al pasar el mouse */
                border: 4px solid black;  /* ⬅ Borde más grueso al pasar el mouse */
                padding: 7px;  /* ⬅ Reduce el padding para simular el efecto de crecimiento */
            }
            QPushButton:pressed {
                background-color: #B88B5A;
                border: 5px solid black;
                padding: 6px;
            }
        """)
        self.button_ocupar.setFixedSize(240, 40)
        self.button_ocupar.clicked.connect(self.ingresar_persona)
        botones_layout.addWidget(self.button_ocupar)

        self.button_modificar = QPushButton("Modificar Habitación")
        self.button_modificar.setStyleSheet("""
            QPushButton {
                background-color: #C69C6D;
                color: black;
                font-weight: bold;
                border: 3px solid black;
                border-radius: 13px;
                padding: 8px;
                transition: all 0.3s ease-in-out;
            }
            QPushButton:hover {
                background-color: #D8A878;
                border: 4px solid black;
                padding: 7px;
            }
            QPushButton:pressed {
                background-color: #B88B5A;
                border: 5px solid black;
                padding: 6px;
            }
        """)
        self.button_modificar.setFixedSize(241, 40)
        self.button_modificar.clicked.connect(self.modificar_habitacion)
        botones_layout.addWidget(self.button_modificar)

        self.button_danada = QPushButton("Marcar Dañada")
        self.button_danada.setStyleSheet("""
            QPushButton {
                background-color: #C69C6D;
                color: black;
                font-weight: bold;
                border: 3px solid black;
                border-radius: 13px;
                padding: 8px;
                transition: all 0.3s ease-in-out;  /* ⬅ TRANSICIÓN SUAVE */
            }
            QPushButton:hover {
                background-color: #D8A878;
                border: 4px solid black;
                padding: 7px;
            }
            QPushButton:pressed {
                background-color: #B88B5A;
                border: 5px solid black;
                padding: 6px;
            }
        """)
        self.button_danada.setFixedSize(240,40)
        self.button_danada.clicked.connect(self.marcar_danada)
        botones_layout.addWidget(self.button_danada)
        
        self.button_refresh = QPushButton("Actualizar")
        self.button_refresh.setStyleSheet("""
            QPushButton {
                background-color: #C69C6D;
                color: black;
                font-weight: bold;
                border: 3px solid black;
                border-radius: 13px;
                padding: 8px;
                transition: all 0.3s ease-in-out;  /* ⬅ TRANSICIÓN SUAVE */
            }
            QPushButton:hover {
                background-color: #D8A878;
                border: 4px solid black;
                padding: 7px;
            }
            QPushButton:pressed {
                background-color: #B88B5A;
                border: 5px solid black;
                padding: 6px;
            }
        """)
        self.button_refresh.setFixedSize(240,40)
        self.button_refresh.clicked.connect(self.load_data)
        botones_layout.addWidget(self.button_refresh)

        def create_shadow():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(25)  #Aumenta el difuminado para más realismo
            shadow.setXOffset(6)  #Desplazamiento horizontal
            shadow.setYOffset(6)  #Desplazamiento vertical
            shadow.setColor(QColor(0, 0, 0, 150))  #Color de la sombra mas sofisticada
            return shadow

        # Aplicar la nueva sombra a cada botón
        self.button_ocupar.setGraphicsEffect(create_shadow())
        self.button_danada.setGraphicsEffect(create_shadow())
        self.button_refresh.setGraphicsEffect(create_shadow())

        layout.addWidget(botones_container)  # Añadir el contenedor al layout principal
        
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #2D2D2D;")
        self.setCentralWidget(container)
    
    def load_data(self):
        self.hotel = Habitacion.cargar_datos()  #Recarga el JSON
        self.actualizar_tabla()  #Llama a actualizar la tabla
 
    def ingresar_persona(self):
        num, ok = custom_getText(self, "Ingresar Persona", "Número de habitación:")
        if not ok or not num.isdigit():
            return

        noches, ok = custom_getText(self, "Tiempo de estancia", "Número de noches:")
        if not ok or not noches.isdigit():
            return

        for piso in self.hotel:
            for habitacion in piso:
                if habitacion["numero"] == int(num):
                    habitacion["disponible"] = False
                    habitacion["contador"] = int(noches)
                    habitacion["tiempo_ocupacion"] = (datetime.now() + timedelta(hours=int(noches)*24)).isoformat()
                    Habitacion.guardar_datos(self.hotel)
                    self.load_data()

                    msg_box = QMessageBox(self)
                    msg_box.setStyleSheet("""
                        QLabel { color: white; }
                        QMessageBox { background-color: #000000; }
                        QPushButton { background-color: #C69C6D; color: black; font-weight: bold; }
                    """)
                    msg_box.setWindowTitle("Éxito")
                    msg_box.setText(f"Habitación {num} ocupada por {noches} noches.")
                    msg_box.exec_()
                    return

    def modificar_habitacion(self):
        num, ok = custom_getText(self, "Modificar Habitación", "Número de habitación:")
        if not ok or not num.isdigit():
            return

        num = int(num)
        for piso in self.hotel:
            for habitacion in piso:
                if habitacion["numero"] == num:
                    #Guardar copia de seguridad en caso de cancelación
                    habitacion_original = habitacion.copy()

                    #Cambiar Tipo de Habitación
                    tipo_habitacion = {
                        1: "Simple", 2: "Doble", 3: "Matrimonial", 4: "Suite",
                        5: "Familiar", 6: "Presidencial", 7: "Penthouse"
                    }
                    tipos_lista = list(tipo_habitacion.values())
                    tipo_actual = tipo_habitacion.get(habitacion["tipo"], tipos_lista[0])  
                    nuevo_tipo, ok = custom_getItem(self, "Modificar Tipo", "Seleccione el nuevo tipo:", tipos_lista, tipos_lista.index(tipo_actual))
                    if not ok:
                        habitacion.update(habitacion_original)
                        return
                    habitacion["tipo"] = list(tipo_habitacion.keys())[list(tipo_habitacion.values()).index(nuevo_tipo)]

                    #Cambiar Disponibilidad
                    opciones_disponibilidad = ["Disponible", "Ocupada"]
                    estado_actual = "Disponible" if habitacion["disponible"] else "Ocupada"
                    nueva_disp, ok = custom_getItem(self, "Modificar Disponibilidad", "Seleccione la nueva disponibilidad:", opciones_disponibilidad, opciones_disponibilidad.index(estado_actual))
                    if not ok:
                        habitacion.update(habitacion_original)
                        return
                    habitacion["disponible"] = (nueva_disp == "Disponible")

                    #Si se cambia a "Disponible", resetear el contador
                    if habitacion["disponible"]:
                        habitacion["contador"] = 0
                        habitacion["tiempo_ocupacion"] = None

                    #Cambiar Contador (Tiempo de ocupación)
                    nuevo_contador, ok = custom_getInt(self, "Modificar Contador", "Ingrese el nuevo tiempo de ocupación en horas:", habitacion["contador"], 0, 9999)
                    if not ok:
                        habitacion.update(habitacion_original)
                        return
                    habitacion["contador"] = nuevo_contador
                    habitacion["tiempo_ocupacion"] = (datetime.now() + timedelta(hours=nuevo_contador)).isoformat()

                    #Cambiar Mensaje de Detalles
                    nuevo_mensaje, ok = custom_getText(self, "Modificar Mensaje", "Ingrese el nuevo mensaje:", habitacion["mensaje"])
                    if not ok:
                        habitacion.update(habitacion_original)
                        return
                    habitacion["mensaje"] = nuevo_mensaje

                    #Guardar cambios solo si el usuario no canceló
                    Habitacion.guardar_datos(self.hotel)
                    self.load_data()
                    msg_box = QMessageBox(self)
                    msg_box.setStyleSheet("""
                        QLabel { color: white; }
                        QMessageBox { background-color: #000000; }
                        QPushButton { background-color: #C69C6D; color: black; font-weight: bold; }
                    """)
                    msg_box.setWindowTitle("Éxito")
                    msg_box.setText(f"Habitación {num} modificada correctamente.")
                    msg_box.exec_()
                    return

        QMessageBox.warning(self, "Error", "Número de habitación no encontrado.")

    def marcar_danada(self):
        num, ok = custom_getText(self, "Marcar como dañada", "Número de habitación:")
        if not ok or not num.isdigit():
            return

        motivo, ok = custom_getText(self, "Motivo", "Ingrese el motivo de la avería:")
        if not ok or not motivo.strip():  #Evita guardar motivo vacío
            return

        for piso in self.hotel:
            for habitacion in piso:
                if habitacion["numero"] == int(num):
                    habitacion["disponible"] = False
                    habitacion["tipo"] = 4
                    habitacion["mensaje"] = motivo.strip()  #Quitar espacios extra
                    habitacion["danada"] = True
                    Habitacion.guardar_datos(self.hotel)
                    self.load_data()

                    msg_box = QMessageBox(self)
                    msg_box.setStyleSheet("""
                        QLabel { color: white; }
                        QMessageBox { background-color: #000000; }
                        QPushButton { background-color: #C69C6D; color: black; font-weight: bold; }
                    """)
                    msg_box.setWindowTitle("Éxito")
                    msg_box.setText(f"Habitación {num} marcada como dañada: {motivo}")
                    msg_box.exec_()
                    return
                
    def iniciar_actualizacion_automatica(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tabla)
        self.timer.start(1000)  #Actualiza cada segundo

    def actualizar_tabla(self):
        self.table.setRowCount(0)
        tipo_habitacion = {
            1: "Simple",
            2: "Doble",
            3: "Matrimonial",
            4: "Minisuite",
            5: "Suite",
            6: "Lavanderia"
        }

        cambios = False

        for piso in self.hotel:
            for habitacion in piso:

                 #✅Comprobar si el tiempo ya venció y actualizar disponibilidad
                if not habitacion["danada"] and not habitacion["disponible"]:
                    if habitacion["tiempo_ocupacion"]:
                        tiempo_ocupacion = datetime.fromisoformat(habitacion["tiempo_ocupacion"])
                        if datetime.now() >= tiempo_ocupacion:
                            habitacion["disponible"] = True
                            habitacion["contador"] = 0
                            habitacion["tiempo_ocupacion"] = None
                            cambios = True

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(habitacion["numero"])))
                self.table.setItem(row, 1, QTableWidgetItem(tipo_habitacion.get(habitacion["tipo"], "Desconocido")))
                if habitacion["danada"]:
                    estado = "⚠ Dañada"
                elif habitacion["disponible"]:
                    estado = "🟢 Disponible"
                else:
                    estado = "🔴 Ocupada"

                self.table.setItem(row, 2, QTableWidgetItem(estado))
                if not habitacion["disponible"] and not habitacion["danada"] and habitacion["tiempo_ocupacion"]:
                    tiempo_ocupacion = datetime.fromisoformat(habitacion["tiempo_ocupacion"])
                    diferencia = tiempo_ocupacion - datetime.now()
                    if diferencia.total_seconds() > 0:
                        horas, resto = divmod(int(diferencia.total_seconds()), 3600)
                        minutos, segundos = divmod(resto, 60)
                        tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                    else:
                        tiempo_formateado = "00:00:00"
                else:
                    tiempo_formateado = "00:00:00"
                self.table.setItem(row, 3, QTableWidgetItem(tiempo_formateado))
                self.table.setItem(row, 4, QTableWidgetItem(habitacion["mensaje"]))
        if cambios:
            Habitacion.guardar_datos(self.hotel)

    def iniciar_auto_guardado(self):
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_guardar_datos)
        self.auto_save_timer.start(300000)  # Cada 5 minutos (300000 ms)

    def auto_guardar_datos(self):
        self.thread_guardar = GuardarDatosThread(self.hotel)
        self.thread_guardar.progreso.connect(self.mostrar_mensaje_guardado)
        self.thread_guardar.start()

    def mostrar_mensaje_guardado(self, mensaje):
        print(mensaje)  #Mostrar el mensaje en la consola o en un log

    def editar_celda(self, row, column):
        print(f"[DEBUG] Doble clic detectado en fila {row}, columna {column}")

        # Obtener el número de la habitación seleccionada
        try:
            habitacion_numero = int(self.table.item(row, 0).text())
            print(f"[DEBUG] Número de habitación seleccionada: {habitacion_numero}")
        except Exception as e:
            print(f"[ERROR] No se pudo obtener el número de la habitación: {e}")
            return

        # Buscar la habitación en la estructura de datos
        habitacion_encontrada = None
        for piso in self.hotel:
            for habitacion in piso:
                if habitacion["numero"] == habitacion_numero:
                    habitacion_encontrada = habitacion
                    break
            if habitacion_encontrada:
                break

        if not habitacion_encontrada:
            print("[ERROR] Habitación no encontrada en la estructura de datos.")
            return

        print(f"[DEBUG] Habitación encontrada: {habitacion_encontrada}")

        if column == 2:  # Cambiar disponibilidad
            opciones = ["Disponible", "Ocupada"]
            texto_estado = self.table.item(row, column).text()
            estado_actual = "Disponible" if "Disponible" in texto_estado else "Ocupada"
            print(f"[DEBUG] Estado actual: {estado_actual}")

            nueva_disp, ok = custom_getItem(self, "Modificar Disponibilidad", "Seleccione la nueva disponibilidad:", opciones, opciones.index(estado_actual))
            if ok:
                print(f"[DEBUG] Nueva disponibilidad seleccionada: {nueva_disp}")
                if self.confirmar_cambios(f"¿Está seguro de cambiar la disponibilidad a '{nueva_disp}'?"):
                    habitacion_encontrada["disponible"] = (nueva_disp == "Disponible")
                    print(f"[DEBUG] Disponibilidad actualizada: {habitacion_encontrada['disponible']}")

                    if not habitacion_encontrada["disponible"]:
                        # Pide tiempo de ocupación en noches
                        dialog = QInputDialog(self)
                        dialog.setInputMode(QInputDialog.IntInput)
                        dialog.setIntValue(1)
                        dialog.setIntRange(1, 365)
                        dialog.setWindowTitle("Tiempo de ocupación")
                        dialog.setLabelText("Ingrese el tiempo de ocupación en noches:")

                        # Aplica el estilo al QDialog
                        dialog.setStyleSheet("""
                            * { font-size: 10pt; }
                            QLabel { color: white; }
                            QDialog { background-color: #000000; }
                            QPushButton { background-color: #C69C6D; color: black; font-weight: bold; }
                        """)

                        # Encuentra el campo de entrada y cámbiale el color de texto y fondo directamente:
                        line_edit = dialog.findChild(QLineEdit)
                        if line_edit:
                            line_edit.setStyleSheet("""
                                background-color: #3A3A3A;
                                font-size: 10pt;
                                color: white;
                                border-radius: 6px;
                                padding: 4px;
                                selection-background-color: #555555;
                                selection-color: white;
                            """)
                        ok = dialog.exec_()
                        if ok:
                            noches = dialog.intValue()
                            habitacion_encontrada["contador"] = noches
                            habitacion_encontrada["tiempo_ocupacion"] = (datetime.now() + timedelta(hours=noches * 24)).isoformat()
                            print(f"[DEBUG] Tiempo de ocupación actualizado: {habitacion_encontrada['tiempo_ocupacion']}")
                        else:
                            # Si el usuario cancela, revertir a disponible
                            habitacion_encontrada["disponible"] = True
                            habitacion_encontrada["contador"] = 0
                            habitacion_encontrada["tiempo_ocupacion"] = None
                            print("[DEBUG] Operación cancelada, disponibilidad revertida a 'Disponible'")

                    else:
                        # Si pasa a disponible, resetear
                        habitacion_encontrada["contador"] = 0
                        habitacion_encontrada["tiempo_ocupacion"] = None
                        print("[DEBUG] Habitación marcada como 'Disponible'")

                    # Guardar los cambios inmediatamente
                    Habitacion.guardar_datos(self.hotel)
                    self.actualizar_tabla()  # Asegurarse de que la tabla se actualice
                    print("[DEBUG] Cambios guardados y tabla actualizada")
                    return  # Salir después de aplicar los cambios

    def confirmar_cambios(self, texto):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar Cambios")
        msg_box.setText(texto)
        msg_box.setStyleSheet("""
            QLabel { color: white; }
            QMessageBox { background-color: #000000; }
            QPushButton {
                background-color: #C69C6D;
                font-size: 10pt;
                color: black;
                font-weight: bold;
                border: 2px solid black;
                border-radius: 10px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #D8A878;
            }
            QPushButton:pressed {
                background-color: #B88B5A;
            }
        """)
        continuar_button = msg_box.addButton("Continuar", QMessageBox.AcceptRole)
        cancelar_button = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
        msg_box.exec_()
        return msg_box.clickedButton() == continuar_button
    
def custom_getText(parent, title, label, default=""):
    dialog = QInputDialog(parent)
    dialog.setInputMode(QInputDialog.TextInput)
    dialog.setTextValue(default)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setFont(QFont("Lucida Sans", 10))
    dialog.setStyleSheet("""
        QLineEdit { background-color: #3A3A3A; color: white; border-radius: 6px; padding: 4px; font-size: 11pt; }
        QLabel { color: white; font-size: 11pt; }
        QDialog { background-color: #000000; }
        QPushButton {
            background-color: #C69C6D;
            color: black;
            font-weight: bold;
            font-size: 10pt;
            border-radius: 6px;
            padding: 4px;
            min-width: 100px;  /* Tamaño mínimo uniforme */
            min-height: 17px;  /* Altura mínima ajustada */
        }
        QPushButton:hover {
            background-color: #D8A878;
        }
        QPushButton:pressed {
            background-color: #B88B5A;
        }
    """)
    ok = dialog.exec_()
    return dialog.textValue(), ok == QDialog.Accepted

def custom_getInt(parent, title, label, value=0, min_value=0, max_value=9999):
    dialog = QInputDialog(parent)
    dialog.setInputMode(QInputDialog.IntInput)
    dialog.setIntValue(value)
    dialog.setIntRange(min_value, max_value)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setFont(QFont("Lucida Sans", 10))
    dialog.setStyleSheet("""
        QLineEdit { background-color: #3A3A3A; color: white; border-radius: 6px; padding: 4px; font-size: 11pt; }
        QLabel { color: white; font-size: 11pt; }
        QDialog { background-color: #000000; }
        QPushButton {
            background-color: #C69C6D;
            color: black;
            font-weight: bold;
            font-size: 10pt;
            border-radius: 6px;
            padding: 4px;
            min-width: 100px;  /* Tamaño mínimo uniforme */
            min-height: 17px;  /* Altura mínima ajustada */
        }
        QPushButton:hover {
            background-color: #D8A878;
        }
        QPushButton:pressed {
            background-color: #B88B5A;
        }
    """)
    ok = dialog.exec_()
    return dialog.intValue(), ok == QDialog.Accepted

def custom_getItem(parent, title, label, items, current=0):
    dialog = QInputDialog(parent)
    dialog.setComboBoxItems(items)
    dialog.setComboBoxEditable(False)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setFont(QFont("Lucida Sans", 10))
    dialog.setStyleSheet("""
        QDialog {
            background-color: #000000;  /* Fondo del diálogo */
        }
        QLabel {
            color: white;  /* Color del texto del título */
            font-size: 11pt;
        }
        QComboBox {
            background-color: #2D2D2D;  /* Fondo del cuadro de texto */
            color: white;  /* Color del texto en el cuadro */
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 4px;
        }
        QComboBox QAbstractItemView {
            background-color: #2D2D2D;  /* Fondo de las opciones desplegables */
            color: white;  /* Color del texto de las opciones */
            selection-background-color: #444444;  /* Fondo de la opción seleccionada */
            selection-color: white;  /* Color del texto de la opción seleccionada */
            border: 1px solid #444444;
        }
        QPushButton {
            background-color: #C69C6D;
            color: black;
            font-weight: bold;
            font-size: 10pt;
            border-radius: 6px;
            padding: 4px;
            min-width: 100px;  /* Tamaño mínimo uniforme */
            min-height: 17px;  /* Altura mínima ajustada */
        }
        QPushButton:hover {
            background-color: #D8A878;
        }
        QPushButton:pressed {
            background-color: #B88B5A;
        }
    """)

    # Forzar el estilo del menú desplegable
    combo_box = dialog.findChild(QComboBox)
    if combo_box:
        combo_box.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;  /* Fondo del cuadro de texto */
                color: white;  /* Color del texto en el cuadro */
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2D2D;  /* Fondo de las opciones desplegables */
                color: white;  /* Color del texto de las opciones */
                selection-background-color: #444444;  /* Fondo de la opción seleccionada */
                selection-color: white;  /* Color del texto de la opción seleccionada */
                border: 1px solid #444444;
            }
        """)

        # Forzar el estilo del QAbstractItemView
        view = combo_box.view()
        if view:
            view.setStyleSheet("""
                QListView {
                    background-color: #2D2D2D;  /* Fondo del menú desplegable */
                    color: white;  /* Color del texto de las opciones */
                    selection-background-color: #444444;  /* Fondo de la opción seleccionada */
                    selection-color: white;  /* Color del texto de la opción seleccionada */
                    border: 1px solid #444444;
                }
            """)

    ok = dialog.exec_()
    return dialog.textValue(), ok == QDialog.Accepted

def resource_path(relative_path):
    """Obtiene el path absoluto, funciona tanto en desarrollo como cuando es ejecutable."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class CustomDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setStyleSheet("""
            background-color: #3A3A3A;
            color: white;
            selection-background-color: #555555;
            selection-color: white;
            border-radius: 6px;
            padding: 4px;
        """)
        return editor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Lucida Sans, 12"))
    app.setStyleSheet("""
        * { font-size: 12pt; }
        QLineEdit { background-color: #2D2D2D; color: white; }
        QLabel { color: white; }
    """)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())