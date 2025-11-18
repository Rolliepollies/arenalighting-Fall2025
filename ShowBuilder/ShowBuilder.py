import os
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QTabWidget, QComboBox, QHBoxLayout, QLineEdit,
    QGraphicsEllipseItem, QPushButton, QVBoxLayout, QWidget, QColorDialog, QSlider, QLabel, QScrollArea, QGridLayout, QCheckBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QRegExp
from PyQt5.QtGui import QColor, QBrush, QPainter, QIntValidator, QDoubleValidator, QRegExpValidator, QImage, QPixmap
from PIL import Image

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene = scene
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
        self.mode = "single"
        # Create LEDs and sves row and section numbers
        self.create_LEDs()
        self.sectionsRowsInit()
        
    def mousePressEvent(self, event):
        
        if event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return
        
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        
        print(self.mode)
        if isinstance(item, LEDItem):
            if self.mode == "single":
                modifiers = QApplication.keyboardModifiers()
                if modifiers & Qt.ControlModifier:
                # Toggle selection instead of clearing
                    item.setSelected(not item.isSelected())
                else:
                    # Normal click: clear all others
                    for led in self.leds:
                        led.setSelected(False)
                    item.setSelected(True)
            elif self.mode == "section":
                print("section")
                sect = self.sections
                # Find which section this LED belongs to
                section_index = -1
                index = 0
                for i in sect:
                    if i[0] <= item.index < i[1]:
                        section_index = index
                        break
                    index += 1
                print(section_index)
                if section_index >=0:
                    modifiers = QApplication.keyboardModifiers()
                    if not (modifiers & Qt.ControlModifier):
                        for led in self.leds:
                            led.setSelected(False)
                    for led in self.leds[sect[section_index][0]:sect[section_index][1]]:
                        led.setSelected(True)
                        

            elif self.mode == "row":
                print("row")
                row = self.rows
            # Find which row this LED belongs to
            # You said rows.txt stores LED indices where rows end, so:
                rowIndex = -1
                index = 0 

                for i in row:
                    print(i)
                    if i[0] <= item.index < i[1]:
                        rowIndex = index
                        break

                    index += 1
                    
                print(rowIndex)
                if rowIndex >= 0:
                    modifiers = QApplication.keyboardModifiers()
                    if not (modifiers & Qt.ControlModifier):
                        for led in self.leds:
                            led.setSelected(False)
                    for led in self.leds[row[rowIndex][0]:row[rowIndex][1]]:
                        led.setSelected(True)
        # Only call super() if you didn't manually handle the click
        else:
            super().mousePressEvent(event)

        
        
    def sectionsRowsInit(self):
        self.sections = []
        self.rows = []
        temp = -1
        with open("showBuilder/sections.txt", 'r', encoding='utf-8') as f:
            for line in f:
                if temp != -1:
                    self.sections.append([int(temp), int(line.strip())])
                temp = line.strip()
        self.sections.append([int(temp), len(self.leds)])  
        temp = -1     
        with open("showBuilder/rows.txt", 'r', encoding='utf-8') as f:
            for line in f:
                if temp != -1:
                    self.rows.append([int(temp), int(line.strip())])
                temp = line.strip()
        self.rows.append([int(temp), len(self.leds)])
    

    def create_LEDs(self):
        self.leds = []
        index = 0
        with open("showBuilder/postions.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.split(',')
                
                x = float(line[0].strip())
                z = float(line[1].strip()) # We will refer to this as y now on since it makes more sense in a 2d space
                if index > 16862:
                    if index > 20800:
                        x = x -3
                    else:
                        x += 3
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
        preset_tab = QWidget()
        mode_tab = QWidget()

        tabs.addTab(README_tab, "README")
        tabs.addTab(frame_tab, "Frame")
        tabs.addTab(color_tab, "Color")
        tabs.addTab(preset_tab, "Presets")
        tabs.addTab(mode_tab, "Mode")
        tabs.addTab(self.create_image_tab(), "Image Loader")

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

        duplicate_frame_button = QPushButton("Duplicate Current Frame")
        duplicate_frame_button.setFixedWidth(150)
        duplicate_frame_button.setFixedHeight(20)
        duplicate_frame_button.clicked.connect(self.duplicate_current_frame)

        color_button = QPushButton("Color Selected LEDs")
        color_button.clicked.connect(self.set_selected_color)
        color_button.setFixedWidth(150)
        color_button.setFixedHeight(20)

        single_button = QPushButton("single")
        single_button.clicked.connect(self.single)
        single_button.setFixedWidth(color_button.sizeHint().width())

        row_button = QPushButton("row")
        row_button.clicked.connect(self.row)
        row_button.setFixedWidth(color_button.sizeHint().width())

        section_button = QPushButton("section")
        section_button.clicked.connect(self.section)
        section_button.setFixedWidth(color_button.sizeHint().width())

        preset_button = QPushButton("plaid")
        preset_button.clicked.connect(self.plaid)
        preset_button.setFixedWidth(100)

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

        # Primary hex box
        primary_hex_label = QLabel("Primary Hex: #")
        primary_hex_label.setFixedWidth(primary_hex_label.sizeHint().width())
        self.primary_hex_textBox = QLineEdit("FF0000FF")  # default red
        self.primary_hex_textBox.setFixedWidth(100)
        self.primary_hex_textBox.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{8}")))
        self.primary_hex_textBox.textEdited.connect(self.primary)

        primary_hex_layout = QHBoxLayout()
        primary_hex_layout.setAlignment(Qt.AlignLeft)
        primary_hex_layout.addWidget(primary_hex_label)
        primary_hex_layout.addWidget(self.primary_hex_textBox)

        # Secondary hex box
        secondary_hex_label = QLabel("Secondary Hex: #")
        secondary_hex_label.setFixedWidth(secondary_hex_label.sizeHint().width())
        self.secondary_hex_textBox = QLineEdit("0000FFFF")  # default cyan
        self.secondary_hex_textBox.setFixedWidth(100)
        self.secondary_hex_textBox.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{8}")))
        self.secondary_hex_textBox.textEdited.connect(self.secondary)

        secondary_hex_layout = QHBoxLayout()
        secondary_hex_layout.setAlignment(Qt.AlignLeft)
        secondary_hex_layout.addWidget(secondary_hex_label)
        secondary_hex_layout.addWidget(self.secondary_hex_textBox)

        # Duration text box
        duration_label = QLabel("Duration (ms):")
        duration_label.setFixedWidth(duration_label.sizeHint().width())
        self.duration_textBox = QLineEdit("1000")  # default 1000 ms
        self.duration_textBox.setFixedWidth(100)
        self.duration_textBox.setValidator(QIntValidator(0, 100000))  # Allow durations from 0 to 100000 ms

        duration_layout = QHBoxLayout()
        duration_layout.setAlignment(Qt.AlignLeft)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_textBox)

        # Dropdowns
        self.show_dropdown = QComboBox()
        self.show_dropdown.setFixedWidth(150)
        self.show_dropdown.setFixedHeight(20)
        self.show_dropdown.currentIndexChanged.connect(self.update_json_scroll_area)
        self.show_dropdown.currentIndexChanged.connect(lambda: self.load_frame(0))

        self.update_json_scroll_area()
        self.update_show_dropdown()

        # Layouts
        frame_tab_layout = QHBoxLayout()
        frame_tab_layout_left = QVBoxLayout()
        frame_tab_layout_right = QVBoxLayout()

        frame_tab_layout_left.addWidget(self.current_frame_label)
        frame_tab_layout_left.addWidget(self.show_dropdown)
        frame_tab_layout_left.addWidget(self.json_scroll_area)

        frame_tab_layout_right.addWidget(save_frame_button)
        frame_tab_layout_right.addWidget(create_frame_button)
        frame_tab_layout_right.addWidget(duplicate_frame_button)
        frame_tab_layout_right.addWidget(delete_current_frame)

        frame_tab_layout.addLayout(frame_tab_layout_left)
        frame_tab_layout.addLayout(frame_tab_layout_right)
        frame_tab.setLayout(frame_tab_layout)

        color_tab_layout = QHBoxLayout()
        column1_layout = QVBoxLayout()
        column2_layout = QVBoxLayout()
        column1_layout.addLayout(red_layout)
        column1_layout.addLayout(green_layout)
        column1_layout.addLayout(blue_layout)
        column1_layout.addLayout(alpha_layout)
        column1_layout.addLayout(hex_layout)
        column1_layout.addWidget(color_button)
        column2_layout.addLayout(duration_layout)
        color_tab_layout.addLayout(column1_layout)
        color_tab_layout.addLayout(column2_layout)
        color_tab.setLayout(color_tab_layout)

        preset_tab_layout = QVBoxLayout()
        preset_tab_layout.addWidget(preset_button)
        preset_tab_layout.addLayout(primary_hex_layout)
        preset_tab_layout.addLayout(secondary_hex_layout)
        preset_tab.setLayout(preset_tab_layout)

        mode_tab_layout = QVBoxLayout()
        mode_tab_layout.addWidget(single_button)
        mode_tab_layout.addWidget(row_button)
        mode_tab_layout.addWidget(section_button)
        mode_tab.setLayout(mode_tab_layout)

        # Main container (central widget)
        main_container_layout = QVBoxLayout()
        main_container_layout.addWidget(self.view)
        main_container_layout.addWidget(tabs)
        main_container = QWidget()
        main_container.setLayout(main_container_layout)
        self.setCentralWidget(main_container)

    def create_image_tab(self):
        layout = QVBoxLayout()

        # Image preview
        self.image_preview = QLabel("No image loaded")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setFixedSize(300, 300)
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(self.image_preview)

        # Rotation buttons
        rotate_layout = QHBoxLayout()
        rotate_left_btn = QPushButton("⟲ Rotate Left")
        rotate_right_btn = QPushButton("⟳ Rotate Right")

        rotate_left_btn.clicked.connect(lambda: self.rotate_loaded_image(-90))
        rotate_right_btn.clicked.connect(lambda: self.rotate_loaded_image(90))

        rotate_layout.addWidget(rotate_left_btn)
        rotate_layout.addWidget(rotate_right_btn)
        layout.addLayout(rotate_layout)

        # Load image button
        load_button = QPushButton("Select Image")
        load_button.clicked.connect(self.pick_image_file)
        layout.addWidget(load_button)

        # Apply image to LEDs
        apply_button = QPushButton("Apply Image to LEDs")
        apply_button.clicked.connect(self.load_image_onto_leds)
        layout.addWidget(apply_button)

        widget = QWidget()
        widget.setLayout(layout)
        return widget
        

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


    #simplify this later
    def primary(self):
        hex_text = self.primary_hex_textBox.text()
        if len(hex_text) == 8:
            r = int(hex_text[0:2], 16)
            g = int(hex_text[2:4], 16)
            b = int(hex_text[4:6], 16)
            a = int(hex_text[6:8], 16) 
            self.primary_color = QColor(r, g, b, a)
            
        
    def secondary(self):
        hex_text = self.secondary_hex_textBox.text()
        if len(hex_text) == 8:
            r = int(hex_text[0:2], 16)
            g = int(hex_text[2:4], 16)
            b = int(hex_text[4:6], 16)
            a = int(hex_text[6:8], 16) 
            self.secondary_color = QColor(r, g, b, a)
            
    
    def update_rgba_values(self):
        hex_text = self.hex_textBox.text()
        if len(hex_text) == 8:
            red = int(hex_text[0:2], 16)
            green = int(hex_text[2:4], 16)
            blue = int(hex_text[4:6], 16)
            alpha = int(hex_text[6:8], 16) / 255.0
            self.sred_textBox.setText(f"{red}")
            self.sgreen_textBox.setText(f"{green}")
            self.sblue_textBox.setText(f"{blue}")
            self.salpha_textBox.setText(f"{alpha:.4f}")

    def update_effect(self):
        # No automatic animation for now
        pass
    
    def row(self):
        self.scene.mode = "row"
        
    def section(self):
        self.scene.mode = "section"
        
    def single(self):
        self.scene.mode = "single"
    
    def plaid(self):
        leds = self.scene.leds
        index = 0
        odd = False
        
        primary = getattr(self, "primary_color", QColor(255,0,0,255))
        secondary = getattr(self, "secondary_color", QColor(0,0,255,255))
        
        for i in self.scene.sections:
            print(i)
           
            if odd:
                which = primary
            else:
                which = secondary
            
            while index < i[1]:
                
                leds[index].set_color(which)
                index += 1
            odd = not odd
            print(odd)
                
    def pick_image_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return

        self.loaded_image_path = path
        self.loaded_image = Image.open(path).convert("RGBA")  # keep transparency
        self.update_image_preview()

    def rotate_loaded_image(self, angle):
        if not hasattr(self, "loaded_image"):
            return

        # Rotate PIL image
        self.loaded_image = self.loaded_image.rotate(angle, expand=True)
        self.update_image_preview()

    def update_image_preview(self):
        if not hasattr(self, "loaded_image"):
            return

        img = self.loaded_image.copy()
        img.thumbnail((300, 300))  # fit preview box

        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)

        self.image_preview.setPixmap(pix)

    def load_image_onto_leds(self):
        if not hasattr(self, "loaded_image"):
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return

        img = self.loaded_image.convert("RGB")

        # Get selected LEDs
        selected_leds = [led for led in self.scene.leds if led.isSelected()]
        if not selected_leds:
            QMessageBox.warning(self, "No LEDs Selected", "Please select some LEDs first.")
            return

        # Resize image to number of LEDs (square-ish)
        num_leds = len(selected_leds)
        grid_size = int(num_leds ** 0.5)
        if grid_size < 1:
            return

        img = img.resize((grid_size, grid_size))
        width, height = img.size

        # Normalize LED positions
        min_x = min(l.x() for l in selected_leds)
        max_x = max(l.x() for l in selected_leds)
        min_y = min(l.y() for l in selected_leds)
        max_y = max(l.y() for l in selected_leds)

        for led in selected_leds:
            lx = (led.x() - min_x) / (max_x - min_x + 1e-6)
            ly = (led.y() - min_y) / (max_y - min_y + 1e-6)

            px = int(lx * (width - 1))
            py = int(ly * (height - 1))

            r, g, b = img.getpixel((px, py))
            led.set_color(QColor(r, g, b, 255))

    def set_selected_color(self):
        red = int(self.red_textBox.text())
        green = int(self.green_textBox.text())
        blue = int(self.blue_textBox.text())
        alpha = int(round(float(self.alpha_textBox.text()), 4) * 255)
        print(red, green, blue, alpha)
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

            if "duration" in frame_data:
                self.duration_textBox.setText(str(frame_data["duration"]))
            else:
                self.duration_textBox.setText("1000")  # default value

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
            button.clicked.connect(lambda connected, f=json_file: self.load_frame(f.split('.')[0]))
            layout.addWidget(button)

        layout.addStretch()
        self.json_scroll_area.setWidget(content_widget)
        self.json_scroll_area.setWidgetResizable(True)

    def create_new_frame(self):
        self.current_frame_label.setText(f"Current Frame: temp")
        for led in self.scene.leds:
            led.set_color(QColor(0, 0, 0, 255))  # Reset to black

    def duplicate_current_frame(self):
        folder = str(self.show_dropdown.currentText())
        source_filename = f"./stadium/Assets/Resources/{folder}/{self.frameNumber}.json"

        # Shift existing frames to make space for the duplicate
        self.update_frame_numbers(direction=True)

        # Copy the current frame to the new frame
        dest_filename = f"./stadium/Assets/Resources/{folder}/{self.frameNumber + 1}.json"
        with open(source_filename, "r", encoding="utf-8") as src_file, open(dest_filename, "w", encoding="utf-8") as dst_file:
            dst_file.write(src_file.read())

        self.update_json_scroll_area()

    def delete_current_frame(self):
        if self.current_frame_label.text() == f"Current Frame: temp":
            print("Cannot delete unsaved frame.")
            return
        
        # Delete the current frame file
        folder = str(self.show_dropdown.currentText())
        filename = f"./stadium/Assets/Resources/{folder}/{self.frameNumber}.json"
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted frame {self.frameNumber}.json from {filename}")

        self.update_frame_numbers(direction=False)

        self.load_frame(self.frameNumber - 1 if self.frameNumber > 0 else 0)
    
    # Renames frames after insertion or deletion to maintain sequence
    # direction: True = insert, False = delete
    def update_frame_numbers(self, direction:bool):
        folder = str(self.show_dropdown.currentText())
        fileList = os.listdir(f"./stadium/Assets/Resources/{folder}")
        fileList.sort(key=lambda f: int(f.split('.')[0]))

        for file in (fileList[self.frameNumber:] if not direction else reversed(fileList[self.frameNumber + 1:])):
            num = int(file.split('.')[0])
            os.rename(
                f"./stadium/Assets/Resources/{folder}/{file}",
                f"./stadium/Assets/Resources/{folder}/{num + 1 if direction else num - 1}.json"
            )
            print(f"Renamed frame {num}.json to {num + 1 if direction else num - 1}.json")

        self.update_json_scroll_area()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MainWindow()
    viewer.show()
    sys.exit(app.exec_())