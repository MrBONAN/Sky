import math
from datetime import datetime

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from StarDataclass import Star
from StarParser import StarParser
from StarParser import StarPositionUpdater


class SkyWidget(QGLWidget):
    headLatitudeChanged = pyqtSignal(float)
    headLongitudeChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super(SkyWidget, self).__init__(parent)

        self._latitude: float = 57.0
        self._latitude_max: int = 90
        self._latitude_min: int = -90

        self._longitude: float = 61.0
        self._longitude_max: int = 180
        self._longitude_min: int = -180

        self._fov: float = 45.0
        self._max_fov: int = 90
        self._min_fov: int = 10

        self._head_latitude: float = 0.0
        self._head_latitude_max: int = 90
        self._head_latitude_min: int = -90

        self._head_longitude: float = 0.0
        self._head_longitude_max: int = 180
        self._head_longitude_min: int = -180

        self._last_mouse_pos = None
        self._rotation_sensitivity = 0.057

        self._date = datetime(2000, 1, 1, 12, 0)

        stars = StarParser.read_database()
        self._stars = stars

        self.update_date(self._date)

        r = 1.0
        latitudes = 15
        longitudes = 25
        self.sphere_grid = self.generate_sphere_grid(r, latitudes, longitudes)
        self._ground_vertices = self._generate_ground_vertices(r, longitudes)

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
        self.update_projection()

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glRotatef(-90, 0, 1, 0)


        glRotatef(-90, 0, 0, 1)
        glRotatef(self._head_latitude, 0, 0, 1)
        glRotatef(self._head_longitude, 1, 0, 0)

        glRotatef(90, 0, 0, 1)
        self._draw_ground()
        glRotatef(-90, 0, 0, 1)

        glRotatef(-self._latitude, 0.0, 1.0, 0.0)
        glRotatef(-self._longitude, 0.0, 0.0, 1.0)

        self.draw_grid()

        self._draw_stars(self._stars_by_groups)

    @classmethod
    def generate_sphere_grid(cls, r: float, latitudes: int, longitudes: int) -> list[list[tuple[float, float, float]]]:
        sphere = [[None] * longitudes for _ in range(1, latitudes)]
        for longitude in range(longitudes):
            phi = (longitude / longitudes) * 2 * math.pi
            for latitude in range(1, latitudes):
                theta = (latitude / latitudes) * math.pi - math.pi / 2
                x = r * math.cos(theta) * math.cos(phi)
                y = r * math.cos(theta) * math.sin(phi)
                z = r * math.sin(theta)
                sphere[latitude - 1][longitude] = (x, y, z)
        return sphere

    def draw_grid(self) -> None:
        sphere_grid = self.sphere_grid
        glColor3f(0.2, 0.5, 0.8)

        for longitude in range(len(sphere_grid[0])):
            glBegin(GL_LINE_STRIP)
            for latitude in sphere_grid:
                glVertex3f(*latitude[longitude])
            glEnd()

        for latitude in sphere_grid:
            glBegin(GL_LINE_LOOP)
            for longitude in range(len(latitude)):
                glVertex3f(*latitude[longitude])
            glEnd()

    def _draw_ground(self):
        glColor3f(0.11, 0.65, 0.14)
        glBegin(GL_TRIANGLE_FAN)
        for point in self._ground_vertices:
            glVertex3f(*point)
        glEnd()

    def _generate_ground_vertices(self, r: float, sides_count: int):
        vertices = [(0, -0.5, 0)]
        angle = 2 * math.pi / sides_count
        for i in range(sides_count + 1):
            vertices.append(
                (r * math.cos(i * angle), 0, r * math.sin(i * angle)))
        return vertices

    def _draw_stars(self, stars_by_groups: dict[int, list[Star]]) -> None:
        glColor3f(1.0, 1.0, 1.0)

        min_size = 1.0
        max_size = 5.5
        num_groups = 10

        for size, stars in stars_by_groups.items():
            inverted_size = num_groups - size + 1

            scaled_size = min_size + (max_size - min_size) * (
                        inverted_size / num_groups) ** 8.5

            glPointSize(scaled_size)
            glBegin(GL_POINTS)
            for star in stars:
                x,y,z = star.get_vector().extract_coords()
                glVertex3f(x,y,z)
            glEnd()

    def _separate_stars_by_groups(self, stars: list[Star], sizes_range: list[int]) -> dict[int, list[Star]]:
        stars_by_size = {size: [] for size in sizes_range}
        stars = sorted(stars, key=lambda star: star.get_magnitude())
        group_len = max(1, int(len(stars) / len(sizes_range)))
        for i, star in enumerate(stars):
            index = i // group_len
            if index >= len(sizes_range):
                index = len(sizes_range)-1
            stars_by_size[sizes_range[index]].append(star)
        return stars_by_size

    def update_date(self, new_date):
        self._date = new_date
        base_date = datetime(2000, 1, 1, 12, 0)
        delta_time = new_date - base_date

        self._updated_stars = StarPositionUpdater.update_positions(self._stars, delta_time)
        self._stars_by_groups = self._separate_stars_by_groups(self._updated_stars, list(range(1, 10)))
        self.update()

    def get_current_date_text(self):
        return self._date.strftime("%Y/%m/%d/%H/%M")

    def set_latitude(self, value: int) -> None:
        value = max(min(self._latitude_max, value), self._latitude_min)
        self._latitude = value
        self.update()

    def set_longitude(self, value: int) -> None:
        value = (value - self._longitude_min) % (self._longitude_max - self._longitude_min) + self._longitude_min
        self._longitude = value
        self.update()

    def set_head_latitude(self, value: float) -> None:
        value = max(min(self._head_latitude_max, value), self._head_latitude_min)
        self._head_latitude = value
        self.headLatitudeChanged.emit(self._head_latitude)
        self.update()

    def set_head_longitude(self, value: float) -> None:
        value = (value - self._head_longitude_min) % (
                self._head_longitude_max - self._head_longitude_min) + self._head_longitude_min
        self._head_longitude = value
        self.headLongitudeChanged.emit(self._head_longitude)
        self.update()

    def update_zoom(self, value: int) -> None:
        self._fov = value
        self._fov = max(self._min_fov, min(self._fov, self._max_fov))
        self.update_projection()
        self.update()

    def update_projection(self) -> None:
        aspect = self.width() / self.height() if self.height() != 0 else 1
        aspect = 1.8
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self._fov, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._last_mouse_pos is None:
            return

        delta_x = event.x() - self._last_mouse_pos.x()
        delta_y = event.y() - self._last_mouse_pos.y()

        longitude_delta = delta_x * self._rotation_sensitivity
        latitude_delta = delta_y * self._rotation_sensitivity

        new_head_longitude = self._head_longitude + longitude_delta
        new_head_latitude = self._head_latitude + latitude_delta

        self.set_head_longitude(new_head_longitude)
        self.set_head_latitude(new_head_latitude)

        self._last_mouse_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = None