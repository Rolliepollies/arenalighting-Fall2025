import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsEllipseItem, QPushButton, QVBoxLayout, QWidget, QColorDialog, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPainter

ledLocations = []

def grabPositions():
    index = 0
    with open("showBuilder/postions.txt", 'r', encoding='utf-8') as f:
        for line in f:
            line = line.split(',')
            x = float(line[0].strip())
            
            z = float(line[1].strip())#we will refer to this as y now on since it makes more sense in a 2d space
            
            ledLocations.append([x * 30, z * 30, index])
            index += 1
            

grabPositions()


def set_selected_color(self):
    color = QColorDialog.getColor()
    if not color.isValid():  
        return
    for led in self.leds:
        if led.isSelected():
            led.set_color(color)

class LEDItem(QGraphicsEllipseItem):
    def __init__(self, x, y, index, size=10):
        super().__init__(-size/2, -size/2, size, size)
        self.setPos(x, y)
        self.index = index
        self.setBrush(QBrush(Qt.gray))
        self.color = QColor(Qt.gray)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)

    def set_color(self, color: QColor):
        self.color = color
        self.setBrush(QBrush(color))


class LEDViewer(QMainWindow):
    def __init__(self, led_positions):
        super().__init__()
        self.setWindowTitle("LED Mapper")
        self.resize(800, 600)

        # Scene & view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)  # allow box selection

        # Create LEDs
        self.leds = []
        for (x, y, index) in led_positions:
            led = LEDItem(x, y, index)
            self.scene.addItem(led)
            self.leds.append(led)

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
        self.frame = 0
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
        for led in self.leds:
            if led.isSelected():
                led.set_color(color)
                
                
    

    def save_frame(self):
        print('hello')
        groups = []
        color_map = {}
        group_id = 1
        for led in self.leds:
            r, g, b, a = led.color.getRgbF()
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
        print(str(self.frame) )
        filename = f"frame_{self.frame}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(frame_data, f, indent=2)




        
        
        
        
    # Zoom with mouse wheel
    def wheelEvent(self, event):
        zoom_in = 1.2
        zoom_out = 1 / zoom_in
        if event.angleDelta().y() > 0:
            self.view.scale(zoom_in, zoom_in)
        else:
            self.view.scale(zoom_out, zoom_out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = LEDViewer(ledLocations)
    viewer.show()
    sys.exit(app.exec_())