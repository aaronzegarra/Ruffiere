# Prueba de Ruffier - 3 pantallas (PyQt5) EN ESPAÑOL
# Requisitos: pip install PyQt5
# Ejecutar (con consola): python ruffier_app.py
# Sin consola (Windows): guardar como ruffier_app.pyw y doble clic

import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout,
    QMessageBox, QStackedWidget, QFrame
)


def a_entero(texto):
    try:
        return int(str(texto).strip())
    except Exception:
        return None


def ruffier_desde_15s(p0_15, p1_15, p2a_15, p2b_15):
    # Convertimos a latidos por minuto (x4).
    # Para P2 usamos el promedio de las dos mediciones de 15s (inicio y final del minuto).
    p0 = float(p0_15) * 4.0
    p1 = float(p1_15) * 4.0
    p2 = (float(p2a_15) + float(p2b_15)) / 2.0
    p2 = p2 * 4.0
    ir = (p0 + p1 + p2 - 200.0) / 10.0
    return ir, p0, p1, p2


def clasificar(ir):
    # Rangos típicos escolares (pueden variar según la tabla de tu profe)
    if ir < 0:
        return "Excelente"
    if ir <= 5:
        return "Muy buena"
    if ir <= 10:
        return "Buena"
    if ir <= 15:
        return "Regular"
    if ir <= 20:
        return "Débil"
    return "Muy débil"


def rendimiento_por_edad(edad, ir):
    # En tu ejemplo aparece: "no hay datos para esta edad"
    # Aquí ponemos ese mensaje si la edad está fuera del rango escolar común.
    if edad is None or edad < 7 or edad > 15:
        return "no hay datos para esta edad"
    return clasificar(ir)


class RelojGrande(QLabel):
    def __init__(self):
        super().__init__("00:00:00")
        f = QFont()
        f.setPointSize(32)
        f.setBold(True)
        self.setFont(f)
        self.setAlignment(Qt.AlignCenter)


class Pantalla1Bienvenida(QWidget):
    def __init__(self, al_iniciar):
        super().__init__()
        self.al_iniciar = al_iniciar

        titulo = QLabel("¡Bienvenido(a) al programa de detección del estado de salud!")
        fuente_t = QFont()
        fuente_t.setPointSize(12)
        fuente_t.setBold(True)
        titulo.setFont(fuente_t)

        info = QLabel(
            "Esta aplicación te permite usar la Prueba de Ruffier para obtener una evaluación inicial "
            "de tu condición cardíaca durante el esfuerzo físico.\n\n"
            "Procedimiento:\n"
            "1) Recuéstate (boca arriba) y descansa 5 minutos. Mide tu pulso durante 15 segundos (P0).\n"
            "2) Realiza 30 sentadillas en 45 segundos.\n"
            "3) Al terminar, recuéstate y mide tu pulso:\n"
            "   - Primeros 15 segundos del minuto de recuperación (P1).\n"
            "   - Últimos 15 segundos del mismo minuto (P2).\n\n"
            "Importante: si te sientes mal (mareos, náuseas, falta de aire, etc.), "
            "detén la prueba y consulta a un profesional de salud."
        )
        info.setWordWrap(True)

        btn = QPushButton("Iniciar")
        btn.setFixedWidth(140)
        btn.clicked.connect(self.al_iniciar)

        root = QVBoxLayout()
        root.addSpacing(10)
        root.addWidget(titulo)
        root.addSpacing(10)
        root.addWidget(info)
        root.addStretch(1)

        fila_btn = QHBoxLayout()
        fila_btn.addStretch(1)
        fila_btn.addWidget(btn)
        fila_btn.addStretch(1)
        root.addLayout(fila_btn)

        root.addSpacing(10)
        self.setLayout(root)


