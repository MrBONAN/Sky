import math

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from StarDataclass import Star
from StarParser import StarParser
from StarParser import StarPositionUpdater
from datetime import datetime


class SkyWidget(QGLWidget):
    def __init__(self, parent=None):
        super(SkyWidget, self).__init__(parent)

        # Углы поворота неба
        self._latitude: float = 0.0
        self._latitude_max: int = 90
        self._latitude_min: int = -90

        self._longitude: float = 0.0
        self._longitude_max: int = 180
        self._longitude_min: int = -180

        # Поле зрения
        self._fov: float = 45.0
        self._max_fov: int = 90
        self._min_fov: int = 10

        # Углы поворота наблюдателя
        self._head_latitude: float = 0.0
        self._head_latitude_max: int = 90
        self._head_latitude_min: int = -90

        self._head_longitude: float = 0.0
        self._head_longitude_max: int = 180
        self._head_longitude_min: int = -180

        # Переменные для обработки событий мыши
        self._last_mouse_pos = None
        self._rotation_sensitivity = 0.057

        # Инициализируем дату
        self._date = datetime(2000, 1, 1, 12, 0)

        # Загрузка звезд из базы данных
        stars = StarParser.read_database()
        self._stars = stars  # Оригинальные позиции звезд

        # Обновляем позиции звезд в соответствии с текущей датой
        self.update_date(self._date)

        r = 1.0
        latitudes = 15
        longitudes = 25
        self.sphere_grid = self.generate_sphere_grid(r, latitudes, longitudes)

    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Тёмный фон
        glLineWidth(1.0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_POINT_SMOOTH)
        glDisable(GL_CULL_FACE)  # Отключаем отсечение граней для видимости изнутри

    def resizeGL(self, w: int, h: int) -> None:
        self.update_projection()

    def paintGL(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Отсчитываем от экватора
        glRotatef(-90, 0, 1, 0)

        # Наклоняем голову наблюдателя вверх/вниз
        glRotatef(-90, 0, 0, 1)  # смотрим сначала "вдаль"
        glRotatef(self._head_latitude, 0, 0, 1)
        # Наклоняем голову наблюдателя влево/вправо
        glRotatef(self._head_longitude, 1, 0, 0)

        # Устанавливаем наблюдателя на нужные координаты
        glRotatef(-self._latitude, 0.0, 1.0, 0.0)  # Вращение вокруг X оси (широта)
        glRotatef(-self._longitude, 0.0, 0.0, 1.0)  # Вращение вокруг Y оси (долгота)

        # Рисуем меридианы и параллели
        self.draw_grid()

        # Рисуем звезды
        self._draw_stars(self._stars_by_groups)

    @classmethod
    def generate_sphere_grid(cls, r: float, latitudes: int, longitudes: int) -> list[list[tuple[float, float, float]]]:
        # Первая координата - широта, потом долгота
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

        # Рисуем меридианы
        for longitude in range(len(sphere_grid[0])):
            glBegin(GL_LINE_STRIP)
            for latitude in sphere_grid:
                glVertex3f(*latitude[longitude])
            glEnd()

        # Рисуем параллели
        for latitude in sphere_grid:
            glBegin(GL_LINE_LOOP)
            for longitude in range(len(latitude)):
                glVertex3f(*latitude[longitude])
            glEnd()

    def _draw_stars(self, stars_by_groups: dict[int, list[Star]]) -> None:
        glColor3f(1.0, 1.0, 1.0)

        for size, stars in stars_by_groups.items():
            glPointSize((size / 5) ** 1.4)
            glBegin(GL_POINTS)
            for star in stars:
                glVertex3f(*star.get_vector())
            glEnd()

    def _separate_stars_by_groups(self, stars: list[Star], sizes_range: list[int]) -> dict[int, list[Star]]:
        min_magnitude = min(star.magnitude for star in stars)
        max_magnitude = max(star.magnitude for star in stars)
        min_pixel_size = 0
        max_pixel_size = len(sizes_range)
        stars_by_size = {size: [] for size in sizes_range}
        for star in stars:
            size = self._calculate_star_size(star, min_magnitude, max_magnitude, min_pixel_size, max_pixel_size)
            size = sizes_range[int(min(size, max_pixel_size - 1))]
            stars_by_size[size].append(star)
        return stars_by_size

    def _calculate_star_size(self, star: Star, min_magnitude: float, max_magnitude: float,
                             min_pixel_size: int, max_pixel_size: int) -> float:
        magnitude_coeff = (star.magnitude - min_magnitude) / (max_magnitude - min_magnitude)
        star_size = (max_pixel_size - min_pixel_size) * magnitude_coeff + min_pixel_size
        return star_size

    def set_latitude(self, value: int) -> None:
        value = max(min(self._latitude_max, value), self._latitude_min)
        self._latitude = value
        self.update()

    def set_longitude(self, value: int) -> None:
        value = (value - self._longitude_min) % (self._longitude_max - self._longitude_min) + self._longitude_min
        self._longitude = value
        self.update()

    def set_head_latitude(self, value: int) -> None:
        value = max(min(self._head_latitude_max, value), self._head_latitude_min)
        self._head_latitude = value
        self.update()

    def set_head_longitude(self, value: int) -> None:
        value = (value - self._head_longitude_min) % (
                self._head_longitude_max - self._head_longitude_min) + self._head_longitude_min
        self._head_longitude = value
        self.update()

    def update_zoom(self, value: int) -> None:
        self._fov = value  # Значение уже в градусах
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

    # Методы для обработки событий мыши
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._last_mouse_pos is None:
            return

        delta_x = event.x() - self._last_mouse_pos.x()
        delta_y = event.y() - self._last_mouse_pos.y()

        # Обновляем longitude и latitude на основе движения мыши
        longitude_delta = delta_x * self._rotation_sensitivity
        latitude_delta = delta_y * self._rotation_sensitivity  # Отрицательный знак для естественного ощущения

        # Устанавливаем новые значения углов
        self.set_head_longitude(self._head_longitude + longitude_delta)
        self.set_head_latitude(self._head_latitude + latitude_delta)

        self._last_mouse_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = None

    def update_date(self, new_date):
        self._date = new_date
        # Вычисляем разницу во времени от базовой даты
        base_date = datetime(2000, 1, 1, 12, 0)
        delta_time = new_date - base_date

        # Обновляем позиции звезд
        self._updated_stars = StarPositionUpdater.update_positions(self._stars, delta_time)
        self._stars_by_groups = self._separate_stars_by_groups(self._updated_stars, list(range(1, 20, 2)))
        self.update()

    def get_current_date_text(self):
        return self._date.strftime("%Y/%m/%d/%H/%M")
