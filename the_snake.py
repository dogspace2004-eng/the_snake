from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

SCREEN_CENTER = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE,
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
TURNS = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует позицию и цвет объекта."""
        self.position = position if position is not None else SCREEN_CENTER
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Рисует одну клетку c рамкой по указанным координатам."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект; переопределяется в дочерних классах."""
        raise NotImplementedError(
            'Метод draw не реализован в классе '
            f'{type(self).__name__}'
        )


class Apple(GameObject):
    """Яблоко, которое съедает змейка."""

    def __init__(
        self,
        position=SCREEN_CENTER,
        body_color=APPLE_COLOR,
        occupied_cells=(),
    ):
        """Задаёт цвет яблока и начальную позицию."""
        super().__init__(position, APPLE_COLOR)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=()):
        """Устанавливает случайную позицию на поле."""
        free_cells = ALL_CELLS - set(occupied_cells)
        self.position = choice(tuple(free_cells))

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, управляемая игроком."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует начальное состояние змейки."""
        super().__init__(position, SNAKE_COLOR)
        self.reset()
        self.direction = RIGHT

    def reset(self):
        """Сбрасывает змейку в начальное положение."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction=None):
        """Обновляет направление движения змейки."""
        if new_direction:
            self.direction = new_direction

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        # Остаток от деления переносит змейку через границы.
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает новую голову и затирает бывший хвост."""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            new_direction = TURNS.get((game_object.direction, event.key))
            if new_direction:
                game_object.update_direction(new_direction)


def main():
    """Основная логика игры."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_cells=snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        head = snake.get_head_position()

        if head == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif head in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
