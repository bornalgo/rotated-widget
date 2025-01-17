from balQt.QtWidgets import QWidget, QSizePolicy
from typing import Tuple, Optional
from enum import Enum
import math

def combine_size_policies(horizontal_policy, vertical_policy):
    """
    Combines horizontal and vertical size policies by using logical OR and finding
    the closest matching or superior policy.

    Args:
        horizontal_policy (QSizePolicy.Policy): Horizontal size policy.
        vertical_policy (QSizePolicy.Policy): Vertical size policy.

    Returns:
        QSizePolicy.Policy: A single QSizePolicy.Policy representing both.
    """
    # Perform a logical OR to combine the policies
    combined_policy = horizontal_policy | vertical_policy

    # Ordered list of available policies from least to most flexible
    policy_order = [
        QSizePolicy.Fixed,
        QSizePolicy.Minimum,
        QSizePolicy.MinimumExpanding,
        QSizePolicy.Maximum,
        QSizePolicy.Preferred,
        QSizePolicy.Expanding,
        QSizePolicy.Ignored
    ]

    # Otherwise, find the closest superior policy
    for policy in policy_order:
        if combined_policy <= policy:
            return policy

    # Default fallback (should not be reached if all cases are covered)
    return QSizePolicy.Ignored


def get_policies(size_policy: QSizePolicy) -> Tuple[QSizePolicy.Policy, QSizePolicy.Policy]:
    return size_policy.horizontalPolicy(), size_policy.verticalPolicy()


def get_dimensions(widget: QWidget, consider_none: bool = False) -> Tuple[Optional[int], Optional[int]]:
    horizontal_policy, vertical_policy = get_policies(widget.sizePolicy())
    if horizontal_policy == QSizePolicy.Preferred:
        width = widget.sizeHint().width()
    elif horizontal_policy == QSizePolicy.Fixed or not consider_none:
        width = widget.width()
    else:
        width = None
    if vertical_policy == QSizePolicy.Preferred:
        height = widget.sizeHint().height()
    elif vertical_policy == QSizePolicy.Fixed or not consider_none:
        height = widget.height()
    else:
        height = None
    return width, height


class QuadrantOrAxis(Enum):
    POSITIVE_X_AXIS = "Positive X-Axis"
    POSITIVE_Y_AXIS = "Positive Y-Axis"
    NEGATIVE_X_AXIS = "Negative X-Axis"
    NEGATIVE_Y_AXIS = "Negative Y-Axis"
    QUADRANT_1 = "Quadrant 1 (0° to 90°)"
    QUADRANT_2 = "Quadrant 2 (90° to 180°)"
    QUADRANT_3 = "Quadrant 3 (180° to 270°)"
    QUADRANT_4 = "Quadrant 4 (270° to 360°)"


def get_quadrant_or_axis(angle: float) -> QuadrantOrAxis:
    """Determine the quadrant or axis for a given angle in degrees."""
    normalized_angle = normalize_angle(angle)  # Normalize the angle to [0, 360)

    if normalized_angle == 0:
        return QuadrantOrAxis.POSITIVE_X_AXIS
    elif normalized_angle == 90:
        return QuadrantOrAxis.POSITIVE_Y_AXIS
    elif normalized_angle == 180:
        return QuadrantOrAxis.NEGATIVE_X_AXIS
    elif normalized_angle == 270:
        return QuadrantOrAxis.NEGATIVE_Y_AXIS
    elif normalized_angle < 90:
        return QuadrantOrAxis.QUADRANT_1
    elif normalized_angle < 180:
        return QuadrantOrAxis.QUADRANT_2
    elif normalized_angle < 270:
        return QuadrantOrAxis.QUADRANT_3
    else:
        return QuadrantOrAxis.QUADRANT_4

def normalize_angle(angle: float):
    return angle % 360

def radians_angle(angle: float, normalize: bool = True):
    return math.radians(normalize_angle(angle) if normalize else angle)

def abs_sin(angle: float):
    return abs(math.sin(angle))

def abs_cos(angle: float):
    return abs(math.cos(angle))

def abs_sin_d(angle: float):
    return abs_sin(radians_angle(angle))

