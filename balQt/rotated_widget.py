from typing import TypeVar, Generic
from balQt.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QWidget, QSizePolicy
from balQt.QtCore import QSize, Qt
from balQt.tools import (combine_size_policies, get_policies, get_dimensions, get_rotated_dimensions,
                         get_original_dimensions, get_quadrant_or_axis, QuadrantOrAxis, abs_sin_d, abs_cos_d)

# Type variable for generic widget type
T = TypeVar('T', bound=QWidget)

class RotatedWidget(QGraphicsView, Generic[T]):
    """
    A custom QGraphicsView that rotates a widget by a specified angle.
    This class wraps a QWidget in a QGraphicsProxyWidget and handles rotation and resizing dynamically.

    Attributes:
        widget (T): The widget to be rotated.
        angle (float): The rotation angle in degrees (default is 270).
        preserve_aspect_ratio (bool): Flag for preserving the aspect ratio of the widget (default is False)
        scene (QGraphicsScene): The scene containing the proxy widget.
        proxy (QGraphicsProxyWidget): The proxy that applies the rotation to the widget.
    """

    def __init__(self, widget: T, angle: float = 270, parent: QWidget = None, preserve_aspect_ratio: bool = False):
        """
        Initialize the rotated widget.

        Args:
            widget (T): The widget to be embedded and rotated.
            angle (float): The rotation angle in degrees.
            parent (QWidget, optional): The parent widget. Defaults to None.
            preserve_aspect_ratio (bool, optional): To preserve aspect ratio. Defaults to False.
        """
        super().__init__(parent)
        self.widget = widget
        self.angle = angle
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.scene = QGraphicsScene(self)

        # Create and configure the QGraphicsProxyWidget
        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(widget)
        self.proxy.setTransformOriginPoint(widget.width() / 2, widget.height() / 2)
        self.proxy.setRotation(angle)

        # Add the proxy widget to the scene
        self.scene.addItem(self.proxy)
        self.setScene(self.scene)

        # Set view properties for transparent background
        self.setStyleSheet("border: none; background: transparent;")
        self.setAlignment(Qt.AlignCenter)
        self.update_size_policy()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def update_size_policy(self):
        """
        Update the size policy and adjust the widget dimensions based on the rotation angle.
        """
        rotated_width, rotated_height = get_rotated_dimensions(self.widget.width(), self.widget.height(), self.angle)
        rotated_width, rotated_height = round(rotated_width), round(rotated_height)
        horizontal_policy, vertical_policy = get_policies(self.widget.sizePolicy())
        if self.angle % 180 == 0:
            self.setSizePolicy(horizontal_policy, vertical_policy)
            self.setMinimumSize(self.widget.minimumSize())
            self.setMaximumSize(self.widget.maximumSize())
            if vertical_policy == QSizePolicy.Fixed:
                self.setFixedHeight(rotated_height)
            if horizontal_policy == QSizePolicy.Fixed:
                self.setFixedWidth(rotated_width)
        elif self.angle % 90 == 0:
            self.setSizePolicy(vertical_policy, horizontal_policy)
            self.setMinimumSize(QSize(self.widget.minimumHeight(), self.widget.minimumWidth()))
            self.setMaximumSize(QSize(self.widget.maximumHeight(), self.widget.maximumWidth()))
            if vertical_policy == QSizePolicy.Fixed:
                self.setFixedWidth(rotated_width)
            if horizontal_policy == QSizePolicy.Fixed:
                self.setFixedHeight(rotated_height)
        else:
            combined_size_policy = combine_size_policies(horizontal_policy, vertical_policy)
            self.setSizePolicy(combined_size_policy, combined_size_policy)
            self.setMinimumSize(QSize(*map(round, get_rotated_dimensions(self.widget.minimumWidth(),
                                                                         self.widget.minimumHeight(), self.angle))))
            self.setMaximumSize(QSize(*map(round, get_rotated_dimensions(self.widget.maximumWidth(),
                                                                         self.widget.maximumHeight(), self.angle))))
        self.setGeometry(0, 0, rotated_width, rotated_height)
        horizontal_policy, vertical_policy = get_policies(self.sizePolicy())
        if horizontal_policy in [QSizePolicy.Minimum, QSizePolicy.MinimumExpanding]:
            if rotated_width > self.minimumWidth():
                self.setMinimumWidth(rotated_width)
        elif horizontal_policy == QSizePolicy.Maximum:
            if rotated_width < self.maximumWidth():
                self.setMaximumWidth(rotated_width)
        if vertical_policy in [QSizePolicy.Minimum, QSizePolicy.MinimumExpanding]:
            if rotated_height > self.minimumHeight():
                self.setMinimumHeight(rotated_height)
        elif vertical_policy == QSizePolicy.Maximum:
            if rotated_height < self.maximumHeight():
                self.setMaximumHeight(rotated_height)

    def sizeHint(self):
        rotated_width, rotated_height = get_rotated_dimensions(self.widget.sizeHint().width(),
                                                               self.widget.sizeHint().height(), self.angle)
        return QSize(round(rotated_width), round(rotated_height))


    def get_widget_dimensions(self):
        horizontal_policy, vertical_policy = get_policies(self.widget.sizePolicy())
        current_width, current_height = get_dimensions(self.widget, consider_none=not self.preserve_aspect_ratio)
        constant_width = horizontal_policy in [QSizePolicy.Fixed, QSizePolicy.Preferred]
        constant_height = vertical_policy in [QSizePolicy.Fixed, QSizePolicy.Preferred]
        if (constant_height and constant_width) or ((constant_height or constant_width) and self.preserve_aspect_ratio):
            return current_width, current_height
        else:
            width, height = get_original_dimensions(self.width(), self.height(), self.angle,
                                                    current_width=current_width, current_height=current_height)
            if horizontal_policy in [QSizePolicy.Minimum, QSizePolicy.MinimumExpanding]:
                width = max(float(self.widget.sizeHint().width()), width)
            elif horizontal_policy == QSizePolicy.Maximum:
                width = min(float(self.widget.sizeHint().width()), width)
            if vertical_policy in [QSizePolicy.Minimum, QSizePolicy.MinimumExpanding]:
                height = max(float(self.widget.sizeHint().height()), height)
            elif vertical_policy == QSizePolicy.Maximum:
                height = min(float(self.widget.sizeHint().height()), height)
            return width, height

    def resizeEvent(self, event):
        """
        Handle the resize event to update proxy and scene geometries.

        Args:
            event: The resize event.
        """
        proxy_rect = self.proxy.geometry()
        scene_rect = self.scene.sceneRect()

        # Calculate original and rotated dimensions
        width, height = self.get_widget_dimensions()
        rotated_width, rotated_height = get_rotated_dimensions(width, height, self.angle)

        # Adjust geometry if necessary
        if abs(self.width() - round(rotated_width)) >= 1 or abs(self.height() - round(rotated_height)) >= 0:
            geom = self.geometry()
            self.setGeometry(geom.left(), geom.top(), round(rotated_width), round(rotated_height))

        # Adjust scene rect based on the quadrant or axis
        quadrant_or_axis = get_quadrant_or_axis(self.angle)
        if quadrant_or_axis == QuadrantOrAxis.QUADRANT_1:
            scene_rect.setLeft(scene_rect.left() - (height - proxy_rect.height()) * abs_sin_d(self.angle))
        elif quadrant_or_axis == QuadrantOrAxis.QUADRANT_2:
            scene_rect.setLeft(scene_rect.left() - (rotated_width - scene_rect.width()))
            scene_rect.setTop(scene_rect.top() - (height - proxy_rect.height()) * abs_cos_d(self.angle))
        elif quadrant_or_axis == QuadrantOrAxis.QUADRANT_3:
            scene_rect.setLeft(scene_rect.left() - (width - proxy_rect.width()) * abs_cos_d(self.angle))
            scene_rect.setTop(scene_rect.top() - (rotated_height - scene_rect.height()))
        elif quadrant_or_axis == QuadrantOrAxis.QUADRANT_4:
            scene_rect.setTop(scene_rect.top() - (width - proxy_rect.width()) * abs_sin_d(self.angle))
        elif quadrant_or_axis == QuadrantOrAxis.NEGATIVE_X_AXIS:
            scene_rect.setLeft(scene_rect.left() - (rotated_width - scene_rect.width()))
        elif quadrant_or_axis == QuadrantOrAxis.NEGATIVE_Y_AXIS:
            scene_rect.setTop(scene_rect.top() - (rotated_height - scene_rect.height()))

        # Set final scene and proxy geometry
        scene_rect.setWidth(rotated_width)
        scene_rect.setHeight(rotated_height)

        proxy_rect.adjust(0, 0, width - proxy_rect.width(), height - proxy_rect.height())
        self.scene.setSceneRect(scene_rect)
        self.proxy.setGeometry(proxy_rect)
        super().resizeEvent(event)

    def __getattr__(self, item):
        """
        Delegate attribute access to the underlying widget or the QGraphicsView.

        Args:
            item (str): Attribute name.

        Returns:
            Any: Attribute value from either the widget or the base class.
        """
        if hasattr(super(QGraphicsView, self), item):
            return super(QGraphicsView, self).__getattribute__(item)
        else:
            return self.widget.__getattribute__(item)
