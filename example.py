import os.path
from balQt.QtWidgets import QApplication, QPushButton, QHBoxLayout, QWidget
from balQt.QtGui import QPainter, QImage
from balQt.QtCore import QSize, QPoint
from balQt.rotated_widget import RotatedWidget


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rotated Widget Example")
        layout = QHBoxLayout(self)

        # Create a normal QPushButton
        normal_button = QPushButton("Normal Button")
        layout.addWidget(normal_button)

        # Create a rotated button using RotatedWidget at angle 45
        rotated_button_45 = QPushButton("Rotated Button 45")
        rotated_button_45_widget = RotatedWidget(rotated_button_45, angle=45)
        layout.addWidget(rotated_button_45_widget)
        
        # Create a rotated button using RotatedWidget at angle 45
        rotated_button_270 = QPushButton("Rotated Button 270")
        rotated_button_270_widget = RotatedWidget(rotated_button_270, angle=270)
        layout.addWidget(rotated_button_270_widget)

        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        if not os.path.exists("images\\screenshot.png"):
            self.capture_screenshot()

    def capture_screenshot(self):
        # Define a higher resolution (scaling factor)
        scale_factor = 2  # Change to a higher value for better quality
        original_size = self.size()
        high_quality_size = QSize(original_size.width() * scale_factor, original_size.height() * scale_factor)

        # Render to a high-resolution QImage
        image = QImage(high_quality_size, QImage.Format_ARGB32)
        image.setDevicePixelRatio(scale_factor)  # Account for scale factor
        painter = QPainter(image)
        self.render(painter, QPoint(0, 0))
        painter.end()

        # Save the image
        image.save("images\\screenshot.png", "PNG")
        print("Screenshot saved as 'images\\screenshot.png'")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWidget()
    window.show()
    app.exec_()