def abs_cos_d(angle: float):
    return abs_cos(radians_angle(angle))

def get_rotated_dimensions(width: float, height: float, angle: float):
    angle_rad = radians_angle(angle)

    # Reverse rotation matrix elements
    cos_angle = abs_cos(angle_rad)
    sin_angle = abs_sin(angle_rad)

    # Calculate rotated bounding box size
    rotated_width = width * cos_angle + height * sin_angle
    rotated_height = height * cos_angle + width * sin_angle

    return rotated_width, rotated_height


def get_original_dimensions(
        rotated_width: float,
        rotated_height: float,
        angle: float,
        current_width: float = None,
        current_height: float = None
) -> tuple[float, float]:
    """
    Compute the original width and height of a rectangle before rotation.

    Parameters:
        rotated_width (float): The width of the rectangle after rotation.
        rotated_height (float): The height of the rectangle after rotation.
        angle (float): The rotation angle in degrees.
        current_width (float, optional): The current width, used to determine aspect ratio if provided.
        current_height (float, optional): The current height, used to determine aspect ratio if provided.

    Returns:
        tuple[float, float]: The original width and height before rotation.
    """
    angle_rad = radians_angle(angle)

    # Compute trigonometric values for calculations.
    cos_angle = abs_cos(angle_rad)
    cos_2_angle = math.cos(2 * angle_rad)
    sin_angle = abs_sin(angle_rad)

    # Determine aspect ratio from provided dimensions.
    if current_width is not None and current_height is not None and current_height != 0:
        aspect_ratio = current_width / current_height
    elif current_width is not None:
        aspect_ratio = math.inf  # Infinite aspect ratio if only width is provided.
    elif current_height is not None:
        aspect_ratio = 0  # Zero aspect ratio if only height is provided.
    else:
        aspect_ratio = None  # Undefined if no dimensions are provided.

    # Handle cases where angle is a multiple of 90 degrees.
    if angle % 90 == 0:
        if angle % 180 == 0:
            if aspect_ratio is not None:
                if math.isinf(aspect_ratio):
                    height = rotated_height
                    width = current_width
                elif aspect_ratio == 0:
                    width = rotated_width
                    height = current_height
                else:
                    width = min(rotated_width, rotated_height * aspect_ratio)
                    height = width / aspect_ratio
            else:
                width, height = rotated_width, rotated_height
        else:
            if aspect_ratio is not None:
                if math.isinf(aspect_ratio):
                    height = rotated_width
                    width = current_width
                elif aspect_ratio == 0:
                    width = rotated_height
                    height = current_height
                else:
                    width = min(rotated_height, rotated_width * aspect_ratio)
                    height = width / aspect_ratio
            else:
                width, height = rotated_height, rotated_width

    # Handle special case for angles like 45°, 135°, etc.
    elif cos_2_angle == 0:
        sqrt2_min_dim = math.sqrt(2) * min(rotated_width, rotated_height)
        if aspect_ratio is not None:
            if math.isinf(aspect_ratio):
                width = current_width
                height = sqrt2_min_dim - width
            elif aspect_ratio == 0:
                height = current_height
                width = sqrt2_min_dim - height
            else:
                height = sqrt2_min_dim / (aspect_ratio + 1)
                width = height * aspect_ratio
        else:
            # Assume equal width and height for square-like shapes.
            width = height = sqrt2_min_dim / 2

    # General case for arbitrary angles.
    else:
        if aspect_ratio is not None:
            if math.isinf(aspect_ratio):
                width = current_width
                height = min((rotated_width - width * cos_angle) / sin_angle,
                             (rotated_height - width * sin_angle) / cos_angle)
            elif aspect_ratio == 0:
                height = current_height
                width = min((rotated_width - height * sin_angle) / cos_angle,
                            (rotated_height - height * cos_angle) / sin_angle)
            else:
                height = min(rotated_width / (aspect_ratio * cos_angle + sin_angle),
                             rotated_height / (aspect_ratio * sin_angle + cos_angle))
                width = height * aspect_ratio
        else:
            width = abs((rotated_width * cos_angle - rotated_height * sin_angle) / cos_2_angle)
            height = abs(rotated_height - width * sin_angle) / cos_angle

    return width, height
