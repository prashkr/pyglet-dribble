import pyglet
from pyglet.window import mouse


G = -3000
SCORE = 0
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BALL_CENTER_X = 400
BALL_CENTER_Y = 300
BALL_SCALE = 0.25
IMPULSIVE_FORCE = 60000
IMPULSE_DURATION = 0.02  # 20 ms
WINDOW_REFRESH_RATE = 1 / 120


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


class Score:
    def __init__(self, *args, **kwargs):
        self.current_score = 0
        self.high_score = 0
        self.current_score_label = pyglet.text.Label(text="Score: 0", x=600, y=550)
        self.high_score_label = pyglet.text.Label(text="Score: 0", x=600, y=530)

    def reset(self):
        self.current_score = 0

    def add(self, points=1):
        self.current_score += points
        if self.current_score > self.high_score:
            self.high_score = self.current_score

    def update(self, dt):
        self.current_score_label.text = f'Current Score: {self.current_score}'
        self.high_score_label.text = f'High Score: {self.high_score}'

    def draw(self):
        self.current_score_label.draw()
        self.high_score_label.draw()

    def __str__(self):
        return f'Current score: {self.current_score}, High score: {self.high_score}'


class Ball(pyglet.sprite.Sprite):
    def __init__(self, file_name, score, x=BALL_CENTER_X, y=BALL_CENTER_Y, scale=BALL_SCALE):
        self.img = pyglet.resource.image(file_name)
        center_image(self.img)
        super(Ball, self).__init__(img=self.img, x=x, y=y)
        self.x = x
        self.y = y
        self.scale = scale
        self.velocity_x, self.velocity_y = 0.0, 0.0
        self.mass = 1  # 1 kg
        self.damping_factor = 0.8
        self.score = 0
        self.velocity_after_force = 800
        self.radius = self.compute_radius()
        self.score = score

    def compute_radius(self):
        lower_left, top_left, top_right, lower_right = self.get_bounding_box()
        radius = abs(top_left[1] - self.y)
        return radius

    def update(self, dt):
        """
        Distance update equation:
            s = ut + 1/2 * a * t2

        Velocity update equation:
            v = u + at

        """
        # print("radius: ", self.radius)
        # print("velocities: ", (self.velocity_x, self.velocity_y))
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt + 1 / 2 * G * dt ** 2
        self.velocity_y = self.velocity_y + G * dt
        self.check_wall_collision_and_update_state()

    def get_bounding_box(self):
        lower_left = (self.x - self.width // 2, self.y - self.height // 2)
        top_left = (self.x - self.width // 2, self.y + self.height // 2)
        top_right = (self.x + self.width // 2, self.y + self.height // 2)
        lower_right = (self.x + self.width // 2, self.y - self.height // 2)
        return lower_left, top_left, top_right, lower_right

    def is_coord_inside_ball(self, coordinate):
        return (coordinate[0] - self.x) ** 2 + (coordinate[1] - self.y) ** 2 <= self.radius ** 2

    def check_wall_collision_and_update_state(self):
        window_x_bounds = (0, WINDOW_WIDTH)
        window_y_bounds = (0, WINDOW_HEIGHT)
        lower_left, top_left, top_right, lower_right = self.get_bounding_box()

        collision_with_ground = lower_left[1] <= window_y_bounds[0]
        collision_with_left_wall = lower_left[0] <= window_x_bounds[0]
        collision_with_right_wall = lower_right[0] >= window_x_bounds[1]

        if collision_with_ground:
            print("collision with ground")
            self.velocity_y = -self.velocity_y * self.damping_factor
            self.y = window_y_bounds[0] + self.height // 2
            self.score.reset()

        elif collision_with_left_wall:
            print("collision with left wall")
            self.velocity_x = -self.velocity_x * self.damping_factor
            self.x = window_x_bounds[0] + self.width // 2

        elif collision_with_right_wall:
            print("collision with right wall")
            self.velocity_x = -self.velocity_x * self.damping_factor
            self.x = window_x_bounds[1] - self.width // 2

    def x_distance_from_center(self, coordinate):
        return self.x - coordinate[0]

    def apply_force(self, x, y, F_x=0, F_y=IMPULSIVE_FORCE):
        """
        impulse = change in momentum i.e. F * dt = m * (vf - vi)

        self.velocity_x = F_x * dt / self.mass + self.velocity_x
        self.velocity_y = (F_y + self.mass * G) * dt / self.mass + self.velocity_y
        """
        if self.is_coord_inside_ball(coordinate=(x, y)):
            print("coordinate_inside_ball")
            x_distance = self.x_distance_from_center(coordinate=(x, y))
            self.velocity_x = self.velocity_after_force * (x_distance / self.radius)
            self.velocity_y = self.velocity_after_force
            print("velocities: ", (self.velocity_x, self.velocity_y))
            self.score.add(points=1)


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.score = Score()
        self.ball = Ball(file_name='res/ball.png', score=self.score)

    def on_draw(self):
        window.clear()
        self.ball.draw()
        self.score.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        print("mouse button: ", button, " was pressed at: ", (x, y), ', Score: ', self.score)
        if button == mouse.LEFT:
            self.ball.apply_force(x, y)

    def update(self, dt):
        self.ball.update(dt)
        self.score.update(dt)


if __name__ == '__main__':
    window = Window()
    pyglet.clock.schedule_interval(window.update, WINDOW_REFRESH_RATE)
    pyglet.app.run()
