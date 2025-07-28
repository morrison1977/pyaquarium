#!/usr/bin/python3
import curses
import time
import random

FISH_ART = [
    [">((º>", "<º))><"],
    ['><>', '<><'],
]

SHARK_ART = [
    [
        r"              |\\",
        r"    \\`.__---~~  ~~~--_",
        r"    //~~----___  (_o_-~",
        r"   '           |/'"
    ],
    [
        r"            //|",
        r"        _--~~~  ~~---__.'`//",
        r"       ~-_o_)  ___----~~\\",
        r"            '\|           '"
    ]
]

OTHER_CREATURES = [
    [r"V=(° °)=V"],
    [
        r"      _____",
        r"   ,-~     ~-,",
        r"  (           )",
        r"   \_-,',',-_/",
        r"    / /| |\ \ ",
        r"   | | | | | |",
        r"  / / /   \ \ \ "
    ]
]


CASTLE_ART = [
    r"""
++++=++++|
         |
        /^\
       / | \
_  _  /  |  \  _   _   _
[ ]_[ ]_ _   _ [ ]_[ ]_[ ]
|_=__- =_[ ]_[ ]_=-___-__|
 | _- =  =_ = _  = _=   |
 |= -[] - _ = _ =_-=_[] |
 | =_  = -  ___ =_ =  = |
 |=  []- - /| |\ =_ =[] |
 |- =_ = =| | | | - = - |
 |________|_|_|_|_______|
"""
]

WATER_LINE = [
    "~~~-__~`~__-~~~~-~~~~-~~~~-~~~~-__~`~__-~~~~~-~~~~-~~",
    "^^^^ ^^^  ^^^   ^^^    ^^^^      ",
    "^^^     ^^^^     ^^^    ^^      ",
    "^^     ^^^^     ^^^    ^^^^^^  "
]

class Entity:
    """Base class for any object in the aquarium."""
    def __init__(self, x, y, art, direction=1, color=None):
        self.x = int(x)
        self.y = int(y)
        self.art = art
        self.direction = direction
        self.color = color if color is not None else curses.color_pair(1)
        self.width = max(len(line) for line in self.art) if self.art else 0
        self.height = len(self.art)
        self.dead = False

    def draw(self, screen):
        """Draws the entity on the screen."""
        for i, line in enumerate(self.art):
            try:
                screen.addstr(self.y + i, self.x, line, self.color)
            except curses.error:
                pass

    def move(self, max_width, max_height):
        """Moves the entity and marks it as dead if it goes off-screen."""
        self.x += self.direction
        if self.x < -self.width or self.x > max_width:
            self.dead = True

    def collides_with(self, other):
        """Checks for collision with another entity."""
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )

class Fish(Entity):
    """A fish entity that can be of a random color."""
    def __init__(self, x, y, art, direction, color):
        super().__init__(x, y, art, direction, color=color)
        self.kind = 'fish'

class Bubble(Entity):
    """A bubble entity that moves upwards."""
    def __init__(self, x, y, color):
        art = [random.choice([".", "o", "O"])]
        super().__init__(x, y, art, direction=0, color=color)
        self.kind = 'bubble'

    def move(self, max_width, max_height):
        """Overrides move to go upwards and die at the water line."""
        self.y -= 1
        if self.y < 1:
            self.dead = True

class Shark(Entity):
    """A shark entity that eats fish."""
    def __init__(self, max_width, max_height):
        direction = random.choice([-1, 1])
        art_index = 0 if direction == 1 else 1
        art = SHARK_ART[art_index]
        y = random.randint(8, max_height - len(art) - 2)

        super().__init__(0, y, art, direction, color=curses.color_pair(4))

        self.x = 0 - self.width if direction == 1 else max_width
        self.kind = 'shark'

class OtherCreature(Entity):
    """A rare other creature entity."""
    def __init__(self, max_width, max_height):
        direction = random.choice([-1, 1])
        art = OTHER_CREATURES[0]
        y = random.randint(5, max_height - len(art) - 5)

        super().__init__(0, y, art, direction, color=curses.color_pair(7))

        self.x = 0 - self.width if direction == 1 else max_width
        self.kind = 'other_creature'