class Pantalla2Prueba(QWidget):
    def __init__(self, al_enviar_resultados):
        super().__init__()
        self.al_enviar_resultados = al_enviar_resultados

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.restante = 0
        self.fase = ""  # "p0", "sentadillas", "p1p2"
        self.timer.timeout.connect(self._tick)

        # Entradas
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")

        self.edad = QLineEdit()
        self.edad.setPlaceholderText("0")

        self.p0 = QLineEdit()
        self.p0.setPlaceholderText("0")

        self.p1 = QLineEdit()
        self.p1.setPlaceholderText("0")

        self.p2a = QLineEdit()
        self.p2a.setPlaceholderText("0")

        self.p2b = QLineEdit()
        self.p2b.setPlaceholderText("0")

        # Reloj grande (derecha)
        self.reloj = RelojGrande()

        # Botones
        self.btn_p0 = QPushButton("Iniciar medición P0 (15 s)")
        self.btn_sent = QPushButton("Iniciar sentadillas (45 s)")
        self.btn_final = QPushButton("Iniciar recuperación (60 s)")
        self.btn_enviar = QPushButton("Enviar resultados")

        self.btn_p0.clicked.connect(self.iniciar_p0)
        self.btn_sent.clicked.connect(self.iniciar_sentadillas)
        self.btn_final.clicked.connect(self.iniciar_recuperacion)
        self.btn_enviar.clicked.connect(self._enviar)

        # Layout izquierdo
        grid = QGridLayout()
        r = 0

        grid.addWidget(QLabel("Escribe tu nombre completo:"), r, 0, 1, 2); r += 1
        grid.addWidget(self.nombre, r, 0, 1, 2); r += 1

        grid.addWidget(QLabel("Edad (años):"), r, 0, 1, 2); r += 1
        grid.addWidget(self.edad, r, 0, 1, 2); r += 1

        grid.addWidget(QLabel(
            "Paso 1 (P0): Recuéstate y cuenta tus latidos por 15 segundos.\n"
            "Haz clic en el botón para iniciar el cronómetro y luego escribe el número."
        ), r, 0, 1, 2); r += 1

        grid.addWidget(self.btn_p0, r, 0, 1, 2); r += 1
        grid.addWidget(self.p0, r, 0, 1, 2); r += 1

        grid.addWidget(QLabel(
            "Paso 2: Realiza 30 sentadillas en 45 segundos.\n"
            "Haz clic para iniciar el contador."
        ), r, 0, 1, 2); r += 1

        grid.addWidget(self.btn_sent, r, 0, 1, 2); r += 1

        grid.addWidget(QLabel(
            "Paso 3 (Recuperación): Recuéstate y cuenta tus latidos:\n"
            "• P1: primeros 15 s del minuto.\n"
            "• P2: últimos 15 s del minuto.\n"
            "Haz clic para iniciar el minuto de recuperación y luego llena los campos."
        ), r, 0, 1, 2); r += 1

        grid.addWidget(self.btn_final, r, 0, 1, 2); r += 1
        grid.addWidget(QLabel("P1 (latidos en 15 s):"), r, 0); grid.addWidget(self.p1, r, 1); r += 1
        grid.addWidget(QLabel("P2 (primeros 15 s o última medición):"), r, 0); grid.addWidget(self.p2a, r, 1); r += 1
        grid.addWidget(QLabel("P2 (últimos 15 s):"), r, 0); grid.addWidget(self.p2b, r, 1); r += 1

        fila_enviar = QHBoxLayout()
        fila_enviar.addStretch(1)
        fila_enviar.addWidget(self.btn_enviar)
        fila_enviar.addStretch(1)

        izquierda = QVBoxLayout()
        izquierda.addLayout(grid)
        izquierda.addLayout(fila_enviar)

        derecha = QVBoxLayout()
        derecha.addStretch(1)
        derecha.addWidget(self.reloj)
        derecha.addStretch(1)

        root = QHBoxLayout()
        root.addLayout(izquierda, 3)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep)

        root.addLayout(derecha, 2)
        self.setLayout(root)

        self._set_reloj(0)

    def _set_reloj(self, sec):
        h = sec // 3600
        rem = sec % 3600
        m = rem // 60
        s = rem % 60
        self.reloj.setText("{:02d}:{:02d}:{:02d}".format(h, m, s))

    def _tick(self):
        self.restante -= 1
        self._set_reloj(self.restante)

        if self.restante <= 0:
            self.timer.stop()
            self._set_reloj(0)
            self._mensaje_fin_fase()
            self.fase = ""

    def _mensaje_fin_fase(self):
        if self.fase == "p0":
            QMessageBox.information(self, "Cronómetro", "Terminó P0. Escribe el número de latidos (15 s).")
        elif self.fase == "sentadillas":
            QMessageBox.information(self, "Cronómetro", "Terminó el tiempo de sentadillas. Prepárate para la recuperación.")
        elif self.fase == "p1p2":
            QMessageBox.information(self, "Cronómetro", "Terminó el minuto de recuperación. Llena P1 y P2.")

    def _iniciar(self, segundos, fase):
        if self.timer.isActive():
            self.timer.stop()
        self.restante = int(segundos)
        self.fase = fase
        self._set_reloj(self.restante)
        self.timer.start()

    def iniciar_p0(self):
        self._iniciar(15, "p0")

    def iniciar_sentadillas(self):
        self._iniciar(45, "sentadillas")

    def iniciar_recuperacion(self):
        self._iniciar(60, "p1p2")

    def _enviar(self):
        nom = str(self.nombre.text()).strip()
        edad = a_entero(self.edad.text())

        p0 = a_entero(self.p0.text())
        p1 = a_entero(self.p1.text())
        p2a = a_entero(self.p2a.text())
        p2b = a_entero(self.p2b.text())

        if nom == "":
            QMessageBox.warning(self, "Error", "Escribe tu nombre completo.")
            return
        if edad is None or edad <= 0:
            QMessageBox.warning(self, "Error", "Escribe una edad válida.")
            return

        valores = [p0, p1, p2a, p2b]
        for v in valores:
            if v is None or v <= 0:
                QMessageBox.warning(self, "Error", "Completa todos los pulsos con enteros mayores que 0.")
                return

        ir, p0_lpm, p1_lpm, p2_lpm = ruffier_desde_15s(p0, p1, p2a, p2b)
        rend = rendimiento_por_edad(edad, ir)

        datos = {
            "nombre": nom,
            "edad": edad,
            "p0_15": p0,
            "p1_15": p1,
            "p2a_15": p2a,
            "p2b_15": p2b,
            "p0_lpm": p0_lpm,
            "p1_lpm": p1_lpm,
            "p2_lpm": p2_lpm,
            "ir": ir,
            "rend": rend
        }

        self.al_enviar_resultados(datos)


