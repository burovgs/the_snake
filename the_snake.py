import sys
from random import randint

import pygame as pg

# Константы игрового поля
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Базовая палитра цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Цвета игровых элементов
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = WHITE
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

# Скорость игры
SPEED = 10

# Настройка экрана и часов
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()

# Словарь поворотов: код клавиши -> (новое направление, запрещенное)
TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None, position=SCREEN_CENTER):
        self.body_color = body_color
        self.position = position

    def draw_cell(
        self, surface, position, body_color=None, border_color=BORDER_COLOR
    ):
        """Отрисовывает одну ячейку на игровом поле."""
        cell_color = body_color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, cell_color, rect)
        if border_color:
            pg.draw.rect(surface, border_color, rect, 1)

    def draw(self, surface):
        """Отрисовывает объект на экране."""
        raise NotImplementedError(
            f'Метод draw() должен быть переопределен в классе '
            f'{self.__class__.__name__}'
        )


class Apple(GameObject):
    """Класс, описывающий яблоко и его поведение."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайное положение яблока на свободную клетку."""
        occupied_positions = occupied_positions or []
        self.position = None
        while self.position is None or self.position in occupied_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

    def draw(self, surface):
        """Отрисовывает яблоко."""
        self.draw_cell(surface, self.position)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color=body_color)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в исходное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction=None):
        """Обновляет направление движения змейки."""
        if new_direction:
            self.direction = new_direction

    def move(self):
        """Обновляет позицию змейки с учетом границ экрана."""
        cur_head = self.get_head_position()
        delta_x, delta_y = self.direction
        new_head = (
            (cur_head[0] + delta_x * GRID_SIZE) % SCREEN_WIDTH,
            (cur_head[1] + delta_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        if new_head in self.positions[2:]:
            self.reset()
            return True

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        return False

    def draw(self, surface):
        """Отрисовывает голову змейки и затирает хвост."""
        self.draw_cell(surface, self.get_head_position())

        if self.last:
            self.draw_cell(
                surface,
                self.last,
                body_color=BOARD_BACKGROUND_COLOR,
                border_color=None,
            )


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и события выхода."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN and event.key in TURNS:
            new_direction, opposite = TURNS[event.key]
            if game_object.direction != opposite:
                game_object.update_direction(new_direction)


def main():
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        is_reset = snake.move()

        if is_reset:
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(occupied_positions=snake.positions)

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)

        apple.draw(screen)
        snake.draw(screen)
        pg.display.update()


if __name__ == '__main__':
    main()