class Aquarium:
    """Manages the state and rendering of the aquarium."""
    def __init__(self, screen):
        self.screen = screen
        self.max_y, self.max_x = self.screen.getmaxyx()
        self.entities = []
        self.running = True
        self.fish_colors = []
        self.castle_colors = []
        self.castle_color_index = 0
        self.last_castle_color_change = time.time()
        self.water_colors = []
        self.water_color_index = 0
        self.last_water_color_change = time.time()
        self.water_offset = 0
        self.last_water_shift = time.time()


    def add_water_lines(self):
        """Draws the wavy, moving, color-shifting water lines at the top."""
        current_water_color = self.water_colors[self.water_color_index]
        for i, line in enumerate(WATER_LINE):
            offset = self.water_offset % len(line)
            rotated_line = line[offset:] + line[:offset]

            repeat = (self.max_x // len(rotated_line)) + 1
            tiled = (rotated_line * repeat)[:self.max_x]

            self.screen.addstr(i + 1, 0, tiled, current_water_color)

    def add_castle(self):
        """Draws the sand castle at the bottom right."""
        castle_lines = CASTLE_ART[0].strip().splitlines()
        castle_height = len(castle_lines)
        castle_width = max(len(line) for line in castle_lines)

        y_start = self.max_y - castle_height -1
        x_start = self.max_x - castle_width - 2

        current_castle_color = self.castle_colors[self.castle_color_index]

        for i, line in enumerate(castle_lines):
            try:
                self.screen.addstr(y_start + i, x_start, line, current_castle_color)
            except curses.error:
                pass

    def spawn_fish(self):
        """Creates a new fish entity with a random color."""
        art_pair = random.choice(FISH_ART)
        direction = random.choice([-1, 1])
        shape = art_pair[0] if direction == 1 else art_pair[1]
        lines = [shape]

        x = 0 - len(lines[0]) if direction == 1 else self.max_x
        y = random.randint(5, self.max_y - 5)

        random_color = random.choice(self.fish_colors)

        self.entities.append(Fish(x, y, lines, direction, random_color))

    def maybe_spawn_shark(self):
        """Has a small chance of spawning a shark."""
        if random.random() < 0.05:
            self.entities.append(Shark(self.max_x, self.max_y))

    def maybe_spawn_other_creature(self):
        """Has a very small chance of spawning a other creature."""
        if random.random() < 0.09:
            self.entities.append(OtherCreature(self.max_x, self.max_y))

    def update(self):
        """Updates the state of all entities in the aquarium."""
        new_entities = []
        sharks = [e for e in self.entities if e.kind == 'shark']

        for entity in self.entities:
            entity.move(self.max_x, self.max_y)

        for entity in self.entities:
            if entity.kind == 'fish' or entity.kind == 'other_creature':
                if random.random() < 0.02:
                    bubble_x = entity.x + random.randint(0, entity.width - 1)
                    bubble_color = self.water_colors[self.water_color_index]
                    new_entities.append(Bubble(bubble_x, entity.y, bubble_color))

            if entity.kind == 'fish':
                for shark in sharks:
                    if not entity.dead and shark.collides_with(entity):
                        entity.dead = True
                        break

        self.entities.extend(new_entities)
        self.entities = [e for e in self.entities if not e.dead]


    def draw(self):
        """Clears the screen and draws all elements."""
        self.screen.clear()
        self.add_water_lines()
        self.add_castle()
        for entity in self.entities:
            entity.draw(self.screen)
        self.screen.refresh()

    def run(self):
        """Main loop for the application."""
        curses.curs_set(0)
        self.screen.nodelay(True)

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        curses.init_pair(8, curses.COLOR_YELLOW, -1)
        curses.init_pair(9, curses.COLOR_RED, -1)
        curses.init_pair(10, curses.COLOR_MAGENTA, -1)

        self.fish_colors = [
            curses.color_pair(1),
            curses.color_pair(5),
            curses.color_pair(6),
        ]
        self.castle_colors = [
            curses.color_pair(3),
            curses.color_pair(8),
            curses.color_pair(9),
            curses.color_pair(10),
        ]
        self.water_colors = [
            curses.color_pair(1),
            curses.color_pair(2),
        ]

        last_fish_spawn = time.time()
        last_rare_spawn_check = time.time()

        while self.running:
            try:
                key = self.screen.getch()
                if key != -1:
                    self.running = False
                    continue

                now = time.time()

                if now - last_fish_spawn > 1.5:
                    self.spawn_fish()
                    last_fish_spawn = now

                if now - last_rare_spawn_check > 7:
                    self.maybe_spawn_shark()
                    self.maybe_spawn_other_creature()
                    last_rare_spawn_check = now

                if now - self.last_castle_color_change > 0.5:
                    self.castle_color_index = (self.castle_color_index + 1) % len(self.castle_colors)
                    self.last_castle_color_change = now

                if now - self.last_water_color_change > 1.0:
                    self.water_color_index = (self.water_color_index + 1) % len(self.water_colors)
                    self.last_water_color_change = now

                if now - self.last_water_shift > 0.15:
                    self.water_offset += 1
                    self.last_water_shift = now

                self.update()
                self.draw()
                time.sleep(0.1)
            except (curses.error, KeyboardInterrupt):
                self.running = False


def main(stdscr):
    """Wrapper function to run the aquarium."""
    aquarium = Aquarium(stdscr)
    aquarium.run()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except curses.error as e:
        print("There was an error with curses.")
        print("Your terminal window might be too small to run the application.")
        print(f"Error: {e}")
