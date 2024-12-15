import math
from datetime import datetime

from PyQt5.QtGui import QMouseEvent, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from star_dataclass import Star, Vector
from star_parser import StarParser, StarPositionUpdater
from settings import DATE_FORMAT, AngleConfig


class SkyWidget(QGLWidget):
    """
    Виджет для отображения звездного неба с использованием OpenGL.
    """
    headLatitudeChanged = pyqtSignal(float)
    headLongitudeChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super(SkyWidget, self).__init__(parent)

        self.latitude = AngleConfig(value=57.0, min_value=-90, max_value=90)
        self.longitude = AngleConfig(value=61.0, min_value=-180, max_value=180)
        self.fov = AngleConfig(value=45.0, min_value=10, max_value=90)
        self.head_latitude = AngleConfig(value=0.0, min_value=-90, max_value=90)
        self.head_longitude = AngleConfig(value=0.0, min_value=-180, max_value=180)

        self._last_mouse_pos = None
        self._rotation_sensitivity = 0.057

        self._date = datetime(2000, 1, 1, 12, 0)
        self._stars = StarParser.read_database()

        self._min_magnitude = -1.0
        self._max_magnitude = 6.0
        self._filtered_stars = []

        self.update_date(self._date)

        r = 1.0
        latitudes = 15
        longitudes = 25
        self.sphere_grid = self.generate_sphere_grid(r, latitudes, longitudes)
        self._ground_vertices = self._generate_ground_vertices(r, longitudes)

        self.direction_font = QFont("Arial", 24)

    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glLineWidth(1.0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_POINT_SMOOTH)
        glDisable(GL_CULL_FACE)

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, w, h)
        self.update_projection()

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 0, 0, 1)

        self.apply_head_orientation()

        glRotatef(90, 0, 0, 1)
        self._draw_ground()

        self._draw_cardinal_points()

        glRotatef(-90, 0, 0, 1)

        self.apply_scene_orientation()

        self.draw_grid()

        self._draw_stars()

    def apply_head_orientation(self):
        glRotatef(self.head_latitude.value, 0, 0, 1)
        glRotatef(self.head_longitude.value, 1, 0, 0)

    def apply_scene_orientation(self):
        glRotatef(-self.latitude.value, 0.0, 1.0, 0.0)
        glRotatef(-self.longitude.value, 0.0, 0.0, 1.0)

    @classmethod
    def generate_sphere_grid(cls, r: float, latitudes: int, longitudes: int) -> list[list[Vector]]:
        sphere_grid: list[list[Vector]] = [
            [Vector(0.0, 0.0, 0.0) for _ in range(longitudes)]
            for _ in range(1, latitudes)
        ]

        for longitude in range(longitudes):
            phi = (longitude / longitudes) * 2 * math.pi
            for latitude in range(1, latitudes):
                theta = (latitude / latitudes) * math.pi - math.pi / 2
                coord_x = r * math.cos(theta) * math.cos(phi)
                coord_y = r * math.cos(theta) * math.sin(phi)
                coord_z = r * math.sin(theta)
                sphere_grid[latitude - 1][longitude] = Vector(coord_x, coord_y, coord_z)

        return sphere_grid

    @staticmethod
    def _generate_ground_vertices(r: float, sides_count: int) -> list[tuple[float, float, float]]:
        vertices = [(0, -0.5, 0)]
        angle = 2 * math.pi / sides_count
        for i in range(sides_count + 1):
            vertices.append(
                (r * math.cos(i * angle), 0, r * math.sin(i * angle))
            )
        return vertices

    def draw_grid(self) -> None:
        sphere_grid = self.sphere_grid
        glColor3f(0.2, 0.5, 0.8)

        for longitude in range(len(sphere_grid[0])):
            glBegin(GL_LINE_STRIP)
            for latitude in sphere_grid:
                vector = latitude[longitude]
                glVertex3f(vector.x, vector.y, vector.z)
            glEnd()

        for latitude in sphere_grid:
            glBegin(GL_LINE_LOOP)
            for longitude in range(len(latitude)):
                vector = latitude[longitude]
                glVertex3f(vector.x, vector.y, vector.z)
            glEnd()

    def _draw_ground(self):
        glColor3f(0.11, 0.65, 0.14)
        glBegin(GL_TRIANGLE_FAN)
        for point in self._ground_vertices:
            glVertex3f(*point)
        glEnd()

    def _draw_cardinal_points(self):
        glColor3f(1.0, 1.0, 1.0)

        directions = [
            (0.0, 0.01, 1.0, "N"),
            (0.0, 0.01, -1.0, "S"),
            (1.0, 0.01, 0.0, "W"),
            (-1.0, 0.01, 0.0, "E")
        ]
        for x, y, z, label in directions:
            self.renderText(x, y, z, label, self.direction_font)

    def _draw_stars(self):
        max_mag = 6.0
        min_rad = 1.0
        k = 0.4

        spectral_colors = {
            'O': (0.7, 0.8, 1.0),
            'B': (0.75, 0.8, 1.0),
            'A': (0.8, 0.8, 1.0),
            'F': (0.9, 0.9, 1.0),
            'G': (1.0, 1.0, 0.8),
            'K': (1.0, 0.9, 0.6),
            'M': (1.0, 0.7, 0.5)
        }

        for star in self._filtered_stars:
            magnitude = star.get_magnitude()
            spectral_class = star.get_spectral_class() or ""
            spectral_class = spectral_class.strip().upper()

            main_class = None
            for c in spectral_class:
                if c in spectral_colors.keys():
                    main_class = c
                    break

            if main_class is None:
                main_class = 'A'

            color = spectral_colors.get(main_class, (1.0, 1.0, 1.0))

            size = min_rad * math.exp(k * (max_mag - magnitude))
            glPointSize(size)

            glColor3f(*color)

            glBegin(GL_POINTS)
            x, y, z = star.get_vector().extract_coords()
            glVertex3f(x, y, z)
            glEnd()

    def set_magnitude_range(self, min_mag: float, max_mag: float) -> None:
        self._min_magnitude = min_mag
        self._max_magnitude = max_mag
        self.update_stars_by_magnitude()

    def update_stars_by_magnitude(self):
        self._filtered_stars = [
            star for star in self._stars
            if self._min_magnitude <= star.get_magnitude() <= self._max_magnitude
        ]
        self.update()

    def update_date(self, new_date: datetime):
        self._date = new_date
        base_date = datetime(2000, 1, 1, 12, 0)
        delta_time = new_date - base_date

        self._updated_stars = StarPositionUpdater.update_positions(self._stars, delta_time)
        self._stars = self._updated_stars
        self.update_stars_by_magnitude()

    def get_current_date_text(self) -> str:
        return self._date.strftime(DATE_FORMAT)

    def set_latitude(self, value: int) -> None:
        value = max(self.latitude.min_value, min(self.latitude.max_value, value))
        self.latitude.value = value
        self.update()

    def set_longitude(self, value: int) -> None:
        range_min, range_max = self.longitude.min_value, self.longitude.max_value
        value = (value - range_min) % (range_max - range_min) + range_min
        self.longitude.value = value
        self.update()

    def set_head_latitude(self, value: float) -> None:
        if self.head_latitude.min_value < value < self.head_latitude.max_value:
            self.head_latitude.value = value
            self.headLatitudeChanged.emit(self.head_latitude.value)
            self.update()

    def set_head_longitude(self, value: float) -> None:
        range_min, range_max = self.head_longitude.min_value, self.head_longitude.max_value
        value = (value - range_min) % (range_max - range_min) + range_min
        self.head_longitude.value = value
        self.headLongitudeChanged.emit(self.head_longitude.value)
        self.update()

    def update_zoom(self, value: int) -> None:
        self.fov.value = max(self.fov.min_value, min(self.fov.max_value, value))
        self.update_projection()
        self.update()

    def update_projection(self) -> None:
        aspect = 1.8
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov.value, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._last_mouse_pos is None:
            return

        delta_x = event.x() - self._last_mouse_pos.x()
        delta_y = event.y() - self._last_mouse_pos.y()

        longitude_delta = delta_x * self._rotation_sensitivity
        latitude_delta = delta_y * self._rotation_sensitivity

        new_head_longitude = self.head_longitude.value + longitude_delta
        new_head_latitude = self.head_latitude.value + latitude_delta

        self.set_head_longitude(new_head_longitude)
        self.set_head_latitude(new_head_latitude)

        self._last_mouse_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = None
        super().mouseReleaseEvent(event)
