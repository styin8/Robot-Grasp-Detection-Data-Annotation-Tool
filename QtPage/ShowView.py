from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QListWidget, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QImageReader, QImage, QFont, QPainter, QPen, QCursor
import numpy as np
from typing import Tuple
import math
from skimage.draw import polygon  # Import polygon from skimage.draw


class ClickableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.parent_view = None

    def mousePressEvent(self, event):
        if self.parent_view:
            # Convert mouse coordinates to image coordinates
            mapped_pos = self.parent_view.map_to_image_coordinates(event.pos())
            if mapped_pos:
                event.mapped_pos = mapped_pos
                self.parent_view.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.parent_view:
            # Convert mouse coordinates to image coordinates
            mapped_pos = self.parent_view.map_to_image_coordinates(event.pos())
            if mapped_pos:
                event.mapped_pos = mapped_pos
                self.parent_view.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.parent_view:
            # Convert mouse coordinates to image coordinates
            mapped_pos = self.parent_view.map_to_image_coordinates(event.pos())
            if mapped_pos:
                event.mapped_pos = mapped_pos
                self.parent_view.mouseReleaseEvent(event)


class ShowView():
    def __init__(self) -> None:
        # Component
        self.is_drawing = False
        self.start_point = None
        self.end_point = None
        self.current_pixmap = None
        self.temp_pixmap = None
        self.image_rect = None  # Store actual display area of the image

        self.origin_image = ClickableLabel(
            "Please add and select an image :)")
        self.origin_image.parent_view = self

        font = QFont()
        font.setPointSize(20)
        self.origin_image.setFont(font)
        self.origin_image.setAlignment(Qt.AlignCenter)
        self.origin_image.setGeometry(100, 100, 640, 480)
        self.origin_image.setFixedSize(640, 480)

        self.quality_image = QLabel()
        self.quality_image.setAlignment(Qt.AlignCenter)

        self.angle_image = QLabel()
        self.angle_image.setAlignment(Qt.AlignCenter)

        self.width_image = QLabel()
        self.width_image.setAlignment(Qt.AlignCenter)

        # Add labels
        self.quality_label = QLabel("")  # Initialize without text
        self.quality_label.setAlignment(Qt.AlignCenter)
        self.angle_label = QLabel("")    # Initialize without text
        self.angle_label.setAlignment(Qt.AlignCenter)
        self.width_label = QLabel("")    # Initialize without text
        self.width_label.setAlignment(Qt.AlignCenter)

        # Create color scale labels
        self.colorbar_label = QLabel()
        self.width_colorbar_label = QLabel()
        self.angle_colorbar_label = QLabel()  # Add angle scale label

        self.colorbar_label.setFixedWidth(20)
        self.width_colorbar_label.setFixedWidth(20)
        self.angle_colorbar_label.setFixedWidth(20)  # Set width

        self.colorbar_label.setAlignment(Qt.AlignCenter)
        self.width_colorbar_label.setAlignment(Qt.AlignCenter)
        self.angle_colorbar_label.setAlignment(Qt.AlignCenter)

        # Layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Origin Image
        self.origin_groupbox = QGroupBox("Original Image")
        self.origin_groupbox.setAlignment(Qt.AlignCenter)
        self.origin_layout = QHBoxLayout()
        self.origin_layout.addWidget(self.origin_image)
        self.origin_groupbox.setLayout(self.origin_layout)

        # Preview
        self.preview_groupbox = QGroupBox("Preview Images")
        self.preview_groupbox.setAlignment(Qt.AlignCenter)
        self.preview_layout = QVBoxLayout()  # Vertical layout

        # Create horizontal layout for preview images
        self.preview_images_layout = QHBoxLayout()
        self.preview_images_layout.setAlignment(Qt.AlignCenter)

        # Create vertical layout for each preview image
        quality_container = QVBoxLayout()    # Vertical layout for image and label
        quality_preview = QHBoxLayout()      # Horizontal layout for scale and image
        quality_preview.addWidget(self.colorbar_label)  # Add scale first
        quality_preview.addWidget(self.quality_image)   # Then add image
        quality_preview.setAlignment(
            self.colorbar_label, Qt.AlignVCenter)  # Vertical center alignment
        quality_container.addLayout(quality_preview)    # Add horizontal layout
        quality_container.addWidget(self.quality_label)  # Add label

        angle_container = QVBoxLayout()
        angle_preview = QHBoxLayout()
        angle_preview.addWidget(self.angle_colorbar_label)
        angle_preview.addWidget(self.angle_image)
        angle_preview.setAlignment(
            self.angle_colorbar_label, Qt.AlignVCenter)
        angle_container.addLayout(angle_preview)
        angle_container.addWidget(self.angle_label)

        width_container = QVBoxLayout()
        width_preview = QHBoxLayout()
        width_preview.addWidget(self.width_colorbar_label)
        width_preview.addWidget(self.width_image)
        width_preview.setAlignment(self.width_colorbar_label, Qt.AlignVCenter)
        width_container.addLayout(width_preview)
        width_container.addWidget(self.width_label)

        # Add each container to preview images layout
        preview_widget1 = QWidget()
        preview_widget1.setLayout(quality_container)
        preview_widget2 = QWidget()
        preview_widget2.setLayout(angle_container)
        preview_widget3 = QWidget()
        preview_widget3.setLayout(width_container)

        self.preview_images_layout.addWidget(preview_widget1)
        self.preview_images_layout.addWidget(preview_widget2)
        self.preview_images_layout.addWidget(preview_widget3)

        # Add preview images layout to preview group layout
        self.preview_layout.addLayout(self.preview_images_layout)
        self.preview_groupbox.setLayout(self.preview_layout)

        self.layout.addWidget(self.origin_groupbox, 3)
        self.layout.addWidget(self.preview_groupbox, 2)

        # Add callback function property
        self.on_drawing_finished = None

        # Add new grasp line information storage
        self.grasp_lines = []  # Store all grasp line information
        self.current_grasp_line = None  # Currently selected grasp line

        # Add related properties
        self.quality_map = None
        self.angle_map = None
        self.width_map = None

        self.click_tolerance = 5  # Half width of center axis clickable area (total width 10px)

        # Add fine-tuning related properties
        self.fine_tune_mode = None  # 'up', 'down', or 'select'
        self.fine_tune_radius = 10  # Changed to 10 (was 20)
        self.fine_tune_strength = 0.1  # Fine-tuning strength per adjustment

        # Modify mouse tracking
        self.origin_image.setMouseTracking(True)
        self.origin_image.setCursor(Qt.ArrowCursor)

        self.current_file_path = None  # Add this line

    def map_to_image_coordinates(self, pos):
        """Map window coordinates to image coordinates"""
        if not self.image_rect or not self.current_pixmap:
            return None

        # Calculate coordinates relative to image display area
        x = pos.x() - self.image_rect.x()
        y = pos.y() - self.image_rect.y()

        # Check if within image area
        if x < 0 or y < 0 or x > self.image_rect.width() or y > self.image_rect.height():
            return None

        return QPoint(x, y)

    def update_image_rect(self):
        """Update image display area information"""
        if not self.current_pixmap:
            return

        # Calculate scaled image size maintaining aspect ratio
        label_size = self.origin_image.size()
        scaled_size = self.current_pixmap.size().scaled(
            label_size, Qt.KeepAspectRatio)

        # Calculate actual display area of image in Label
        x = (label_size.width() - scaled_size.width()) // 2
        y = (label_size.height() - scaled_size.height()) // 2

        self.image_rect = QRect(
            x, y, scaled_size.width(), scaled_size.height())

    def distance_to_line(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        px = point[0]
        py = point[1]
        x1 = line_start[0]
        y1 = line_start[1]
        x2 = line_end[0]
        y2 = line_end[1]

        # Calculate square of line segment length
        l2 = (x2 - x1) ** 2 + (y2 - y1) ** 2

        if l2 == 0:
            # If line segment length is 0, return distance to endpoint
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # Calculate projection position parameter t of point to line segment
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))

        # Calculate projection point coordinates
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        # Return distance from point to projection point
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

    def find_nearest_line(self, point):
        """Find the grasp line nearest to click position"""
        if not self.grasp_lines:
            return None

        min_distance = float('inf')
        nearest_line = None

        for line in self.grasp_lines:
            distance = self.distance_to_line(
                point,
                line['start'],
                line['end']
            )
            if distance < min_distance and distance <= self.click_tolerance:
                min_distance = distance
                nearest_line = line

        return nearest_line

    def mousePressEvent(self, event):
        if self.fine_tune_mode in ['up', 'down'] and event.button() == Qt.LeftButton:
            # Call update_quality_value method to update value
            self.update_quality_value(event.mapped_pos)
        elif self.is_drawing and event.button() == Qt.LeftButton:
            # Handle click in drawing mode
            self.start_point = event.mapped_pos
            if self.current_pixmap:
                self.temp_pixmap = self.current_pixmap.copy()
        elif not self.is_drawing and event.button() == Qt.LeftButton:
            # Non-drawing mode, check if clicked on a center axis
            clicked_point = (event.mapped_pos.x(), event.mapped_pos.y())
            nearest_line = self.find_nearest_line(clicked_point)

            if nearest_line:
                # Update currently selected grasp line
                self.current_grasp_line = nearest_line

                # Redraw all lines, highlight selected line
                if self.current_pixmap:
                    self.current_pixmap = self.temp_pixmap.copy()
                    painter = QPainter(self.current_pixmap)

                    # Draw all unselected lines first
                    for line in self.grasp_lines:
                        if line != self.current_grasp_line:
                            # Draw red center axis
                            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                            painter.drawLine(
                                int(line['start'][0]), int(line['start'][1]),
                                int(line['end'][0]), int(line['end'][1])
                            )

                            # If there's a perpendicular line, draw blue perpendicular line
                            if line['perp_line']:
                                painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                                painter.drawLine(
                                    int(line['perp_line']['start'][0]),
                                    int(line['perp_line']['start'][1]),
                                    int(line['perp_line']['end'][0]),
                                    int(line['perp_line']['end'][1])
                                )

                    # Draw selected line (using thicker line)
                    painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                    painter.drawLine(
                        int(self.current_grasp_line['start'][0]),
                        int(self.current_grasp_line['start'][1]),
                        int(self.current_grasp_line['end'][0]),
                        int(self.current_grasp_line['end'][1])
                    )

                    # If selected line has perpendicular line, draw it with thicker line
                    if self.current_grasp_line['perp_line']:
                        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                        painter.drawLine(
                            int(self.current_grasp_line['perp_line']
                                ['start'][0]),
                            int(self.current_grasp_line['perp_line']
                                ['start'][1]),
                            int(self.current_grasp_line['perp_line']
                                ['end'][0]),
                            int(self.current_grasp_line['perp_line']['end'][1])
                        )

                    painter.end()
                    self.origin_image.setPixmap(
                        self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

    def mouseMoveEvent(self, event):
        if self.fine_tune_mode in ['up', 'down'] and event.buttons() & Qt.LeftButton:
            # When mouse is pressed and moved, also update value
            self.update_quality_value(event.mapped_pos)
        elif self.is_drawing and self.start_point:
            if self.temp_pixmap:
                drawing_pixmap = self.temp_pixmap.copy()
                painter = QPainter(drawing_pixmap)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawLine(self.start_point, event.mapped_pos)
                painter.end()
                self.origin_image.setPixmap(
                    drawing_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

    def mouseReleaseEvent(self, event):
        if self.is_drawing and event.button() == Qt.LeftButton and self.start_point:
            self.end_point = event.mapped_pos
            if self.current_pixmap:
                # Create new grasp line information
                grasp_line = {
                    'start': (self.start_point.x(), self.start_point.y()),
                    'end': (self.end_point.x(), self.end_point.y()),
                    'perp_line': None,  # Store perpendicular line information
                    'length': None,     # Store line segment length
                    'center': None,     # Store center point
                    'angle': None       # Store angle
                }

                # Calculate and store grasp line information
                dx = self.end_point.x() - self.start_point.x()
                dy = self.end_point.y() - self.start_point.y()
                grasp_line['length'] = math.sqrt(dx*dx + dy*dy)
                grasp_line['center'] = (
                    (self.start_point.x() + self.end_point.x()) / 2,
                    (self.start_point.y() + self.end_point.y()) / 2
                )
                grasp_line['angle'] = math.atan2(dy, dx)

                # Add to table
                self.grasp_lines.append(grasp_line)

                # Set as currently selected line
                self.current_grasp_line = grasp_line

                # Redraw all segments
                self.current_pixmap = self.temp_pixmap.copy()
                painter = QPainter(self.current_pixmap)

                # Draw all unselected lines first
                for line in self.grasp_lines:
                    if line != self.current_grasp_line:
                        # Draw red center axis
                        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                        painter.drawLine(
                            int(line['start'][0]), int(line['start'][1]),
                            int(line['end'][0]), int(line['end'][1])
                        )

                        # If there's a perpendicular line, draw blue perpendicular line
                        if line['perp_line']:
                            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                            painter.drawLine(
                                int(line['perp_line']['start'][0]),
                                int(line['perp_line']['start'][1]),
                                int(line['perp_line']['end'][0]),
                                int(line['perp_line']['end'][1])
                            )

                # Draw selected line (using thicker line)
                painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                painter.drawLine(
                    int(self.current_grasp_line['start'][0]),
                    int(self.current_grasp_line['start'][1]),
                    int(self.current_grasp_line['end'][0]),
                    int(self.current_grasp_line['end'][1])
                )

                painter.end()
                self.origin_image.setPixmap(
                    self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

                # Save current state
                self.temp_pixmap = self.current_pixmap.copy()

                print(
                    f"Added new grasp line from {grasp_line['start']} to {grasp_line['end']}")

            self.start_point = None
            self.end_point = None
            self.is_drawing = False

            if self.on_drawing_finished:
                self.on_drawing_finished()

    def draw_perpendicular_line(self, length_ratio=0.25):
        """Draw perpendicular line at center of currently selected grasp line"""
        if not self.current_grasp_line:
            return False

        # Calculate length of perpendicular line
        perp_length = self.current_grasp_line['length'] * length_ratio

        # Calculate angle of perpendicular line
        perp_angle = self.current_grasp_line['angle'] + math.pi/2

        # Calculate perpendicular line endpoints
        center = self.current_grasp_line['center']
        half_length = perp_length / 2
        start_x = center[0] - half_length * math.cos(perp_angle)
        start_y = center[1] - half_length * math.sin(perp_angle)
        end_x = center[0] + half_length * math.cos(perp_angle)
        end_y = center[1] + half_length * math.sin(perp_angle)

        # Store perpendicular line information
        self.current_grasp_line['perp_line'] = {
            'start': (start_x, start_y),
            'end': (end_x, end_y),
            'length_ratio': length_ratio
        }

        # Redraw all segments
        if self.current_pixmap:
            self.current_pixmap = self.temp_pixmap.copy()
            painter = QPainter(self.current_pixmap)

            # Draw all grasp lines
            for line in self.grasp_lines:
                # Draw red center axis first
                if line == self.current_grasp_line:
                    # Current selected line draw thicker
                    painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                else:
                    painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

                painter.drawLine(
                    int(line['start'][0]), int(line['start'][1]),
                    int(line['end'][0]), int(line['end'][1])
                )

                # If there's a perpendicular line, draw blue perpendicular line
                if line['perp_line']:
                    # Calculate perpendicular line endpoints
                    center = line['center']
                    perp_length = line['length'] * \
                        line['perp_line']['length_ratio']
                    half_length = perp_length / 2
                    perp_angle = line['angle'] + math.pi/2

                    start_x = center[0] - half_length * math.cos(perp_angle)
                    start_y = center[1] - half_length * math.sin(perp_angle)
                    end_x = center[0] + half_length * math.cos(perp_angle)
                    end_y = center[1] + half_length * math.sin(perp_angle)

                    if line == self.current_grasp_line:
                        # Current selected line's perpendicular line draw thicker
                        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                    else:
                        painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

            painter.end()
            self.origin_image.setPixmap(
                self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))
            return True
        return False

    def update_perpendicular_line(self, length_ratio):
        """Update length of perpendicular line of currently selected grasp line"""
        if not self.current_grasp_line:
            return False

        # Update length ratio of perpendicular line of currently selected line
        if self.current_grasp_line['perp_line']:
            self.current_grasp_line['perp_line']['length_ratio'] = length_ratio

        # Redraw all segments
        if self.current_pixmap:
            self.current_pixmap = self.temp_pixmap.copy()
            painter = QPainter(self.current_pixmap)

            # Draw all grasp lines
            for line in self.grasp_lines:
                # Draw red center axis first
                if line == self.current_grasp_line:
                    # Current selected line draw thicker
                    painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
                else:
                    painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

                painter.drawLine(
                    int(line['start'][0]), int(line['start'][1]),
                    int(line['end'][0]), int(line['end'][1])
                )

                # If there's a perpendicular line, draw blue perpendicular line
                if line['perp_line']:
                    # Calculate perpendicular line endpoints
                    center = line['center']
                    perp_length = line['length'] * \
                        line['perp_line']['length_ratio']
                    half_length = perp_length / 2
                    perp_angle = line['angle'] + math.pi/2

                    start_x = center[0] - half_length * math.cos(perp_angle)
                    start_y = center[1] - half_length * math.sin(perp_angle)
                    end_x = center[0] + half_length * math.cos(perp_angle)
                    end_y = center[1] + half_length * math.sin(perp_angle)

                    if line == self.current_grasp_line:
                        # Current selected line's perpendicular line draw thicker
                        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
                    else:
                        painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

            painter.end()
            self.origin_image.setPixmap(
                self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))
            return True
        return False

    @staticmethod
    def init_label_image(width, height) -> Tuple[np.ndarray, QImage]:
        # Ensure width and height are integers
        width = int(width)
        height = int(height)
        # Use gray (128) instead of black (0)
        image = np.full((height, width), 200, dtype=np.uint8)  # Use light gray
        qimage = QImage(image.data,
                        width, height,
                        width,  # Add step length parameter
                        QImage.Format_Grayscale8)
        return image, qimage

    def generate_heatmaps(self):
        """Generate heatmap considering all labeled grasp lines"""
        if not self.image_rect or not self.grasp_lines:
            return False

        # Get original image size
        original_height = self.current_pixmap.height()
        original_width = self.current_pixmap.width()

        # Get preview image size
        preview_height = original_height // 2
        preview_width = original_width // 2

        # Create heatmap (using preview image size)
        self.quality_map = np.zeros(
            (preview_height, preview_width), dtype=np.float32)
        self.angle_map = np.zeros(
            (preview_height, preview_width), dtype=np.float32)
        self.width_map = np.zeros(
            (preview_height, preview_width), dtype=np.float32)

        # Used to track maximum value
        max_angle = float('-inf')
        max_width = float('-inf')

        # Draw blue lines on center axis of original image
        if self.current_pixmap:
            painter = QPainter(self.current_pixmap)
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))

            # Iterate through all grasp lines
            for grasp_line in self.grasp_lines:
                if not grasp_line['perp_line']:  # Skip lines without width annotation
                    continue

                # Calculate points uniformly distributed on center axis
                num_points = int(grasp_line['length'])  # One point per pixel

                dx = (grasp_line['end'][0] -
                      grasp_line['start'][0]) / (num_points - 1)
                dy = (grasp_line['end'][1] -
                      grasp_line['start'][1]) / (num_points - 1)

                # Calculate angle between center axis and positive x-axis direction
                dx_axis = grasp_line['end'][0] - grasp_line['start'][0]
                dy_axis = -(grasp_line['end'][1] - grasp_line['start'][1])
                angle_rad = math.atan2(dy_axis, dx_axis)
                angle_deg = math.degrees(angle_rad)

                # Ensure angle is between -90 and 90 degrees
                if angle_deg > 90:
                    angle_deg = angle_deg - 180
                elif angle_deg < -90:
                    angle_deg = angle_deg + 180

                # Update maximum angle value
                max_angle = max(max_angle, abs(angle_deg))

                prev_start_x, prev_start_y = None, None
                prev_end_x, prev_end_y = None, None

                # Draw vertical blue lines and update heatmap at each point
                for i in range(num_points):
                    # Original coordinates
                    center_x = grasp_line['start'][0] + dx * i
                    center_y = grasp_line['start'][1] + dy * i

                    # Calculate perpendicular line endpoints (original coordinates)
                    perp_length = grasp_line['length'] * \
                        grasp_line['perp_line']['length_ratio']
                    half_length = perp_length / 2
                    perp_angle = grasp_line['angle'] + math.pi/2

                    start_x = center_x - half_length * math.cos(perp_angle)
                    start_y = center_y - half_length * math.sin(perp_angle)
                    end_x = center_x + half_length * math.cos(perp_angle)
                    end_y = center_y + half_length * math.sin(perp_angle)

                    # Update maximum width value
                    max_width = max(max_width, perp_length)

                    # Draw vertical line (original)
                    painter.drawLine(
                        int(start_x), int(start_y),
                        int(end_x), int(end_y)
                    )

                    # Fill area between two vertical lines
                    if i > 0:  # From second point, connect previous and current vertical lines
                        # Create polygon vertex array (scaled to preview image size)
                        poly_y = np.array([
                            int(prev_start_y * preview_height / original_height),
                            int(prev_end_y * preview_height / original_height),
                            int(end_y * preview_height / original_height),
                            int(start_y * preview_height / original_height)
                        ])
                        poly_x = np.array([
                            int(prev_start_x * preview_width / original_width),
                            int(prev_end_x * preview_width / original_width),
                            int(end_x * preview_width / original_width),
                            int(start_x * preview_width / original_width)
                        ])

                        # Use polygon function to get all points inside polygon
                        rr, cc = polygon(
                            poly_y, poly_x, shape=(preview_height, preview_width))

                        # Calculate center line points (scaled to preview image size)
                        center_line_start = np.array([
                            int((prev_start_x + prev_end_x) / 2 *
                                preview_width / original_width),
                            int((prev_start_y + prev_end_y) / 2 *
                                preview_height / original_height)
                        ])
                        center_line_end = np.array([
                            int((start_x + end_x) / 2 *
                                preview_width / original_width),
                            int((start_y + end_y) / 2 *
                                preview_height / original_height)
                        ])

                        # Calculate Gaussian value for each point inside polygon
                        for y, x in zip(rr, cc):
                            point = np.array([x, y])
                            # Calculate distance from point to center line
                            dist = self.point_to_line_distance(
                                point, center_line_start, center_line_end)
                            # Calculate Gaussian value (sigma can be adjusted to change distribution width)
                            sigma = perp_length / \
                                (4 * original_height /
                                 preview_height)  # Adjust sigma to fit preview image size
                            gaussian_value = np.exp(-0.5 *
                                                    (dist ** 2) / (sigma ** 2))

                            # Update quality map (using Gaussian value)
                            self.quality_map[y, x] = max(
                                self.quality_map[y, x], gaussian_value)
                            # Update other maps (keep unchanged)
                            self.width_map[y, x] = perp_length
                            self.angle_map[y, x] = angle_deg

                    # Update previous point coordinates
                    prev_start_x, prev_start_y = start_x, start_y
                    prev_end_x, prev_end_y = end_x, end_y

            print(f"Maximum angle value: {angle_deg:.2f}°")
            print(f"Maximum width value: {perp_length:.2f}")

            painter.end()
            self.origin_image.setPixmap(
                self.current_pixmap.scaled(640, 480, Qt.KeepAspectRatio))

            # Update preview image display
            self.update_preview_images()
            return True

    def update_preview_images(self):
        """Update preview image display"""
        if all([self.quality_map is not None,
                self.angle_map is not None,
                self.width_map is not None]):

            # Convert to uint8 type and apply color mapping
            quality_colored = self.apply_colormap(self.quality_map)
            angle_colored = self.apply_colormap(self.angle_map)
            width_colored = self.apply_colormap(self.width_map)

            # Create QImage and display
            h, w = self.quality_map.shape

            quality_qimage = QImage(
                quality_colored.data, w, h, w * 3, QImage.Format_RGB888)
            self.quality_image.setPixmap(QPixmap.fromImage(quality_qimage))

            angle_qimage = QImage(angle_colored.data, w,
                                  h, w * 3, QImage.Format_RGB888)
            self.angle_image.setPixmap(QPixmap.fromImage(angle_qimage))

            width_qimage = QImage(width_colored.data, w,
                                  h, w * 3, QImage.Format_RGB888)
            self.width_image.setPixmap(QPixmap.fromImage(width_qimage))

            # Create and update color scale
            self.update_colorbar(h)
            self.update_width_colorbar(h)
            self.update_angle_colorbar(h)  # Add

    def apply_colormap(self, data):
        """Apply heatmap color mapping"""
        # Create colored image
        colored = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)

        # Use different normalization methods based on different types of data
        if data is self.quality_map:
            # quality_map is already 0-1 range, directly use
            normalized_data = np.clip(data, 0, 1)
        elif data is self.angle_map:
            # angle_map range is -90 to 90, normalize to 0-1
            normalized_data = (data + 90) / 180
        elif data is self.width_map:
            # width_map range is 0 to 150, normalize to 0-1
            normalized_data = data / 150
        else:
            # Default case, assume data is already normalized
            normalized_data = np.clip(data, 0, 1)

        # Convert to uint8 type
        data_uint8 = (normalized_data * 255).astype(np.uint8)

        # Apply color mapping (red to blue gradient)
        colored[..., 0] = data_uint8  # Red channel
        colored[..., 2] = 255 - data_uint8  # Blue channel

        return colored

    def set_fine_tune_mode(self, mode):
        """Set fine-tuning mode"""
        self.fine_tune_mode = mode
        if mode in ['up', 'down']:
            # Create circular cursor
            cursor = self.create_circle_cursor()
            self.origin_image.setCursor(cursor)
        else:
            self.origin_image.setCursor(Qt.ArrowCursor)

    def create_circle_cursor(self):
        """Create circular cursor"""
        cursor_size = self.fine_tune_radius * 2
        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.drawEllipse(0, 0, cursor_size-1, cursor_size-1)
        painter.end()

        return QCursor(pixmap)

    def update_colorbar(self, height):
        """Update quality heatmap color scale"""
        # Create a vertical color gradient bar
        colorbar = np.zeros((height, 20, 3), dtype=np.uint8)
        for i in range(height):
            value = 1.0 - (i / height)  # From top to bottom, value from 1 to 0
            colorbar[i, :, 0] = int(value * 255)  # Red channel
            colorbar[i, :, 2] = int((1 - value) * 255)  # Blue channel

        # Add maximum and minimum value labels
        font = QPainter()
        colorbar_pixmap = QPixmap(20, height)
        colorbar_qimage = QImage(
            colorbar.data, 20, height, 60, QImage.Format_RGB888)
        colorbar_pixmap.convertFromImage(colorbar_qimage)

        painter = QPainter(colorbar_pixmap)
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 8))

        # Draw maximum value at top
        painter.drawText(0, 10, "1.0")
        # Draw middle value
        painter.drawText(0, height//2, "0.5")
        # Draw minimum value
        painter.drawText(0, height-2, "0.0")

        painter.end()
        self.colorbar_label.setPixmap(colorbar_pixmap)

    def update_width_colorbar(self, height):
        """Update width heatmap color scale"""
        # Create a vertical color gradient bar
        colorbar = np.zeros((height, 20, 3), dtype=np.uint8)
        for i in range(height):
            value = 1.0 - (i / height)  # From top to bottom, value from 1 to 0
            colorbar[i, :, 0] = int(value * 255)  # Red channel
            colorbar[i, :, 2] = int((1 - value) * 255)  # Blue channel

        # Add maximum and minimum value labels
        font = QPainter()
        colorbar_pixmap = QPixmap(20, height)
        colorbar_qimage = QImage(
            colorbar.data, 20, height, 60, QImage.Format_RGB888)
        colorbar_pixmap.convertFromImage(colorbar_qimage)

        painter = QPainter(colorbar_pixmap)
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 8))

        # Draw maximum value at top
        painter.drawText(0, 10, "150")
        # Draw middle value
        painter.drawText(0, height//2, "75")
        # Draw minimum value
        painter.drawText(0, height-2, "0")

        painter.end()
        self.width_colorbar_label.setPixmap(colorbar_pixmap)

    def update_angle_colorbar(self, height):
        """Update angle heatmap color scale"""
        # Create a vertical color gradient bar
        colorbar = np.zeros((height, 20, 3), dtype=np.uint8)
        for i in range(height):
            value = 1.0 - (i / height)  # From top to bottom, value from 1 to 0
            colorbar[i, :, 0] = int(value * 255)  # Red channel
            colorbar[i, :, 2] = int((1 - value) * 255)  # Blue channel

        # Add maximum and minimum value labels
        font = QPainter()
        colorbar_pixmap = QPixmap(20, height)
        colorbar_qimage = QImage(
            colorbar.data, 20, height, 60, QImage.Format_RGB888)
        colorbar_pixmap.convertFromImage(colorbar_qimage)

        painter = QPainter(colorbar_pixmap)
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 8))

        # Draw maximum value at top
        painter.drawText(0, 10, "90°")
        # Draw middle value
        painter.drawText(0, height//2, "0°")
        # Draw minimum value
        painter.drawText(0, height-2, "-90°")

        painter.end()
        self.angle_colorbar_label.setPixmap(colorbar_pixmap)

    def point_in_quadrilateral(self, point, quad_points):
        """
        Check if point is inside quadrilateral
        point: Point to check [x, y]
        quad_points: Four vertices of quadrilateral [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        """
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        d1 = sign(point, quad_points[0], quad_points[1])
        d2 = sign(point, quad_points[1], quad_points[2])
        d3 = sign(point, quad_points[2], quad_points[3])
        d4 = sign(point, quad_points[3], quad_points[0])

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0)

        return not (has_neg and has_pos)

    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        if np.array_equal(line_start, line_end):
            return np.linalg.norm(point - line_start)

        line_vec = line_end - line_start
        point_vec = point - line_start
        line_length = np.linalg.norm(line_vec)
        line_unit_vec = line_vec / line_length
        projection_length = np.dot(point_vec, line_unit_vec)

        if projection_length < 0:
            return np.linalg.norm(point - line_start)
        elif projection_length > line_length:
            return np.linalg.norm(point - line_end)
        else:
            projection = line_start + line_unit_vec * projection_length
            return np.linalg.norm(point - projection)

    def update_quality_value(self, pos):
        """Update value of quality map"""
        # Convert to preview image coordinates
        preview_x = int(pos.x() / 2)
        preview_y = int(pos.y() / 2)

        # Update quality map
        if self.quality_map is not None:
            height, width = self.quality_map.shape
            radius = self.fine_tune_radius // 2  # Preview image radius

            # Update value in circular area
            for y in range(max(0, preview_y - radius), min(height, preview_y + radius)):
                for x in range(max(0, preview_x - radius), min(width, preview_x + radius)):
                    # Calculate distance to center
                    dist = math.sqrt((x - preview_x) ** 2 + (y - preview_y)**2)
                    if dist <= radius:
                        # Use Gaussian decay
                        factor = math.exp(-(dist**2)/(2*(radius/2)**2))
                        if self.fine_tune_mode == 'up':
                            self.quality_map[y, x] = min(
                                1.0, self.quality_map[y, x] + self.fine_tune_strength * factor)
                        else:  # down
                            self.quality_map[y, x] = max(
                                0.0, self.quality_map[y, x] - self.fine_tune_strength * factor)

            # Update preview image display
            self.update_preview_images()
