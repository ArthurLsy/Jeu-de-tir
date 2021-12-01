import pygame
import constants
import random
import math



def process_mouse_event(world):
    x, y = pygame.mouse.get_pos()
    world['bullet'] = (x, y)
    world['bullet_impacts'].append({
        'center': (x, y),
        'ttl': constants.BULLET_TTL
    })
   

def manage_events(world) -> bool:
    trigger = 0
    stop = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            process_mouse_event(world)
        if event.type == pygame.KEYUP:
            constants.ACCELERATION=0
    if(pygame.time.get_ticks() > constants.TIME_TO_PLAY):
        stop = True
    if pygame.key.get_pressed()[pygame.K_t]:
        #info_cible()
        print(pygame.key.get_pressed()[pygame.K_SPACE])
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        trigger = 1
        move(targets,'r')
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        trigger = 1
        move(targets,'l')
    if pygame.key.get_pressed()[pygame.K_UP]:
        trigger = 1
        move(targets,'u')
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        trigger = 1
        move(targets,'d')
    if constants.ENERGY < 100 and trigger == 0:
        constants.ENERGY += constants.ENERGY_RATIO
        print(constants.ENERGY)

    return stop

    

def info_cible():
    return(targets)

def move(targets,sens):
    if constants.ENERGY > 0 :
        constants.ENERGY -= constants.ENERGY_RATIO
        print(constants.ENERGY)
        if constants.ACCELERATION < constants.TARGET_SPEED :
            constants.ACCELERATION += constants.ACCELERATION_RATIO
        if sens == 'r':
            for i in range(len(targets)):
                targets[i]['rectangle'][0]=targets[i]['rectangle'][0]+constants.ACCELERATION
        if sens == 'l':
            for i in range(len(targets)):
                targets[i]['rectangle'][0]=targets[i]['rectangle'][0]-constants.ACCELERATION                                                                
        if sens == 'u':   
            for i in range(len(targets)):
                targets[i]['rectangle'][1]=targets[i]['rectangle'][1]-constants.ACCELERATION
        if sens == 'd':
            for i in range(len(targets)):
                targets[i]['rectangle'][1]=targets[i]['rectangle'][1]+constants.ACCELERATION


def decay_items(items):
    i = len(items) - 1

    while i >= 0:
        item = items[i]
        item['ttl'] = item['ttl'] - world['delta_time']
        if item['ttl'] <= 0:
            items.pop(i)
        i = i - 1


        
def update_explosions(world):
    for explosion in world['explosions']:
        l = float(explosion['ttl']) / constants.BULLET_TTL
        l = 4 * (l * (1 - l))

        points = []
        x, y = explosion['center']
        for point in explosion['points_reference']:
            X, Y = point
            X = x + (X - x) * l
            Y = y + (Y - y) * l
            points.append((X, Y))
        
        explosion['points_current'] = points

        

def calculate_next_target_delay(world):
    world['next_target_ttl'] = constants.TARGET_DELAY


    
def add_target(targets):
    x = random.randint(0, constants.WIDTH - constants.TARGET_SIZE)
    y = random.randint(0, constants.HEIGHT - constants.TARGET_SIZE)
    targets.append(
        {
            'rectangle': [
                x, y, constants.TARGET_SIZE, constants.TARGET_SIZE
            ],
            'ttl': constants.TARGET_TTL
        }
    )


    
def populate_targets(world, targets):
    world['next_target_ttl'] = world['next_target_ttl'] - world['delta_time']
    if world['next_target_ttl'] <= 0:
        calculate_next_target_delay(world)
        add_target(targets)


        
def update(world, targets):
    decay_items(world['bullet_impacts'])
    decay_items(targets)
    decay_items(world['explosions'])
    update_explosions(world)
    populate_targets(world, targets)


    
def collides_with(bullet, target):
    x, y = bullet
    x_min, y_min, width, height = target
    x_max = x_min + width
    y_max = y_min + height

    return x_min <= x <= x_max and y_min <= y <= y_max



def add_explosion(world, target):
    x, y, _, _ = target
    inner_radius = 50
    outer_radius = 120
    step = math.pi / 10
    points = []
    angle = 0
    for i in range(10):
        points.append((x + math.cos(angle) * inner_radius, y + math.sin(angle) * -inner_radius))
        angle = angle + step
        points.append((x + math.cos(angle) * outer_radius, y + math.sin(angle) * -outer_radius))
        angle = angle + step

    explosion = {
        'center': (x, y) ,
        'points_reference': points,
        'ttl': constants.BULLET_TTL,
        'points_current': []
    }

    world['explosions'].append(explosion)


    
def process_collisions(world, targets):
    if world['bullet'] is None:
        return
    
    bullet = world['bullet']

    i = len(targets) - 1

    while i >= 0:
        target = targets[i]
        
        if collides_with(bullet, target['rectangle']):
            add_explosion(world, target['rectangle'])
            world['score'] = world['score'] + 1
            targets.pop(i)
        i = i - 1


        
def update_display(scene, world, targets):
    scene.fill((0, 0, 0))
    impacts = world['bullet_impacts']
    explosions = world['explosions']

    for target in targets:
        shade = int((float(target['ttl']) / constants.TARGET_TTL) * 255)
        pygame.draw.rect(scene, (0, shade, 0), target['rectangle'])
    
    for impact in impacts:
        shade = int((float(impact['ttl']) / constants.BULLET_TTL) * 255)
        pygame.draw.circle(scene, (shade, 0, 0), impact['center'], 5)

    for explosion in explosions:
        if len(explosion['points_current']) == 0:
            continue
        shade = float(explosion['ttl']) / constants.BULLET_TTL
        pygame.draw.polygon(scene, (200, 200 * shade, 0), explosion['points_current'])

    score = world['score']
    textsurface = world['font'].render(f"Score: {score}", False, (255, 255, 255))
    pygame.draw.rect(
        scene,
        (64, 64, 64),
        (0, constants.HEIGHT, constants.WIDTH, constants.HEIGHT + constants.TEXT_ZONE_HEIGHT)
    )
    scene.blit(
        textsurface,
        (
            constants.TEXT_MARGIN_LEFT,
            constants.HEIGHT + (constants.TEXT_ZONE_HEIGHT - constants.FONT_HEIGHT) / 2
        )
    )
    pygame.draw.rect(
        scene,
        (255,255,0),
        (0,constants.HEIGHT-10,constants.ENERGY*(constants.WIDTH/100),10)
    )
    pygame.display.flip()


    
def loop(scene, world, targets, clock):
    stop = manage_events(world)
    update(world, targets)
    process_collisions(world, targets)
    update_display(scene, world, targets)
    world['bullet'] = None
    world['delta_time'] = clock.tick(constants.FPS)

    return not stop



if __name__ == '__main__':

    pygame.init()

    clock = pygame.time.Clock()

    scene = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT + constants.TEXT_ZONE_HEIGHT))
    pygame.display.set_caption('Shooter')
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), constants.FONT_HEIGHT)

    pygame.key.set_repeat(10, 3)
    
    world = {
        'delta_time': 15,
        'bullet': None,
        'bullet_impacts': [],
        'next_target_ttl': 0,
        'score': 0,
        'font': font,
        'explosions': []
    }

    targets = []

    running = True

    while running:
        running = loop(scene, world, targets, clock)
        pygame.display.update()

    print('---------------------------------------')
    print('Fin du jeu. Vous avez détruit {} cibles.'.format(world['score']))
