import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QTabWidget, QHBoxLayout, QLineEdit,
    QGraphicsEllipseItem, QPushButton, QVBoxLayout, QWidget, QColorDialog, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QTimer, QRegExp
from PyQt5.QtGui import QColor, QBrush, QPainter, QIntValidator, QDoubleValidator, QRegExpValidator


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.scale(0.2, 0.2)  # Initial zoom level
        
        self._pan_active = False
        self._last_pan_point = None

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan_active = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._pan_active and self._last_pan_point is not None:
            # Calculate the difference
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            
            # Move the scrollbars (pan the view)
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan_active = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in = 1.2
        zoom_out = 1 / zoom_in
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)
        # Don't call super().wheelEvent(event) to prevent scrolling
            

class LEDViewer(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(-1500, -2000, 3000, 3500)

        # Create LEDs
        self.create_LEDs()

    def create_LEDs(self):
        self.leds = []
        index = 0
        with open("showBuilder/postions.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.split(',')
                
                x = float(line[0].strip())
                z = float(line[1].strip()) # We will refer to this as y now on since it makes more sense in a 2d space
                
                led = LEDItem(x*40, z*40, index)
                self.addItem(led)
                self.leds.append(led)

                index += 1


class LEDItem(QGraphicsEllipseItem):
    def __init__(self, x, y, index, size=10):
        super().__init__(-size/2, -size/2, size, size)
        self.setPos(x, y)
        self.index = index
        self.brush = QBrush(Qt.gray)
        self.setBrush(self.brush)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)

    def set_color(self, color: QColor):
        self.brush.setColor(color)
        self.setBrush(self.brush)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LED Mapper")
        self.resize(800, 800)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)

        # Timer for animation (placeholder)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_effect)
        self.timer.start(100)  # 10 fps
        self.frameNumber = 0

        # Scene & view
        self.scene = LEDViewer()
        self.view = CustomGraphicsView(self.scene)

        # Tabs
        tabs = QTabWidget()
        README_tab = QWidget()
        frame_tab = QWidget()
        color_tab = QWidget()

        tabs.addTab(README_tab, "README")
        tabs.addTab(frame_tab, "Frame")
        tabs.addTab(color_tab, "Color")

        # Buttons
        save_button = QPushButton("Save Frame")
        save_button.clicked.connect(self.save_frame)
        save_button.setFixedWidth(save_button.sizeHint().width())

        color_button = QPushButton("Color Selected LEDs")
        color_button.clicked.connect(self.set_selected_color)
        color_button.setFixedWidth(color_button.sizeHint().width())

        # Color selection widgets
        self.red_textBox, red_layout = self.create_rgb_slider("R")
        self.green_textBox, green_layout = self.create_rgb_slider("G")
        self.blue_textBox, blue_layout = self.create_rgb_slider("B")
        self.alpha_textBox, alpha_layout = self.create_rgb_slider("A", alpha=True)

        hex_label = QLabel("Hex Code: #")
        hex_label.setFixedWidth(hex_label.sizeHint().width())

        self.hex_textBox = QLineEdit("000000FF")
        self.hex_textBox.setFixedWidth(100)
        self.hex_textBox.textEdited.connect(self.update_rgba_values)
        self.hex_textBox.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{8}")))

        hex_layout = QHBoxLayout()
        hex_layout.setAlignment(Qt.AlignLeft)
        hex_layout.addWidget(hex_label)
        hex_layout.addWidget(self.hex_textBox)

        # Layouts
        frame_tab_layout = QVBoxLayout()
        frame_tab_layout.addWidget(save_button)
        frame_tab.setLayout(frame_tab_layout)

        color_tab_layout = QVBoxLayout()
        color_tab_layout.addLayout(red_layout)
        color_tab_layout.addLayout(green_layout)
        color_tab_layout.addLayout(blue_layout)
        color_tab_layout.addLayout(alpha_layout)
        color_tab_layout.addLayout(hex_layout)
        color_tab_layout.addWidget(color_button)
        color_tab.setLayout(color_tab_layout)

        container_layout = QVBoxLayout()
        container_layout.addWidget(self.view)
        container_layout.addWidget(tabs)

        # Main container (central widget)
        container = QWidget()
        container.setLayout(container_layout)
        self.setCentralWidget(container)
        

    def create_rgb_slider(self, label_text, alpha=False):
        label = QLabel(f"{label_text}:")
        label.setFixedWidth(20)

        textBox = QLineEdit("0" if not alpha else "1")
        textBox.setFixedWidth(50)
        textBox.setValidator(QIntValidator(0, 255) if not alpha else QDoubleValidator(0.0, 1.0, 4))  # Only integers 0-255 or 4 digit values 0-1
        textBox.textChanged.connect(lambda text: slider.setValue(int(text)) if not alpha else slider.setValue(int(float(text)*10000)))
        textBox.textEdited.connect(self.update_hex_value)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 255) if not alpha else slider.setRange(0, 10000)
        slider.setValue(0 if not alpha else 10000)
        slider.setFixedWidth(100)
        slider.valueChanged.connect(lambda v: textBox.setText(f"{v}" if not alpha else f"{round(v/10000, 4)}"))
        slider.valueChanged.connect(self.update_hex_value)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(label)
        layout.addWidget(textBox)
        layout.addWidget(slider)

        return textBox, layout
    
    def update_hex_value(self):
        red_value = int(self.red_textBox.text())
        green_value = int(self.green_textBox.text())
        blue_value = int(self.blue_textBox.text())
        alpha_value = int(round(float(self.alpha_textBox.text()), 4) * 255)

        self.hex_textBox.setText(f"{red_value:02X}{green_value:02X}{blue_value:02X}{alpha_value:02X}")

    def update_rgba_values(self):
        hex_text = self.hex_textBox.text()
        if len(hex_text) == 8:
            red = int(hex_text[0:2], 16)
            green = int(hex_text[2:4], 16)
            blue = int(hex_text[4:6], 16)
            alpha = int(hex_text[6:8], 16) / 255.0
            self.red_textBox.setText(f"{red}")
            self.green_textBox.setText(f"{green}")
            self.blue_textBox.setText(f"{blue}")
            self.alpha_textBox.setText(f"{alpha:.4f}")

    def update_effect(self):
        # No automatic animation for now
        pass

    def set_selected_color(self):
        red = int(self.red_textBox.text())
        green = int(self.green_textBox.text())
        blue = int(self.blue_textBox.text())
        alpha = int(round(float(self.alpha_textBox.text()), 4) * 255)
        color = QColor(red, green, blue, alpha)
        for led in self.scene.leds:
            if led.isSelected():
                led.set_color(color)

    def save_frame(self):
        groups = []
        color_map = {}
        group_id = 1
        for led in self.scene.leds:
            r, g, b, a = led.brush.color().getRgbF()
            rgb = (r, g, b, a)
            if rgb not in color_map:
                # create new group entry
                group = {
                    "id": group_id,
                    "isPulseActive": False,
                    "isStaticActive": False,
                    "isTwinkleActive": False,
                    "color": {
                        "r": r,
                        "g": g,
                        "b": b,
                        "a": a
                    },
                    "LEDIndices": []
                }
                color_map[rgb] = group
                groups.append(group)
                group_id += 1

            # append this LED index
            color_map[rgb]["LEDIndices"].append(led.index)

        frame_data = {
            "groups": groups
        }

        folder = "ShowBuilderTest"
        filename = f"./stadium/Assets/Resources/{folder}/frame_{self.frameNumber}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(frame_data, f, indent=2)
            print(f"Saved frame_{self.frameNumber}.json to {filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MainWindow()
    viewer.show()
    sys.exit(app.exec_())