class Pantalla3Resultados(QWidget):
    def __init__(self, al_reiniciar):
        super().__init__()
        self.al_reiniciar = al_reiniciar

        titulo = QLabel("Resultados")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        titulo.setFont(f)

        self.lbl_ir = QLabel("Índice de Ruffier: 0")
        self.lbl_rend = QLabel("Rendimiento cardíaco: no hay datos para esta edad")

        btn = QPushButton("Nueva prueba")
        btn.setFixedWidth(160)
        btn.clicked.connect(self.al_reiniciar)

        root = QVBoxLayout()
        root.addWidget(titulo)
        root.addSpacing(10)
        root.addWidget(self.lbl_ir)
        root.addSpacing(10)
        root.addWidget(self.lbl_rend)
        root.addStretch(1)

        fila = QHBoxLayout()
        fila.addStretch(1)
        fila.addWidget(btn)
        fila.addStretch(1)
        root.addLayout(fila)

        self.setLayout(root)

    def set_resultados(self, datos):
        ir = datos.get("ir", 0.0)
        rend = datos.get("rend", "no hay datos para esta edad")

        self.lbl_ir.setText("Índice de Ruffier: {:.2f}".format(ir))
        self.lbl_rend.setText("Rendimiento cardíaco: " + str(rend))


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Salud - Prueba de Ruffier")

        self.stack = QStackedWidget()

        self.p1 = Pantalla1Bienvenida(self.ir_a_p2)
        self.p2 = Pantalla2Prueba(self.ir_a_p3)
        self.p3 = Pantalla3Resultados(self.reiniciar)

        self.stack.addWidget(self.p1)  # 0
        self.stack.addWidget(self.p2)  # 1
        self.stack.addWidget(self.p3)  # 2

        self.setCentralWidget(self.stack)
        self.resize(1000, 600)

    def ir_a_p2(self):
        self.stack.setCurrentIndex(1)

    def ir_a_p3(self, datos):
        self.p3.set_resultados(datos)
        self.stack.setCurrentIndex(2)

    def reiniciar(self):
        self.stack.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)
    w = VentanaPrincipal()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


