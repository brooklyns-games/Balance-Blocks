from global_vars import *
from objects import *

from pymunk import Vec2d

level_types = ['sort', 'total', 'balance', 'find']

class Level:
    def __init__(self, number: int, weights: list, level_type='sort'):
        """Manages level information and controls when to add level objects"""
        self.number = number
        self.weights = weights
        self.level_type = level_type

        self.loading_platforms = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.seesaw = None  # should be sprite groupsingle()

        self.guesses = 0
        self.wrongs = 0
        self.wrong_limit = 3


        self.sprite_objects = pygame.sprite.LayeredUpdates()
        # self.sprite_objects.add(self.level_display)
        self.bodies = []


    def run(self):
        # Add only the current level's objects to SPACE
        pass
        # for sprite in BODIES:
        #     SPACE.add(sprite.body, sprite.shape)
        # for sprite in joints:
        #     SPACE.add(sprite.joint)
    def end(self):
        for sprite in self.sprite_objects:
            sprite.destroy()



    def setup(self):
        total_blocks = len(self.weights)
        l = W / 2 / total_blocks
        # BLOCKS.empty()
        coords = [(100 + int(10 + i * (W / 2 - 20) / total_blocks), 50) for i in range(total_blocks)] # somehow randomize?
        random.shuffle(coords)

        unique_weights = list(set(self.weights))
        weight_to_collision = {w: 10 + i for i, w in enumerate(unique_weights)}

        for i in range(total_blocks):
            weight = self.weights[i]
            block_handler = weight_to_collision[weight]
            platform_handler = max(weight_to_collision.values()) + i   # each handler has different collision type
            # print(coords[i])
            b = Block(*coords[i], weight,
                      category=4, mask=22, collision_type=block_handler)
            # print('block', b.body)


            # plat = LoadingPlatform((W / 2 + i * l, H - i * l), (l, 0),
            #                        category=16, mask=7,
            #                        collision_type=platform_handler,)
            load = LoadingBox((W / 2 + i * l, H - i * l - 50), b.game_sprite.rect.inflate(10, 10).size, weight, platform_handler)
            self.loading_platforms.add(load)
            self.blocks.add(b)

            for j in range(len(Deck.decks)):
                handler = SPACE.add_collision_handler(j, block_handler)
                handler.post_solve = b.touching_deck


        self.sprite_objects.add(*self.loading_platforms, layer=2)
        self.sprite_objects.add(*self.blocks, layer=1)

    def draw(self, screen):
        self.loading_platforms.draw(screen)
        self.blocks.draw(screen)


class WeighingBalance:
    def __init__(self, center: tuple, beam_length: "Vec2d|tuple", carrier_length: "Vec2d|tuple"):
        p = Vec2d(*center)
        v = Vec2d(*beam_length)
        v2 = Vec2d(*carrier_length)

        self.beam = Segment(p, v, category=1, mask=16, center=True)
        # self.beam.shape.damping = 0.9
        mid_local = Vec2d(*(0.5 * v))
        mid_world = p + mid_local  # Attach only at the middle
        PivotJoint(b0, self.beam.body, mid_world, (0, 0), collide=False)

        self.carrier1 = Deck(p - 0.5 * v2 + (0, 100), v2)
        self.carrier2 = Deck(p + v - v2 * 0.5 + (0, 100), v2)
        SlideJoint(self.carrier1.body, self.beam.body, (0,0), -self.beam.v / 2, 0, 100, False)
        SlideJoint(self.carrier1.body, self.beam.body, self.carrier1.v, -self.beam.v / 2, 0, 100, False)

        SlideJoint(self.carrier2.body, self.beam.body, (0, 0), self.beam.v / 2, 0, 100, False)
        SlideJoint(self.carrier2.body, self.beam.body, self.carrier2.v, self.beam.v / 2, 0, 100, False)

        # PinJoint(self.carrier1.body, self.beam.body, (self.carrier1.v / 2), -self.beam.v / 2)
        # PinJoint(self.carrier2.body, self.beam.body, (self.carrier1.v / 2), self.beam.v / 2)



class Seesaw:
    def __init__(self, center: tuple, beam_length: "Vec2d|tuple", carrier_length: "Vec2d|tuple"):

        p = Vec2d(*center)
        v = Vec2d(*beam_length)
        v2 = Vec2d(*carrier_length)

        self.beam = Segment(p, v, category=1, mask=16, center=True)
        # self.beam.shape.damping = 0.9
        mid_local = Vec2d(*(0.5 * v))
        mid_world = p + mid_local # Attach only at the middle
        PivotJoint(b0, self.beam.body, mid_world, (0, 0), collide=False)
        #
        # carriers
        self.carrier1 = Deck(p - 0.5 * v2, v2)
        PivotJoint(self.carrier1.body, self.beam.body, v2 * 0.5, v * -0.5)

        self.carrier2 = Deck(p + v - v2 * 0.5, v2)
        PivotJoint(self.carrier2.body, self.beam.body, v2 * 0.5, v * 0.5)

        self.fulcrum = Triangle(*mid_world, 50, category=8, mask=1, body_type=pymunk.Body.STATIC)

