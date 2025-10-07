import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsEllipseItem, QPushButton, QVBoxLayout, QWidget, QColorDialog, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPainter


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
        self.resize(800, 600)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)


        # Scene & view
        self.scene = LEDViewer()
        self.view = CustomGraphicsView(self.scene)

        # Buttons
        self.save_button = QPushButton("Save Frame")
        self.color_button = QPushButton("Set Selected LEDs selected Hue")

        self.save_button.clicked.connect(self.save_frame)
        self.color_button.clicked.connect(self.set_selected_color)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.color_button)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for animation (placeholder)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_effect)
        self.frameNumber = 0
        self.timer.start(100)  # 10 fps
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setRange(0, 359)
        self.hue_slider.setValue(0)
        self.hue_label = QLabel("Hue: 0")
        self.hue_slider.valueChanged.connect(lambda v: self.hue_label.setText(f"Hue: {v}"))
        layout.addWidget(self.hue_label)
        layout.addWidget(self.hue_slider)

    def update_effect(self):
        # No automatic animation for now
        pass

    def set_selected_color(self):
        hue = self.hue_slider.value()
        color = QColor.fromHsv(hue, 255, 255)
        for led in self.scene.leds:
            if led.isSelected():
                led.set_color(color)

    def save_frame(self):
        print('hello')
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

        print('end')
        print(str(self.frameNumber) )
        folder = "ShowBuilderTest"
        filename = f"./stadium/Assets/Resources/{folder}/frame_{self.frameNumber}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(frame_data, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MainWindow()
    viewer.show()
    sys.exit(app.exec_())