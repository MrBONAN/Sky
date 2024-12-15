import math
from datetime import datetime

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from star_dataclass import Star, Vector
from star_parser import StarParser, StarPositionUpdater
from settings import DATE_FORMAT,AngleConfig



class SkyWidget(QGLWidget):
    """
    Виджет для отображения звездного неба с использованием OpenGL.
    """
    headLatitudeChanged = pyqtSignal(float)
    headLongitudeChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super(SkyWidget, self).__init__(parent)

        # Конфигурации углов
        self.latitude = AngleConfig(value=57.0, min_value=-90, max_value=90)
        self.longitude = AngleConfig(value=61.0, min_value=-180, max_value=180)
        self.fov = AngleConfig(value=45.0, min_value=10, max_value=90)
        self.head_latitude = AngleConfig(value=0.0, min_value=-90,
                                         max_value=90)
        self.head_longitude = AngleConfig(value=0.0, min_value=-180,
                                          max_value=180)

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
        """
        Инициализирует параметры OpenGL.
        """
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
        """
        Обрабатывает изменение размера окна.

        :param w: Новая ширина.
        :param h: Новая высота.
        """
        self.update_projection()

    def paintGL(self) -> None:
        """
        Отрисовывает сцену.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 0, 0, 1)

        self.apply_head_orientation()

        glRotatef(90, 0, 0, 1)
        self._draw_ground()
        glRotatef(-90, 0, 0, 1)

        self.apply_scene_orientation()

        self.draw_grid()
        self._draw_stars(self._stars_by_groups)

    def apply_head_orientation(self):
        """
        Применяет трансформации для наклона головы.
        """
        glRotatef(self.head_latitude.value, 0, 0, 1)
        glRotatef(self.head_longitude.value, 1, 0, 0)

    def apply_scene_orientation(self):
        """
        Применяет трансформации для ориентации сцены.
        """
        glRotatef(-self.latitude.value, 0.0, 1.0, 0.0)
        glRotatef(-self.longitude.value, 0.0, 0.0, 1.0)

    @classmethod
    def generate_sphere_grid(cls, r: float, latitudes: int, longitudes: int) -> \
            list[list[Vector]]:
        """
        Генерирует сетку сферы.

        :param r: Радиус сферы.
        :param latitudes: Количество широт.
        :param longitudes: Количество долгот.
        :return: Сетка сферы.
        """
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
                sphere_grid[latitude - 1][longitude] = Vector(coord_x, coord_y,
                                                              coord_z)

        return sphere_grid

    def draw_grid(self) -> None:
        """
        Рисует сетку сферы.
        """
        sphere_grid = self.sphere_grid
        glColor3f(0.2, 0.5, 0.8)

        for longitude in range(len(sphere_grid[0])):
            glBegin(GL_LINE_STRIP)
            for latitude in sphere_grid:
                vector = latitude[
                    longitude]
                glVertex3f(*vector)
            glEnd()

        for latitude in sphere_grid:
            glBegin(GL_LINE_LOOP)
            for longitude in range(len(latitude)):
                vector = latitude[
                    longitude]
                glVertex3f(*vector)
            glEnd()

    def _draw_ground(self):
        """
        Рисует землю.
        """
        glColor3f(0.11, 0.65, 0.14)
        glBegin(GL_TRIANGLE_FAN)
        for point in self._ground_vertices:
            glVertex3f(*point)
        glEnd()

    @staticmethod
    def _generate_ground_vertices(r: float, sides_count: int) -> list[
        tuple[float, float, float]]:
        """
        Генерирует вершины земли.

        :param r: Радиус земли.
        :param sides_count: Количество сторон.
        :return: Список вершин.
        """
        vertices = [(0, -0.5, 0)]
        angle = 2 * math.pi / sides_count
        for i in range(sides_count + 1):
            vertices.append(
                (r * math.cos(i * angle), 0, r * math.sin(i * angle))
            )
        return vertices

    @staticmethod
    def _draw_stars(stars_by_groups: dict[int, list[Star]]) -> None:
        """
        Рисует звезды, разделённые по группам.

        :param stars_by_groups: Словарь групп звёзд.
        """
        glColor3f(1.0, 1.0, 1.0)

        min_size = 1.0
        max_size = 5.5
        num_groups = 10
        # Эти числа и формула подобраны методом тыка для адекватного отображения звезд по их яркости
        for size, stars in stars_by_groups.items():
            inverted_size = num_groups - size + 1

            scaled_size = min_size + (max_size - min_size) * (
                    inverted_size / num_groups
            ) ** 8.5

            glPointSize(scaled_size)
            glBegin(GL_POINTS)
            for current_star in stars:
               vector = current_star.get_vector()
               glVertex3f(*vector)
            glEnd()

    @staticmethod
    def _separate_stars_by_groups(stars: list[Star], sizes_range: list[int]) -> \
            dict[int, list[Star]]:
        """
        Разделяет звёзды на группы по размеру.

        :param stars: Список звезд.
        :param sizes_range: Диапазон размеров групп.
        :return: Словарь групп звёзд.
        """
        stars_by_size = {size: [] for size in sizes_range}
        stars_sorted = sorted(stars,
                              key=lambda star_obj: star_obj.get_magnitude())
        group_len = max(1, int(len(stars_sorted) / len(sizes_range)))
        for i, current_star in enumerate(stars_sorted):
            index = i // group_len
            if index >= len(sizes_range):
                index = len(sizes_range) - 1
            stars_by_size[sizes_range[index]].append(current_star)
        return stars_by_size

    def update_date(self, new_date: datetime):
        """
        Обновляет дату и позиции звёзд.

        :param new_date: Новая дата.
        """
        self._date = new_date
        base_date = datetime(2000, 1, 1, 12, 0)
        delta_time = new_date - base_date

        self._updated_stars = StarPositionUpdater.update_positions(self._stars,
                                                                   delta_time)
        self._stars_by_groups = self._separate_stars_by_groups(
            self._updated_stars, list(range(1, 11))
        )
        self.update()

    def get_current_date_text(self) -> str:
        """
        Возвращает текущую дату в строковом формате.

        :return: Строка с датой.
        """
        return self._date.strftime(DATE_FORMAT)

    def set_latitude(self, value: int) -> None:
        """
        Устанавливает широту вида.

        :param value: Новое значение широты.
        """
        value = max(self.latitude.min_value,
                    min(self.latitude.max_value, value))
        self.latitude.value = value
        self.update()

    def set_longitude(self, value: int) -> None:
        """
        Устанавливает долготу вида.

        :param value: Новое значение долготы.
        """
        range_min, range_max = self.longitude.min_value, self.longitude.max_value
        value = (value - range_min) % (range_max - range_min) + range_min
        self.longitude.value = value
        self.update()

    def set_head_latitude(self, value: float) -> None:
        """
        Устанавливает наклон головы вверх/вниз.

        :param value: Новое значение наклона.
        """
        if self.head_latitude.min_value < value < self.head_latitude.max_value:
            self.head_latitude.value = value
            self.headLatitudeChanged.emit(self.head_latitude.value)
            self.update()

    def set_head_longitude(self, value: float) -> None:
        """
        Устанавливает наклон головы влево/вправо.

        :param value: Новое значение наклона.
        """
        range_min, range_max = self.head_longitude.min_value, self.head_longitude.max_value
        value = (value - range_min) % (range_max - range_min) + range_min
        self.head_longitude.value = value
        self.headLongitudeChanged.emit(self.head_longitude.value)
        self.update()

    def update_zoom(self, value: int) -> None:
        """
        Обновляет поле зрения (zoom).

        :param value: Новое значение зума.
        """
        self.fov.value = max(self.fov.min_value,
                             min(self.fov.max_value, value))
        self.update_projection()
        self.update()

    def update_projection(self) -> None:
        """
        Обновляет проекцию OpenGL.
        """
        aspect = 1.8
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov.value, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    # Методы нельзя переименовывать, они переопределяют базовые методы QGLWidget
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

        new_head_longitude = self.head_longitude.value + longitude_delta
        new_head_latitude = self.head_latitude.value + latitude_delta

        self.set_head_longitude(new_head_longitude)
        self.set_head_latitude(new_head_latitude)

        self._last_mouse_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = None
