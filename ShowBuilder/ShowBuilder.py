import os
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QTabWidget, QComboBox, QHBoxLayout, QLineEdit,
    QGraphicsEllipseItem, QPushButton, QVBoxLayout, QWidget, QColorDialog, QSlider, QLabel, QScrollArea, QGridLayout
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

        # Labels
        readme_label = QLabel()
        self.current_frame_label = QLabel()
        self.current_frame_label.setFixedWidth(150)
        self.current_frame_label.setFixedHeight(30)

        # Scroll area for .json file selection
        self.json_scroll_area = QScrollArea()
        self.json_scroll_area.setFixedWidth(150)
        self.json_scroll_area.setFixedHeight(150)

        # Buttons
        save_frame_button = QPushButton("Save Frame")
        save_frame_button.clicked.connect(self.save_frame)
        save_frame_button.setFixedWidth(150)
        save_frame_button.setFixedHeight(20)

        create_frame_button = QPushButton("Create New Frame")
        create_frame_button.clicked.connect(self.create_new_frame)
        create_frame_button.setFixedWidth(150)
        create_frame_button.setFixedHeight(20)

        delete_current_frame = QPushButton("Delete Current Frame")
        delete_current_frame.clicked.connect(self.delete_current_frame)
        delete_current_frame.setFixedWidth(150)
        delete_current_frame.setFixedHeight(20)

        color_button = QPushButton("Color Selected LEDs")
        color_button.clicked.connect(self.set_selected_color)
        color_button.setFixedWidth(150)
        color_button.setFixedHeight(20)

        # Dropdowns
        self.show_dropdown = QComboBox()
        self.show_dropdown.setFixedWidth(150)
        self.show_dropdown.setFixedHeight(20)
        self.show_dropdown.currentIndexChanged.connect(self.update_json_scroll_area)
        self.show_dropdown.currentIndexChanged.connect(self.load_frame)
        
        self.update_json_scroll_area()
        self.update_show_dropdown()

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
        frame_tab_layout = QHBoxLayout()
        frame_tab_layout_left = QVBoxLayout()
        frame_tab_layout_right = QVBoxLayout()

        frame_tab_layout_left.addWidget(self.show_dropdown)
        frame_tab_layout_left.addWidget(self.json_scroll_area)
        frame_tab_layout_right.addWidget(self.current_frame_label)
        frame_tab_layout_right.addWidget(save_frame_button)
        frame_tab_layout_right.addWidget(create_frame_button)
        frame_tab_layout_right.addWidget(delete_current_frame)

        frame_tab_layout.addLayout(frame_tab_layout_left)
        frame_tab_layout.addLayout(frame_tab_layout_right)
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

        self.frameNumber = (int(len(self.json_scroll_area.widget().children())) - 1) if self.current_frame_label.text() == f"Current Frame: temp" else self.frameNumber
        self.current_frame_label.setText(f"Current Frame: {self.frameNumber}")

        folder = str(self.show_dropdown.currentText())
        filename = f"./stadium/Assets/Resources/{folder}/{self.frameNumber}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(frame_data, f, indent=2)
            print(f"Saved frame {self.frameNumber}.json to {filename}")
        
        self.update_json_scroll_area()



    def load_frame(self, frame_number=None):
        if frame_number == None:
            frame_number = self.frameNumber
        folder = str(self.show_dropdown.currentText())
        filename = f"./stadium/Assets/Resources/{folder}/{frame_number}.json"
        with open(filename, "r", encoding="utf-8") as f:
            frame_data = json.load(f)
            print(f"Loaded frame {frame_number}.json from {filename}")

            # Apply the loaded frame data to the scene
            for group in frame_data["groups"]:
                color = QColor(
                    int(group["color"]["r"] * 255),
                    int(group["color"]["g"] * 255),
                    int(group["color"]["b"] * 255),
                    int(group["color"]["a"] * 255)
                )
                for led_index in group["LEDIndices"]:
                    led = self.scene.leds[led_index]
                    led.set_color(color)

        self.frameNumber = int(frame_number)
        self.current_frame_label.setText(f"Current Frame: {self.frameNumber}")

    def update_show_dropdown(self):
        self.show_dropdown.clear()
        resources_dir = os.path.join(".", "stadium", "Assets", "Resources")
        try:
            for name in sorted(os.listdir(resources_dir)):
                path = os.path.join(resources_dir, name)
                if os.path.isdir(path):
                    self.show_dropdown.addItem(name)
        except FileNotFoundError:
            pass

    def update_json_scroll_area(self):
        folder = str(self.show_dropdown.currentText())
        json_dir = os.path.join(".", "stadium", "Assets", "Resources", folder)
        if not os.path.exists(json_dir):
            return

        # Sort JSON files by the numeric index in their filename (e.g. "12.json" -> 12)
        json_files_list = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        json_files_list.sort(key=lambda f: int(f.split('.')[0]))

        # Clear previous layout
        if self.json_scroll_area.widget():
            self.json_scroll_area.widget().deleteLater()

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        for json_file in json_files_list:
            button = QPushButton(f"Frame {json_file.split('.')[0]}")
            button.clicked.connect(lambda checked, f=json_file: self.load_frame(f.split('.')[0]))
            layout.addWidget(button)

        layout.addStretch()
        self.json_scroll_area.setWidget(content_widget)
        self.json_scroll_area.setWidgetResizable(True)

    def create_new_frame(self):
        self.current_frame_label.setText(f"Current Frame: temp")
        for led in self.scene.leds:
            led.set_color(QColor(0, 0, 0, 255))  # Reset to black

    def delete_current_frame(self):
        if self.current_frame_label.text() == f"Current Frame: temp":
            print("Cannot delete unsaved frame.")
            return
        
        folder = str(self.show_dropdown.currentText())
        filename = f"./stadium/Assets/Resources/{folder}/{self.frameNumber}.json"
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted frame {self.frameNumber}.json from {filename}")

        fileList = os.listdir(f"./stadium/Assets/Resources/{folder}")
        fileList.sort(key=lambda f: int(f.split('.')[0]))

        for file in fileList[self.frameNumber:]:
            num = int(file.split('.')[0])
            os.rename(
                f"./stadium/Assets/Resources/{folder}/{file}",
                f"./stadium/Assets/Resources/{folder}/{num - 1}.json"
            )
        print(f"Renamed frame {num}.json to {num - 1}.json")

        self.load_frame(self.frameNumber - 1 if self.frameNumber > 0 else 0)
        self.update_json_scroll_area()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MainWindow()
    viewer.show()
    sys.exit(app.exec_())