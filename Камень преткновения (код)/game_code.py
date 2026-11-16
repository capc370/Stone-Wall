import pygame
import os
import sys
import math
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Monolith Defense")
clock = pygame.time.Clock()

#Глобальное время
game_time = 0
last_frame_time = 0

#Игровое время
def update_game_time():
    global game_time, last_frame_time
    current = pygame.time.get_ticks()
    if not paused:
        game_time += current - last_frame_time
    last_frame_time = current

#Монитор
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

#Счет
trees_count = 0
rocks_count = 0
coppers_count = 0
irons_count = 0
titaniums_count = 0
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

#Цвета партиклов
RESOURCE_COLORS = {
    'trees':     (190, 100, 30),
    'rocks':     (140, 140, 140),
    'coppers':   (255, 115, 51),
    'irons':     (220, 220, 220),
    'titaniums': (120, 160, 120)
}
particles = []

#Класс партиклов
class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = random.uniform(-3.5, 3.5)
        self.vy = random.uniform(-6.0, -2.0)
        self.life = random.randint(20, 35)
        self.max_life = self.life
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.vx *= 0.98
        self.life -= 1
        self.size = max(1, self.size - 0.08)

    def draw(self, surface, camera_x, camera_y):
        if self.life <= 0:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        if sx < -10 or sy < -10 or sx > SCREEN_WIDTH + 10 or sy > SCREEN_HEIGHT + 10:
            return
        pygame.draw.circle(surface, self.color, (sx, sy), int(self.size))

#Спавн партиклов
def spawn_resource_particles(resource, resource_type):
    color = RESOURCE_COLORS[resource_type]
    cx = resource.rect.centerx
    cy = resource.rect.centery
    count = random.randint(8, 12)
    for _ in range(count):
        particles.append(Particle(cx, cy, color))

#Иконки интерфейса
def load_icon(path, size):

    img = pygame.image.load(path)
    return pygame.transform.scale(img, (size, size))

ICON_SIZE = 60
ICON_WOOD     = load_icon('icons/wood.png',     ICON_SIZE)
ICON_ROCK     = load_icon('icons/rock.png',     ICON_SIZE)
ICON_COPPER   = load_icon('icons/copper.png',   ICON_SIZE)
ICON_IRON     = load_icon('icons/iron.png',     ICON_SIZE)
ICON_TITANIUM = load_icon('icons/titanium.png', ICON_SIZE)
TOOL_ICONS = {
    'none':            load_icon('icons/none.png',             ICON_SIZE),
    'молот':           load_icon('icons/hammer.png',           ICON_SIZE),
    'каменная кирка':  load_icon('icons/rock pickaxe.png',     ICON_SIZE),
    'медная кирка':    load_icon('icons/copper pickaxe.png',   ICON_SIZE),
    'железная кирка':  load_icon('icons/iron pickaxe.png',     ICON_SIZE),
    'титановая кирка': load_icon('icons/titanium pickaxe.png', ICON_SIZE)
}
WEAPON_ICONS = {
    'none':          load_icon('icons/none.png',           ICON_SIZE),
    'дубина':        load_icon('icons/club.png',           ICON_SIZE),
    'каменный меч':  load_icon('icons/rock sword.png',     ICON_SIZE),
    'медный меч':    load_icon('icons/copper sword.png',   ICON_SIZE),
    'железный меч':  load_icon('icons/iron sword.png',     ICON_SIZE),
    'титановый меч': load_icon('icons/titanium sword.png', ICON_SIZE)
}

#Текущее
current_tool = 'none'
current_weapon = 'none'

def draw_resource_counter(screen):

    slot_w, slot_h = 80, 100
    gap = 10
    x0, y0 = 10, 10

    slots = [
        (ICON_WOOD,     trees_count,     (150, 100, 50)),
        (ICON_ROCK,     rocks_count,     (150, 150, 150)),
        (ICON_COPPER,   coppers_count,   (255, 115, 51)),
        (ICON_IRON,     irons_count,     (220, 220, 220)),
        (ICON_TITANIUM, titaniums_count, (100, 150, 100)),
    ]

    for i, (icon, value, color) in enumerate(slots):
        rect = pygame.Rect(x0 + i * (slot_w + gap), y0, slot_w, slot_h)

        pygame.draw.rect(screen, (0, 0, 0), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        screen.blit(icon, (rect.centerx - ICON_SIZE // 2, rect.top + 5))

        number_surf = font.render(str(value), True, color)
        number_rect = number_surf.get_rect(midbottom=(rect.centerx, rect.bottom - 5))
        screen.blit(number_surf, number_rect)

def draw_tool_slot(screen):
    rect = pygame.Rect(10, 120, 120, 100)

    pygame.draw.rect(screen, (0, 0, 0), rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    icon = TOOL_ICONS.get(current_tool, TOOL_ICONS['none'])
    screen.blit(icon, (rect.centerx - ICON_SIZE // 2, rect.top + 30))

    label = small_font.render('инструмент', True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=(rect.centerx, rect.top + 15)))

def draw_weapon_slot(screen):
    rect = pygame.Rect(140, 120, 120, 100)

    pygame.draw.rect(screen, (0, 0, 0), rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    icon = WEAPON_ICONS.get(current_weapon, WEAPON_ICONS['none'])
    screen.blit(icon, (rect.centerx - ICON_SIZE // 2, rect.top + 30))

    label = small_font.render('оружие', True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=(rect.centerx, rect.top + 15)))

#Верстак
crafting_open = False
unlocked_tools = {'none'}
unlocked_weapons = {'none'}
TOOL_ORDER = ['молот', 'каменная кирка', 'медная кирка', 'железная кирка', 'титановая кирка']
WEAPON_ORDER = ['дубина', 'каменный меч', 'медный меч', 'железный меч', 'титановый меч']

#Рецепты в верстаке
CRAFT_RECIPES = {
    'молот':           {'cost': {'trees': 5},                 'kind': 'tool'},
    'каменная кирка':  {'cost': {'trees': 2, 'rocks': 5},     'kind': 'tool'},
    'медная кирка':    {'cost': {'trees': 2, 'coppers': 5},   'kind': 'tool'},
    'железная кирка':  {'cost': {'trees': 2, 'irons': 5},     'kind': 'tool'},
    'титановая кирка': {'cost': {'trees': 2, 'titaniums': 5}, 'kind': 'tool'},
    'дубина':          {'cost': {'trees': 5},                 'kind': 'weapon'},
    'каменный меч':    {'cost': {'trees': 2, 'rocks': 5},     'kind': 'weapon'},
    'медный меч':      {'cost': {'trees': 2, 'coppers': 5},   'kind': 'weapon'},
    'железный меч':    {'cost': {'trees': 2, 'irons': 5},     'kind': 'weapon'},
    'титановый меч':   {'cost': {'trees': 2, 'titaniums': 5}, 'kind': 'weapon'}
}

#Урон инструментов
HITS_TABLE = {
    'none':            {'trees': 6, 'rocks': 0, 'coppers': 0, 'irons': 0, 'titaniums': 0},
    'молот':           {'trees': 4, 'rocks': 5, 'coppers': 0, 'irons': 0, 'titaniums': 0},
    'каменная кирка':  {'trees': 3, 'rocks': 3, 'coppers': 4, 'irons': 0, 'titaniums': 0},
    'медная кирка':    {'trees': 2, 'rocks': 2, 'coppers': 3, 'irons': 4, 'titaniums': 0},
    'железная кирка':  {'trees': 2, 'rocks': 2, 'coppers': 2, 'irons': 2, 'titaniums': 3},
    'титановая кирка': {'trees': 1, 'rocks': 1, 'coppers': 1, 'irons': 1, 'titaniums': 1}
}

#Урон оружия
WEAPON_DAMAGE = {
    'none':          15,
    'дубина':        20,
    'каменный меч':  25,
    'медный меч':    30,
    'железный меч':  35,
    'титановый меч': 50
}

#Текущий урон игрока
def get_player_damage():
    return WEAPON_DAMAGE.get(current_weapon, WEAPON_DAMAGE['none'])

#Прямоугольники окна крафта
def get_craft_menu_rects():

    menu_w, menu_h = 760, 620
    mx = SCREEN_WIDTH // 2 - menu_w // 2
    my = SCREEN_HEIGHT // 2 - menu_h // 2
    menu_rect = pygame.Rect(mx, my, menu_w, menu_h)

    item_w, item_h = 320, 70
    gap_y = 15
    col_gap = 40

    left_x = mx + 30
    right_x = left_x + item_w + col_gap
    y0 = my + 150

    rects = {}
    for i, name in enumerate(TOOL_ORDER):
        r = pygame.Rect(left_x, y0 + i * (item_h + gap_y), item_w, item_h)
        rects[name] = r
    for i, name in enumerate(WEAPON_ORDER):
        r = pygame.Rect(right_x, y0 + i * (item_h + gap_y), item_w, item_h)
        rects[name] = r

    return menu_rect, rects

#Попытка крафта
def try_craft(name):
    global current_tool, current_weapon

    recipe = CRAFT_RECIPES[name]
    kind = recipe['kind']

    already = (kind == 'tool' and name in unlocked_tools) or \
              (kind == 'weapon' and name in unlocked_weapons)
    if already:
        return

    if get_next_craftable(kind) != name:
        return

    if not has_resources(recipe['cost']):
        return

    spend_resources(recipe['cost'])
    if kind == 'tool':
        unlocked_tools.add(name)
        current_tool = name
    else:
        unlocked_weapons.add(name)
        current_weapon = name


#Отрисовка окна крафта
def draw_crafting_menu():

    menu_rect, rects = get_craft_menu_rects()
    pygame.draw.rect(screen, (0, 0, 0), menu_rect)
    pygame.draw.rect(screen, (255, 255, 255), menu_rect, 2)

    title_font = pygame.font.Font(None, 60)
    title = title_font.render("ВЕРСТАК", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(menu_rect.centerx, menu_rect.top + 40)))

    hint = small_font.render("ESC - закрыть", True, (255, 255, 255))
    screen.blit(hint, hint.get_rect(center=(menu_rect.centerx, menu_rect.top + 70)))

    col_font = pygame.font.Font(None, 42)
    tools_title = col_font.render("ИНСТРУМЕНТЫ", True, (255, 255, 255))
    weapons_title = col_font.render("ОРУЖИЯ", True, (255, 255, 255))

    left_x = menu_rect.x + 30
    right_x = left_x + 320 + 40
    screen.blit(tools_title, tools_title.get_rect(midtop=(left_x + 160, menu_rect.top + 100)))
    screen.blit(weapons_title, weapons_title.get_rect(midtop=(right_x + 160, menu_rect.top + 100)))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    RESOURCE_NAMES = {
    'trees':    'дерево',
    'rocks':    'камень',
    'coppers':    'медь',
    'irons':    'железо',
    'titaniums': 'титан'
}

    next_tool = get_next_craftable('tool')
    next_weapon = get_next_craftable('weapon')
    for name, r in rects.items():
        recipe = CRAFT_RECIPES[name]
        kind = recipe['kind']  
        already = (recipe['kind'] == 'tool' and name in unlocked_tools) or (recipe['kind'] == 'weapon' and name in unlocked_weapons)
        next_name = next_tool if kind == 'tool' else next_weapon
        is_next = (name == next_name)
        affordable = has_resources(recipe['cost'])
        hover = r.collidepoint(mouse_x, mouse_y) and is_next and not already

        pygame.draw.rect(screen, (70, 70, 90) if hover else (50, 50, 60), r)
        if already:
            border_color = (0, 100, 0)
        elif is_next:
            if affordable:
                border_color = (0, 255, 0)
            else:
                border_color = (255, 0, 0)
        else:
            border_color = (150, 150, 150)
        pygame.draw.rect(screen, border_color, r, 2)

        icon_source = TOOL_ICONS if recipe['kind'] == 'tool' else WEAPON_ICONS
        icon = icon_source.get(name)
        if icon is not None:
            screen.blit(icon, (r.x + 5, r.y + 5))

        name_color = (120, 120, 120) if already else (255, 255, 255)
        name_surf = font.render(name, True, name_color)
        screen.blit(name_surf, (r.x + 75, r.y + 8))

        cost_parts = []
        for res, amt in recipe['cost'].items():
            cost_parts.append(f"{RESOURCE_NAMES[res]}: {amt}")
        cost_surf = small_font.render("  ".join(cost_parts), True, (200, 200, 200))
        screen.blit(cost_surf, (r.x + 75, r.y + 40))

def get_next_craftable(kind):

    if kind == 'tool':
        order = TOOL_ORDER
        unlocked = unlocked_tools
    else:
        order = WEAPON_ORDER
        unlocked = unlocked_weapons
    for name in order:
        if name not in unlocked:
            return name
    return None

#Размеры в меню паузы
pause_menu_rect = pygame.Rect(0, 0, 400, 300)
continue_button_rect = pygame.Rect(0, 0, 300, 60)
help_button_rect = pygame.Rect(0, 0, 300, 60)
music_button_rect = pygame.Rect(0, 0, 300, 60)
pause_restart_button_rect = pygame.Rect(0, 0, 300, 60)
exit_button_rect = pygame.Rect(0, 0, 300, 60)

#Центровка меню паузы
def center_pause_menu():
    global pause_menu_rect, continue_button_rect, help_button_rect, music_button_rect, pause_restart_button_rect, exit_button_rect
    
    menu_width = 500
    menu_height = 600
    menu_x = SCREEN_WIDTH // 2 - menu_width // 2
    menu_y = SCREEN_HEIGHT // 2 - menu_height // 2
    pause_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    button_width = 300
    button_height = 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    
    continue_button_rect = pygame.Rect(button_x, menu_y + 100, button_width, button_height)
    help_button_rect = pygame.Rect(button_x, menu_y + 200, button_width, button_height)
    music_button_rect = pygame.Rect(button_x, menu_y + 300, button_width, button_height)
    pause_restart_button_rect = pygame.Rect(button_x, menu_y + 400, button_width, button_height)
    exit_button_rect = pygame.Rect(button_x, menu_y + 500, button_width, button_height)
center_pause_menu()

#Отрисовка меню паузы
def draw_pause_menu():
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    pygame.draw.rect(screen, (0, 0, 0), pause_menu_rect)
    pygame.draw.rect(screen, (255, 255, 255), pause_menu_rect, 2)
    
    #Заголовок "ПАУЗА"
    title_font = pygame.font.Font(None, 88)
    title_text = title_font.render("ПАУЗА", True, (255, 255, 255))
    title_rect = title_text.get_rect(center = (pause_menu_rect.centerx, pause_menu_rect.top + 50))
    screen.blit(title_text, title_rect)
    
    #Кнопка "Продолжить"
    if continue_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), continue_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), continue_button_rect, 2)
        continue_text = font.render("Продолжить", True, (255, 255, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), continue_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), continue_button_rect, 2)
        continue_text = font.render("Продолжить", True, (255, 255, 255))
    
    continue_text_rect = continue_text.get_rect(center = continue_button_rect.center)
    screen.blit(continue_text, continue_text_rect)
    
    #Кнопка "Помощь"
    if help_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), help_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), help_button_rect, 2)
        help_text = font.render("Помощь", True, (255, 255, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), help_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), help_button_rect, 2)
        help_text = font.render("Помощь", True, (255, 255, 255))
    
    help_text_rect = help_text.get_rect(center = help_button_rect.center)
    screen.blit(help_text, help_text_rect)
    
    #Кнопка "Музыка"
    if music_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), music_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), music_button_rect, 2)
        music_text_color = (255, 255, 0)
    else:
        pygame.draw.rect(screen, (0, 0, 0), music_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), music_button_rect, 2)
        music_text_color = (255, 255, 255)
        
    #Изменение текста
    if music_playing:
        music_text_str = "Музыка: Вкл"
    else:
        music_text_str = "Музыка: Выкл"
        
    music_text = font.render(music_text_str, True, music_text_color)
    music_text_rect = music_text.get_rect(center = music_button_rect.center)
    screen.blit(music_text, music_text_rect)

    #Кнопка "Рестарт"
    if pause_restart_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), pause_restart_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), pause_restart_button_rect, 2)
        pause_restart_text = font.render("Рестарт", True, (255, 255, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), pause_restart_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), pause_restart_button_rect, 2)
        pause_restart_text = font.render("Рестарт", True, (255, 255, 255))
    
    pause_restart_text_rect = pause_restart_text.get_rect(center = pause_restart_button_rect.center)
    screen.blit(pause_restart_text, pause_restart_text_rect)
    
    #Кнопка "Выйти из игры"
    if exit_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), exit_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), exit_button_rect, 2)
        exit_text = font.render("Выйти из игры", True, (255, 255, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), exit_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), exit_button_rect, 2)
        exit_text = font.render("Выйти из игры", True, (255, 255, 255))
    
    exit_text_rect = exit_text.get_rect(center = exit_button_rect.center)
    screen.blit(exit_text, exit_text_rect)

#Плашка с помощью
help_open = False 
def draw_help_board():
        
    board_width = 500
    board_height = 600
    board_x = SCREEN_WIDTH // 2 - board_width // 2
    board_y = SCREEN_HEIGHT // 2 - board_height // 2

    board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
    pygame.draw.rect(screen, (0, 0, 0), board_rect)
    pygame.draw.rect(screen, (255, 255, 255), board_rect, 2)
    
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("ПОМОЩЬ", True, (255, 255, 255))
    title_rect = title_text.get_rect(midtop = (board_rect.centerx, board_rect.top + 25))
    screen.blit(title_text, title_rect)
    
    text_lines = [
        "Нажмите ESC чтобы вернуться",
        "========== УПРАВЛЕНИЕ ==========",
        "WASD - движение",
        "ЛКМ - атака/ломание",
        "ПКМ - взаимодействие",
        "TAB - строительство",
        "=================================",
        "P.S.: Зомби идут co всех сторон.",
        "Добудь ресурсы и воздвигни оборону.",
        "He дай им сломать монолит."
    ]
    
    y_offset = board_rect.top + 100
    for line in text_lines:
        help_text = font.render(line, True, (255, 255, 255))
        help_text_rect = help_text.get_rect(center = (board_rect.centerx, y_offset))
        screen.blit(help_text, help_text_rect)
        y_offset += 50
        continue

#Музыка
pygame.mixer.music.set_volume(0.5)
music_playing = False
pygame.mixer.music.load('music/майкл.mp3')

#Вкл/выкл музыки
def toggle_music():
    global music_playing
    
    if music_playing:
        pygame.mixer.music.stop()
        music_playing = False
    else:
        pygame.mixer.music.play(-1)
        music_playing = True

#Затемнение при смерти
dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
dark_overlay.set_alpha(200)
dark_overlay.fill((0, 0, 0))

#Экран смерти
def draw_dead_screen(player_death_time):
    
    death_text_font = pygame.font.Font(None, 64)
    death_text = death_text_font.render("ВЫ УМЕРЛИ", True, (255, 0, 0))
    text_rect = death_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(death_text, text_rect)
    
    current_time = pygame.time.get_ticks()
    time_left = max(0, (RESPAWN_DELAY - (current_time - player_death_time)) // 1000)
    timer_text = font.render(f"Возрождение через: {time_left + 1}c", True, (255, 255, 255))
    timer_rect = timer_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(timer_text, timer_rect)

#Экран конца игры
game_over_menu_rect = pygame.Rect(0, 0, 500, 500)
restart_button_rect = pygame.Rect(0, 0, 300, 60)
game_over_exit_button_rect = pygame.Rect(0, 0, 300, 60)

#Центровка экрана конца игры
def center_game_over_menu():
    global game_over_menu_rect, restart_button_rect, game_over_exit_button_rect
    
    menu_width = 500
    menu_height = 400
    menu_x = SCREEN_WIDTH // 2 - menu_width // 2
    menu_y = SCREEN_HEIGHT // 2 - menu_height // 2
    game_over_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    button_width = 300
    button_height = 60
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    
    restart_button_rect = pygame.Rect(button_x, menu_y + 200, button_width, button_height)
    game_over_exit_button_rect = pygame.Rect(button_x, menu_y + 300, button_width, button_height)
center_game_over_menu()

#Отрисовка экрана конца игры
def draw_game_over_screen():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    screen.blit(dark_overlay, (0, 0))
    pygame.draw.rect(screen, (0, 0, 0), game_over_menu_rect)
    pygame.draw.rect(screen, (255, 255, 255), game_over_menu_rect, 2)
    
    title_font = pygame.font.Font(None, 75)
    title_text = title_font.render("ИГРА ОКОНЧЕНА", True, (255, 0, 0))
    title_rect = title_text.get_rect(center=(game_over_menu_rect.centerx, game_over_menu_rect.top + 70))
    screen.blit(title_text, title_rect)
    
    subtitle_font = pygame.font.Font(None, 36)
    subtitle_text = subtitle_font.render("Монолит разрушен", True, (255, 255, 255))
    subtitle_rect = subtitle_text.get_rect(center=(game_over_menu_rect.centerx, game_over_menu_rect.top + 140))
    screen.blit(subtitle_text, subtitle_rect)
    
    #Кнопка Рестарт
    if restart_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), restart_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), restart_button_rect, 2)
        restart_text = font.render("Рестарт", True, (255, 255, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), restart_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), restart_button_rect, 2)
        restart_text = font.render("Рестарт", True, (255, 255, 255))
    restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
    screen.blit(restart_text, restart_text_rect)
    
    #Кнопка Выйти
    if game_over_exit_button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, (0, 0, 0), game_over_exit_button_rect)
        pygame.draw.rect(screen, (255, 255, 0), game_over_exit_button_rect, 2)
        exit_text = font.render("Выйти", True, (255, 255, 0))
    else:
        pygame.draw.rect(screen, (0, 0, 0), game_over_exit_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), game_over_exit_button_rect, 2)
        exit_text = font.render("Выйти", True, (255, 255, 255))
    exit_text_rect = exit_text.get_rect(center=game_over_exit_button_rect.center)
    screen.blit(exit_text, exit_text_rect)

#Рестарт игры
def restart_game():
    global player_health, player_dead, player_rect, player_visual_rect
    global monolith_health, monolith_destroyed
    global trees_count, rocks_count, coppers_count, irons_count, titaniums_count
    global wave_number, wave_points, wave_active, wave_points_spent, current_wave_enemies
    global last_wave_time, last_spawn_time, last_frame_time, game_time
    global game_over
    global music_playing
    global current_tool, current_weapon, unlocked_tools, unlocked_weapons
    global debug_hitboxes

    #Сброс времени
    game_time = 0
    last_frame_time = pygame.time.get_ticks()
    
    #Сброс игрока
    player_health = player_max_health
    player_dead = False
    SPAWN_POSITION = random.choice(SPAWN_CORNERS)
    player_rect.center = SPAWN_POSITION
    player_visual_rect.center = SPAWN_POSITION
    
    #Сброс монолита
    monolith_health = MONOLITH_MAX_HEALTH
    monolith_destroyed = False
    
    #Сброс ресурсов
    trees_count = 0
    rocks_count = 0
    coppers_count = 0
    irons_count = 0
    titaniums_count = 0

    #Сброс волн
    wave_number = 0
    wave_points = 0
    wave_points_spent = 0
    wave_active = False
    current_wave_enemies = []
    last_wave_time = game_time
    last_spawn_time = game_time

    #Сброс инструмента и оружия
    current_tool = 'none'
    current_weapon = 'none'
    unlocked_tools = {'none'}
    unlocked_weapons = {'none'}

    #Сброс музыки
    if music_playing:
        pygame.mixer.music.stop()
        music_playing = False
    
    #Удалить всех врагов
    enemies.empty()
    
    #Удалить все здания
    for building in buildings[:]:
        world.blit(grass, (building.x, building.y))
        buildings.remove(building)
    
    #Очистить словарь зданий
    buildings_coordinates['buildings'].clear()

    #Очистка мира
    clear_resources()

    #Генерация недостающих ресурсов
    respawn_resources()
    
    #Обновить препятствия
    update_obstacles()
    
    #Сброс флагов
    game_over = False
    debug_hitboxes = False

#Хитбоксы
def draw_debug_hitboxes(screen, camera_x, camera_y):
    def draw_rect(rect, color = (255, 0, 0)):
        sx = rect.x - camera_x
        sy = rect.y - camera_y
        if sx + rect.w < 0 or sy + rect.h < 0 or sx > SCREEN_WIDTH or sy > SCREEN_HEIGHT:
            return
        pygame.draw.rect(screen, color, (sx, sy, rect.w, rect.h), 1)
    draw_rect(player_rect, (255, 0, 0))
    draw_rect(monolith_rect, (255, 0, 0))
    for r in mountain_rects:
        draw_rect(r)
    for enemy in enemies:
        draw_rect(enemy.rect)
    for t in trees:      
        draw_rect(t.rect)
    for r in rocks:      
        draw_rect(r.rect)
    for c in coppers:    
        draw_rect(c.rect)
    for i in irons:      
        draw_rect(i.rect)
    for t in titaniums:
        draw_rect(t.rect)
    for b in buildings:  
        draw_rect(b.rect)
    for a in arrows:     
        draw_rect(a.rect, (255, 0, 0))

#Мир
CELL_SIZE = 128
CELLS_COUNT = 55
WORLD_WIDTH = CELLS_COUNT * CELL_SIZE
WORLD_HEIGHT = CELLS_COUNT * CELL_SIZE
world_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))

#Граница мира
def world_border():
    global player_rect

    if player_rect.left < 0:
        player_rect.left = 0
    player_visual_rect.center = player_rect.center
    if player_rect.right > WORLD_WIDTH:
        player_rect.right = WORLD_WIDTH
    player_visual_rect.center = player_rect.center
    if player_rect.top < 0:
        player_rect.top = 0
    player_visual_rect.center = player_rect.center
    if player_rect.bottom > WORLD_HEIGHT:
        player_rect.bottom = WORLD_HEIGHT
    player_visual_rect.center = player_rect.center

#Координаты по клеткам
def world_to_cell(world_x, world_y):
    cell_x = world_x // CELL_SIZE
    cell_y = world_y // CELL_SIZE
    return cell_x, cell_y

#Земля
grass = pygame.image.load('icons/grass.png')
grass = pygame.transform.scale(grass, (CELL_SIZE, CELL_SIZE))
grass_width = grass.get_width()
grass_height = grass.get_height()
for y in range(0, WORLD_HEIGHT, grass_height):
    for x in range(0, WORLD_WIDTH, grass_width):
        world.blit(grass, (x, y))

#Горы
mountain = pygame.image.load('icons/mountain.png')
mountain = pygame.transform.scale(mountain, (CELL_SIZE, CELL_SIZE))

#Пустые области
SPACE_RADIUS = 2
SPACE_CENTER_RADIUS = 4
SPACE_TRAIL_WIDTH = 2
def space_zone(cell_x, cell_y):
    center_x = CELLS_COUNT // 2
    center_y = CELLS_COUNT // 2

    #Центр
    dx = cell_x - center_x
    dy = cell_y - center_y
    if dx*dx + dy*dy <= SPACE_CENTER_RADIUS * SPACE_CENTER_RADIUS:
        return True
    
    #Вверхний спавн врагов
    if dx*dx + cell_y*cell_y <= SPACE_RADIUS * SPACE_RADIUS:
        return True

    #Спавн врагов снизу
    if dx*dx + (cell_y - (CELLS_COUNT - 1))**2 <= SPACE_RADIUS * SPACE_RADIUS:
        return True
    
    #Спавн врагов слева
    if (cell_x)**2 + dy*dy <= SPACE_RADIUS * SPACE_RADIUS:
        return True
    
    #Спавн врагов справа
    if (cell_x - (CELLS_COUNT - 1))**2 + dy*dy <= SPACE_RADIUS * SPACE_RADIUS:
        return True
    
    #Тропа вверх
    if abs(dx) <= SPACE_TRAIL_WIDTH and 0 <= cell_y <= center_y:
        return True
    
    #Тропа вниз
    if abs(dx) <= SPACE_TRAIL_WIDTH and center_y <= cell_y <= CELLS_COUNT - 1:
        return True
    
    #Тропа влево
    if abs(dy) <= SPACE_TRAIL_WIDTH and 0 <= cell_x <= center_x:
        return True
    
    #Тропа вправо
    if abs(dy) <= SPACE_TRAIL_WIDTH and center_x <= cell_x <= CELLS_COUNT - 1:
        return True
    return False

#Генерация гор по периметру
mountain_rects = []
MOUNTAIN_LAYERS = 3
def is_mountain_cell(cell_x, cell_y):
    if cell_x < 0 or cell_y < 0 or cell_x >= CELLS_COUNT or cell_y >= CELLS_COUNT:
            return False
    dist_to_edge = min(cell_x, cell_y, CELLS_COUNT - 1 - cell_x, CELLS_COUNT - 1 - cell_y)
    if dist_to_edge >= MOUNTAIN_LAYERS:
        return False
    if space_zone(cell_x, cell_y):
        return False
    return True

for cell_x in range(CELLS_COUNT):
    for cell_y in range(CELLS_COUNT):
        if is_mountain_cell(cell_x, cell_y):
            x = cell_x * CELL_SIZE
            y = cell_y * CELL_SIZE
            world.blit(mountain, (x, y))
            mountain_rects.append(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))

#Игрок
player_png = pygame.image.load('icons/player.png')
player = pygame.transform.scale(player_png, (CELL_SIZE, CELL_SIZE))
player_speed = 20
global player_health
player_health = 100
global player_max_health 
player_max_health = 100
player_visual_rect = player.get_rect()
PLAYER_SHRINK = CELL_SIZE * 0.2
player_rect = player_visual_rect.copy()
player_rect = player_rect.inflate(-PLAYER_SHRINK, -PLAYER_SHRINK)
player_rect.center = player_visual_rect.center
player_dead = False
player_death_time = 0
RESPAWN_DELAY = 10000
_cx = CELLS_COUNT // 2
_cy = CELLS_COUNT // 2
SPAWN_CORNERS = [
    ((_cx - 2) * CELL_SIZE + CELL_SIZE // 2, (_cy - 2) * CELL_SIZE + CELL_SIZE // 2),
    ((_cx + 2) * CELL_SIZE + CELL_SIZE // 2, (_cy - 2) * CELL_SIZE + CELL_SIZE // 2),
    ((_cx - 2) * CELL_SIZE + CELL_SIZE // 2, (_cy + 2) * CELL_SIZE + CELL_SIZE // 2),
    ((_cx + 2) * CELL_SIZE + CELL_SIZE // 2, (_cy + 2) * CELL_SIZE + CELL_SIZE // 2)
]
SPAWN_POSITION = random.choice(SPAWN_CORNERS)
player_visual_rect.center = SPAWN_POSITION
player_rect.center = SPAWN_POSITION

#Область атаки игрока
def get_attack_cells(player_rect):
    cx = player_rect.centerx // CELL_SIZE
    cy = player_rect.centery // CELL_SIZE
    
    cells = set()
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx) == 2 and abs(dy) == 2:
                continue
            cells.add((cx + dx, cy + dy))
    return cells

#Проверка места
def is_in_attack_area(target_rect, player_rect):
    cells = get_attack_cells(player_rect)
    tx = target_rect.centerx // CELL_SIZE
    ty = target_rect.centery // CELL_SIZE
    return (tx, ty) in cells

#Камера игрока
camera_x = 0
camera_y = 0

#Логика камеры
def camera():
    global camera_x, camera_y

    #Централизыция камеры
    camera_x = player_rect.centerx - SCREEN_WIDTH // 2
    camera_y = player_rect.centery - SCREEN_HEIGHT // 2

    #Движение камеры
    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > WORLD_WIDTH - SCREEN_WIDTH:
        camera_x = WORLD_WIDTH - SCREEN_WIDTH
    if camera_y > WORLD_HEIGHT - SCREEN_HEIGHT:
        camera_y = WORLD_HEIGHT - SCREEN_HEIGHT


#Коллизия игрока
def player_collision(dx, dy):
    global player_rect, player_visual_rect
    
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return
    
    step_x = dx / steps
    step_y = dy / steps
    
    #Движение по X
    for _ in range(int(steps)):
        player_rect.x += step_x
        if check_collision(player_rect, obstacles):
            player_rect.x -= step_x
            break
        #Проверка на врагов
        collided = False
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect):
                player_rect.x -= step_x
                collided = True
                break
        if collided:
            break
    
    #Движение по Y
    for _ in range(int(steps)):
        player_rect.y += step_y
        if check_collision(player_rect, obstacles):
            player_rect.y -= step_y
            break
        #Проверка на врагов
        collided = False
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect):
                player_rect.y -= step_y
                collided = True
                break
        if collided:
            break
    
    player_visual_rect.center = player_rect.center

#Отрисовка хп над игроком
def draw_player_health_bar(screen, player_rect, camera_x, camera_y):
    
    if not player_dead:
        bar_width = 80
        bar_height = 10
        bar_x = player_rect.centerx - bar_width // 2 - camera_x
        bar_y = player_rect.top - 25 - camera_y
        
        #Фон полоски
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        
        health_percent = player_health / player_max_health
        if health_percent > 0.5:
            color = (0, 255, 0)
        elif health_percent > 0.25:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        #Заполненная часть полоски
        health_width = int(bar_width * health_percent)
        pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))
        
        #Рамка полоски
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
    pass

#Смерть игрока
def dead_player():
    global player_health, player_dead, player_death_time 
    
    if player_health <= 0 and not player_dead:
        player_dead = True
        player_death_time = pygame.time.get_ticks()

#Возрождение игрока
def respawn_player():
    global player_health, player_dead, player_rect, player_visual_rect
    
    player_health = player_max_health
    player_dead = False
    SPAWN_POSITION = random.choice(SPAWN_CORNERS)
    player_rect.center = SPAWN_POSITION
    player_visual_rect.center = SPAWN_POSITION


#Монолит
pygame.draw.rect(world, (50, 50, 80), (WORLD_WIDTH // 2 - 64 * 3, WORLD_HEIGHT // 2 - 64 * 3, CELL_SIZE * 3, CELL_SIZE * 3))
monolith_rect = pygame.Rect(WORLD_WIDTH // 2 - 64 * 3, WORLD_HEIGHT // 2 - 64 * 3, CELL_SIZE * 3, CELL_SIZE * 3)
monolith_health = 1000
MONOLITH_MAX_HEALTH = 1000
monolith_destroyed = False

#Отрисовка хп монолита
def draw_monolith_world_health_bar(screen):

    bar_width = 320
    bar_height = 50
    bar_x = SCREEN_WIDTH - 330
    bar_y = 70
    
    #Фон полоски
    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
    
    health_percent = monolith_health / MONOLITH_MAX_HEALTH
    if health_percent > 0.5:
        color = (0, 210, 0)
    elif health_percent > 0.25:
        color = (210, 210, 0)
    else:
        color = (210, 0, 0)
    
    #Заполненная часть полоски
    health_width = int(bar_width * health_percent)
    pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))
    
    #Рамка полоски
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

#Разрушение монолита
def destruction_monolith():
    global monolith_destroyed, monolith_health
    
    if monolith_health <= 0 and not monolith_destroyed:
        monolith_destroyed = True

#Класс всех врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, health, damage, cooldown, vision_radius, image_path, size_scale=1.0, hitbox_scale=1.0):
        super().__init__()
        self.image = pygame.image.load(image_path)
        size = int(CELL_SIZE * size_scale)
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        hit_w = int(size * hitbox_scale)
        hit_h = int(size * hitbox_scale)
        self.rect = pygame.Rect(0, 0, hit_w, hit_h)
        self.rect.center = (x + size // 2, y + size // 2)
        self.image_rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.health = health
        self.max_health = health
        self.damage = damage
        self.cooldown = cooldown
        self.vision_radius = vision_radius
        self.obstacles = obstacles
        self.last_attack_time = 0
        self.distance_to_player = 0

    #Отрисовка хп над врагом
    def draw_health_bar(self, screen, camera_x, camera_y):
        bar_width = 80
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2 - camera_x
        bar_y = self.rect.top- 25 - camera_y
        
        #Фон полоски
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        
        health_percent = self.health / self.max_health
        if health_percent > 0.5:
            color = (0, 255, 0)
        elif health_percent > 0.25:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        #Заполненная часть полоски
        health_width = int(bar_width * health_percent)
        pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))
        
        #Рамка полоски
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def sync_image_rect(self):
        self.image_rect.center = self.rect.center

    #Выбор цели
    def find_target(self, player_rect):

        target_x = WORLD_WIDTH // 2
        target_y = WORLD_HEIGHT // 2

        closest_xbow = None
        closest_dist = self.vision_radius
        for building in buildings:
            if isinstance(building, XBow):
                dx = building.rect.centerx - self.rect.centerx
                dy = building.rect.centery - self.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_xbow = building
        
        if closest_xbow is not None:
            target_x = closest_xbow.rect.centerx
            target_y = closest_xbow.rect.centery

        if not player_dead:
            dx_to_player = player_rect.centerx - self.rect.centerx
            dy_to_player = player_rect.centery - self.rect.centery
            distance_to_player = math.sqrt(dx_to_player**2 + dy_to_player**2)
            if distance_to_player <= self.vision_radius:
                target_x = player_rect.centerx
                target_y = player_rect.centery

        return target_x, target_y

    #Движение к цели
    def move_to_target(self, all_enemies, player_rect):
        target_x, target_y = self.find_target(player_rect)

        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        if distance == 0:
            return

        move_x = (dx / distance) * self.speed
        move_y = (dy / distance) * self.speed

        current_time = game_time

        if move_x != 0:
            new_rect = self.rect.move(round(move_x), 0)

            blocked = check_collision(new_rect, obstacles)

            if not blocked and not player_dead and new_rect.colliderect(player_rect):
                blocked = True

            if not blocked:
                for other in all_enemies:
                    if other is not self and new_rect.colliderect(other.rect):
                        blocked = True
                        break

            if blocked:
                self.try_attack(player_rect, move_x, 0, 'x', current_time)
            else:
                self.rect = new_rect

        if move_y != 0:
            new_rect = self.rect.move(0, round(move_y))

            blocked = check_collision(new_rect, obstacles)

            if not blocked and not player_dead and new_rect.colliderect(player_rect):
                blocked = True

            if not blocked:
                for other in all_enemies:
                    if other is not self and new_rect.colliderect(other.rect):
                        blocked = True
                        break

            if blocked:
                self.try_attack(player_rect, 0, move_y, 'y', current_time)
            else:
                self.rect = new_rect
        self.sync_image_rect()

    #Попытка атаки
    def try_attack(self, player_rect, step_x, step_y, axis, current_time):
        global player_health, monolith_health
        
        if current_time - self.last_attack_time < self.cooldown:
            return
        
        check_rect = self.rect.copy()
        if axis == 'x':
            check_rect.x += step_x
        else:
            check_rect.y += step_y
        
        if not player_dead and check_rect.colliderect(player_rect):
            player_health -= self.damage
            self.last_attack_time = current_time
            return
        
        for building in buildings:
            if check_rect.colliderect(building.rect):
                if building.take_damage(self.damage):
                    world.blit(grass, (building.x, building.y))
                    buildings.remove(building)
                    remove_building_coordinates(building, building.x, building.y)
                    update_obstacles()
                self.last_attack_time = current_time
                return
        
        if check_rect.colliderect(monolith_rect):
            monolith_health -= self.damage
            self.last_attack_time = current_time
            return

#Зомби
class Zombie(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed = 20, health = 100, damage = 20, cooldown = 1500, vision_radius = CELL_SIZE * 4, image_path = 'icons/zombie.png', size_scale=1.0, hitbox_scale=0.9)
        self.max_health = 100

#Быстрый зомби
class Fast_zombie(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed = 30, health = 50, damage = 20, cooldown = 1000, vision_radius = CELL_SIZE * 4, image_path = 'icons/zombie.png', size_scale=0.8, hitbox_scale=0.9)
        self.max_health = 50

#Танк зомби
class Tank_zombie(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed = 10, health = 250, damage = 50, cooldown = 3000, vision_radius = CELL_SIZE * 4, image_path = 'icons/zombie.png', size_scale=1.4, hitbox_scale=0.9)
        self.max_health = 250

enemies = pygame.sprite.Group()

#Система волн
wave_number = 0
wave_points = 0
wave_points_spent = 0
spawn_delay = 1500
last_spawn_time = 0
FIRST_WAVE_DELAY = 80000
WAVE_DELAY_DECREASE = 10000
MIN_WAVE_DELAY = 20000
last_wave_time = 0
wave_active = False
current_wave_enemies = []

#Стоимость врагов
ENEMY_COSTS = {
    'zombie': 3,
    'fast_zombie': 5,
    'tank_zombie': 10
}

#Время между волнами
def get_wave_delay():
    global wave_number
    
    if wave_number == 0:
        return FIRST_WAVE_DELAY
    else:
        delay = max(MIN_WAVE_DELAY, FIRST_WAVE_DELAY - wave_number * WAVE_DELAY_DECREASE)
        return delay

#Враги на волну
def get_enemies_for_wave(wave, available_points):
    enemies_list = []
    remaining_points = available_points
    
    #Доступные враги
    available_types = ['zombie']
    if wave >= 2:
        available_types.extend(['fast_zombie'])
    if wave >= 3:
        available_types.extend(['tank_zombie'])

    #Трата очков волной
    min_cost = min(ENEMY_COSTS.values())
    while remaining_points >= min_cost:
        enemy_type = random.choice(available_types)
        cost = ENEMY_COSTS[enemy_type]
        
        if cost <= remaining_points:
            enemies_list.append(enemy_type)
            remaining_points -= cost
        else:
            cheapest_type = min(ENEMY_COSTS, key = ENEMY_COSTS.get)
            if ENEMY_COSTS[cheapest_type] <= remaining_points:
                enemies_list.append(cheapest_type)
                remaining_points -= ENEMY_COSTS[cheapest_type]
            else:
                break

    random.shuffle(enemies_list)

    non_tanks = [e for e in enemies_list if e != 'tank_zombie']
    tanks = [e for e in enemies_list if e == 'tank_zombie']
    return non_tanks + tanks

#Начинаем новую волну
def start_new_wave():
    global wave_number, wave_points, wave_active, last_spawn_time, current_wave_enemies, last_wave_time, monolith_health, game_time
    
    wave_number += 1
    wave_active = True

    last_wave_time = game_time 
    wave_points = 10 + (wave_number - 1) * 5
    current_wave_enemies = get_enemies_for_wave(wave_number, wave_points)

    if monolith_health <= 750:
        monolith_health += 250
    else:
        monolith_health = MONOLITH_MAX_HEALTH

    if wave_number > 0 and wave_number % 5 == 0:
        respawn_resources()

    spawn_enemy_from_wave()
    last_spawn_time = game_time

#Спавн врагов
def spawn_enemy_from_wave():
    global current_wave_enemies
    
    if not current_wave_enemies:
        return False
    
    enemy_type = current_wave_enemies.pop(0)

    #Выбираем место спавна
    spawn_zone = random.randint(0, 3)
    if spawn_zone == 0:
        x = WORLD_WIDTH // 2 - CELL_SIZE // 2
        y = 0
    elif spawn_zone == 1:
        x = WORLD_WIDTH // 2 - CELL_SIZE // 2
        y = WORLD_HEIGHT - CELL_SIZE
    elif spawn_zone == 2:
        x = 0
        y = WORLD_HEIGHT // 2 - CELL_SIZE // 2
    else:
        x = WORLD_WIDTH - CELL_SIZE
        y = WORLD_HEIGHT // 2 - CELL_SIZE // 2

    #Спавним врага
    if enemy_type == 'zombie':
        new_enemy = Zombie(x, y)
    elif enemy_type == 'tank_zombie':
        new_enemy = Tank_zombie(x, y)
    elif enemy_type == 'fast_zombie':
        new_enemy = Fast_zombie(x, y)
    else:
        new_enemy = Zombie(x, y)
    
    enemies.add(new_enemy)
    return True

#Обновление волн
def update_wave_system():
    global wave_active, last_wave_time, last_spawn_time, wave_number, current_wave_enemies, game_time
    
    current_time = game_time

    if not wave_active:
        if wave_number == 0:
            if last_wave_time == 0:
                last_wave_time = current_time
            if current_time - last_wave_time >= get_wave_delay():
                start_new_wave()
            return
        if current_time - last_wave_time >= get_wave_delay():
            start_new_wave()
        return
        
    if current_wave_enemies:
        if current_time - last_spawn_time >= spawn_delay:
            spawn_enemy_from_wave()
            last_spawn_time = current_time
    else:
        if len(enemies) == 0:
            wave_active = False
            last_wave_time = current_time

#Рисуем время до волны и кол-во врагов
def draw_wave_info(screen):
    global last_wave_time
    global time_left

    current_time = game_time

    bg_rect = pygame.Rect(SCREEN_WIDTH - 330, 10, 320, 50)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)

    if not wave_active:
        if wave_number == 0:
            if last_wave_time == 0:
                last_wave_time = current_time
            time_left = max(0, (get_wave_delay() - (current_time - last_wave_time)) // 1000)
            timer_text = font.render(f"Следующая волна: {time_left + 1}c", True, (255, 255, 0))
            screen.blit(timer_text, (SCREEN_WIDTH - 322, 22))
        else:
            time_left = max(0, (get_wave_delay() - (current_time - last_wave_time)) // 1000)
            timer_text = font.render(f"Следующая волна: {time_left + 1}c", True, (255, 255, 0))
            screen.blit(timer_text, (SCREEN_WIDTH - 322, 22))
    elif wave_active:
        remaining = len(current_wave_enemies) + len(enemies)
        info_font = pygame.font.Font(None, 30)
        info_text = info_font.render(f"Волна {wave_number}: {remaining} врагов осталось", True, (255, 255, 0))
        screen.blit(info_text, (SCREEN_WIDTH - 322, 26))

#Класс природных объектов
class Nature:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def redraw_tree_above(self, world):
        cell_x, cell_y = world_to_cell(self.x, self.y)
        trunk_key = (cell_x, cell_y + 1)
        
        if trunk_key in nature_coordinates['trees']:
            for tree in nature_coordinates['trees'][trunk_key]:
                tree.draw_crown(world)

#Деревья
class Tree(Nature):
    def __init__(self, x, y):
        super().__init__(x, y, 'icons/trunk.png')
        self.rect.x = x
        self.rect.y = y
        self.trunk_image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.crown_x = x
        self.crown_y = y - CELL_SIZE
        self.crown_image = pygame.image.load('icons/crown.png')
        self.crown_image = pygame.transform.scale(self.crown_image, (CELL_SIZE, CELL_SIZE))
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

    def draw_crown(self, surface):
        surface.blit(self.crown_image, (self.crown_x, self.crown_y))
    
    def draw_trunk(self, surface):
        surface.blit(self.image, (self.x, self.y))
    
    def get_object_above(self):
        cell_x, cell_y = world_to_cell(self.x, self.y)
        key_above = (cell_x, cell_y - 1)
        
        for obj_type in ['trees', 'rocks', 'coppers', 'irons', 'titaniums']:
            if key_above in nature_coordinates[obj_type]:
                obj = nature_coordinates[obj_type][key_above][0]
                return obj_type, obj
        return None, None

#Камни
class Rock(Nature):
    def __init__(self, x, y):
        super().__init__(x, y, 'icons/rock.png')
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

#Медь
class Copper(Nature):
    def __init__(self, x, y):
        super().__init__(x, y, 'icons/copper.png')
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

#Железо
class Iron(Nature):
    def __init__(self, x, y):
        super().__init__(x, y, 'icons/iron.png')
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

#Титан
class Titanium(Nature):
    def __init__(self, x, y):
        super().__init__(x, y, 'icons/titanium.png')
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

#Списки объектов
trees = []
rocks = []
coppers = []
irons = []
titaniums = []

#Словарь координат объектов
nature_coordinates = {
    'trees': {},
    'rocks': {},
    'coppers': {},
    'irons': {},
    'titaniums': {}
}

#Добавление в словарь
def add_object_coordinates(obj, obj_type, x, y):
    cell_x, cell_y = world_to_cell(x, y)
    key = (cell_x, cell_y)
    if key not in nature_coordinates[obj_type]:
        nature_coordinates[obj_type][key] = []
    nature_coordinates[obj_type][key].append(obj)

#Удаление из словаря
def remove_object_coordinates(obj, obj_type, x, y):
    cell_x, cell_y = world_to_cell(x, y)
    key = (cell_x, cell_y)
    if key in nature_coordinates[obj_type]:
        if obj in nature_coordinates[obj_type][key]:
            nature_coordinates[obj_type][key].remove(obj)
        if not nature_coordinates[obj_type][key]:
            del nature_coordinates[obj_type][key]

#Все объекты
def get_all_objects():
    return trees + rocks + coppers + irons + titaniums

#Проверка занятости места другим объектом
def is_position_occupied(x, y, obj):
    new_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    for obj in get_all_objects():
        if new_rect.colliderect(obj.rect):
            return True
    return False

#Число объектов
TREES_COUNT     = 900
ROCKS_COUNT     = 100
COPPERS_COUNT   = 55
IRONS_COUNT     = 30
TITANIUMS_COUNT = 15

#Генерируем деревья
for _ in range(TREES_COUNT):
    while True:
        cell_x = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        cell_y = random.randint(MOUNTAIN_LAYERS + 1, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        x = cell_x * CELL_SIZE
        y = cell_y * CELL_SIZE

        if space_zone(cell_x, cell_y):
            continue
        if not is_position_occupied(x, y, get_all_objects):
            break

    tree = Tree(x, y)
    trees.append(tree)
    add_object_coordinates(tree, 'trees', x, y)

#Генерируем камни
for _ in range(ROCKS_COUNT):
    while True:
        cell_x = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        cell_y = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        x = cell_x * CELL_SIZE
        y = cell_y * CELL_SIZE
        
        if space_zone(cell_x, cell_y):
            continue
        if not is_position_occupied(x, y, get_all_objects):
            break
    
    rock = Rock(x, y)
    rocks.append(rock)
    rock.draw(world)
    add_object_coordinates(rock, 'rocks', x, y)

#Генерируем медь
for _ in range(COPPERS_COUNT):
    while True:
        cell_x = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        cell_y = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        x = cell_x * CELL_SIZE
        y = cell_y * CELL_SIZE
        
        if space_zone(cell_x, cell_y):
            continue
        if not is_position_occupied(x, y, get_all_objects):
            break
    
    copper = Copper(x, y)
    coppers.append(copper)
    copper.draw(world)
    add_object_coordinates(copper, 'coppers', x, y)

#Генерируем железо
for _ in range(IRONS_COUNT):
    while True:
        cell_x = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        cell_y = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        x = cell_x * CELL_SIZE
        y = cell_y * CELL_SIZE
        
        if space_zone(cell_x, cell_y):
            continue
        if not is_position_occupied(x, y, get_all_objects):
            break
    
    iron = Iron(x, y)
    irons.append(iron)
    iron.draw(world)
    add_object_coordinates(iron, 'irons', x, y)

#Генерируем титан
for _ in range(TITANIUMS_COUNT):
    while True:
        cell_x = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        cell_y = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
        x = cell_x * CELL_SIZE
        y = cell_y * CELL_SIZE
        
        if space_zone(cell_x, cell_y):
            continue
        if not is_position_occupied(x, y, get_all_objects):
            break
    
    titanium = Titanium(x, y)
    titaniums.append(titanium)
    titanium.draw(world)
    add_object_coordinates(titanium, 'titaniums', x, y)

#Отрисовка деревьев
def draw_sorted_trees():
    sorted_trees = sorted(trees, key = lambda tree: tree.y)
    
    for tree in sorted_trees:
        tree.draw_crown(world)
        tree.draw_trunk(world)
draw_sorted_trees() 

#Все приородные объекты
RESOURCE_TARGETS = {
    'trees': TREES_COUNT,
    'rocks': ROCKS_COUNT,
    'coppers': COPPERS_COUNT,
    'irons': IRONS_COUNT,
    'titaniums': TITANIUMS_COUNT
}

#Спавн недостающих объектов
def respawn_resources():

    need_trees     = max(0, RESOURCE_TARGETS['trees']     - len(trees))
    need_rocks     = max(0, RESOURCE_TARGETS['rocks']     - len(rocks))
    need_coppers   = max(0, RESOURCE_TARGETS['coppers']   - len(coppers))
    need_irons     = max(0, RESOURCE_TARGETS['irons']     - len(irons))
    need_titaniums = max(0, RESOURCE_TARGETS['titaniums'] - len(titaniums))

    if need_trees == need_rocks == need_coppers == need_irons == need_titaniums == 0:
        return

    plan = (
        ('trees',     need_trees,     Tree,     trees,     True),
        ('rocks',     need_rocks,     Rock,     rocks,     False),
        ('coppers',   need_coppers,   Copper,   coppers,   False),
        ('irons',     need_irons,     Iron,     irons,     False),
        ('titaniums', need_titaniums, Titanium, titaniums, False),
    )

    for key, count, cls, lst, is_tree in plan:
        for _ in range(count):
            while True:
                cell_x = random.randint(MOUNTAIN_LAYERS, CELLS_COUNT - MOUNTAIN_LAYERS - 1)
                cell_y_min = MOUNTAIN_LAYERS + 1 if is_tree else MOUNTAIN_LAYERS
                cell_y = random.randint(cell_y_min, CELLS_COUNT - MOUNTAIN_LAYERS - 1)

                x = cell_x * CELL_SIZE
                y = cell_y * CELL_SIZE

                if space_zone(cell_x, cell_y):
                    continue

                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                if is_position_occupied(x, y, get_all_objects):
                    continue
                if any(b.rect.colliderect(cell_rect) for b in buildings):
                    continue
                if player_rect.colliderect(cell_rect):
                    continue

                break

            obj = cls(x, y)
            lst.append(obj)
            add_object_coordinates(obj, key, x, y)

            if not is_tree:
                obj.draw(world)

    if need_trees > 0:
        for t in sorted(trees, key=lambda tr: tr.y):
            t.draw_crown(world)
            t.draw_trunk(world)

    update_obstacles()

#Очитска мира для рестарта
def clear_resources():

    for t in trees:
        world.blit(grass, (t.x, t.crown_y))
        world.blit(grass, (t.x, t.y))
    for r in rocks:
        world.blit(grass, (r.x, r.y))
    for c in coppers:
        world.blit(grass, (c.x, c.y))
    for i in irons:
        world.blit(grass, (i.x, i.y))
    for t in titaniums:
        world.blit(grass, (t.x, t.y))

    trees.clear()
    rocks.clear()
    coppers.clear()
    irons.clear()
    titaniums.clear()

    for key in nature_coordinates:
        nature_coordinates[key].clear()

    update_obstacles()

#Коллизия
def check_collision(rect, obstacles):
    for obstacle in obstacles:
        if rect.colliderect(obstacle):
            return True
    return False

#Удаление ресурсов
def handle_resource(resource_list, world_mouse_x, world_mouse_y, player_rect, world, grass, resource_class):
    global trees_count, rocks_count, coppers_count, irons_count, titaniums_count

    resource_type = None
    if resource_class == Tree:
        resource_type = 'trees'
    elif resource_class == Rock:
        resource_type = 'rocks'
    elif resource_class == Copper:
        resource_type = 'coppers'
    elif resource_class == Iron:
        resource_type = 'irons'
    elif resource_class == Titanium:
        resource_type = 'titaniums'

    if resource_type is None:
        return False
    
    hits_needed = HITS_TABLE.get(current_tool, HITS_TABLE['none'])[resource_type]
    if hits_needed == 0:
        return False

    for resource in resource_list[:]:
        if not resource.rect.collidepoint(world_mouse_x, world_mouse_y):
            continue
        if not is_in_attack_area(resource.rect, player_rect):
            continue

        if not hasattr(resource, 'hits_left') or resource.hits_left is None:
            resource.hits_left = hits_needed

        resource.hits_left -= 1
        spawn_resource_particles(resource, resource_type)
        if resource.hits_left > 0:
            return False

        if resource_class == Tree:
            world.blit(grass, (resource.x, resource.y - CELL_SIZE))
            world.blit(grass, (resource.x, resource.y))

            above_type, obj_above = resource.get_object_above()
            if obj_above is not None:
                obj_above.draw(world)
                if isinstance(obj_above, Tree):
                    obj_above.draw_crown(world)
            resource.redraw_tree_above(world)
        else:
            world.blit(grass, (resource.x, resource.y))
            resource.redraw_tree_above(world)

        remove_object_coordinates(resource, resource_type, resource.x, resource.y)
        resource_list.remove(resource)
        update_obstacles()

        if resource_class == Tree:
            trees_count += 1
        elif resource_class == Rock:
            rocks_count += 1
        elif resource_class == Copper:
            coppers_count += 1
        elif resource_class == Iron:
            irons_count += 1
        elif resource_class == Titanium:
            titaniums_count += 1

        return True
    return False

#Класс зданий
class Buildings:
    def __init__(self, x, y, health, image_path, building_type):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = health
        self.max_health = health
        self.building_type = building_type

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw_health_bar(self, screen, camera_x, camera_y):

        if self.health >= self.max_health:
            return
        
        bar_width = 80
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2 - camera_x
        bar_y = self.rect.top - 25 - camera_y
        
        #Фон полоски
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        
        health_percent = self.health / self.max_health
        if health_percent > 0.5:
            color = (0, 255, 0)
        elif health_percent > 0.25:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        #Заполненная часть полоски
        health_width = int(bar_width * health_percent)
        if health_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))
        
        #Рамка полоски
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

#Стена
class Wall(Buildings):
    def __init__(self, x, y):
        super().__init__(x, y, health = 100, image_path = 'icons/wall.png', building_type = 'wall')
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

#Арбалет
class XBow(Buildings):
    def __init__(self, x, y):
        super().__init__(x, y, health = 50, image_path = 'icons/xbow.png', building_type = 'xbow')
        self.damage = 20
        self.fire_rate = 1000
        self.last_shot_time = 0
        self.range = CELL_SIZE * 5
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)
    
    def find_target(self):
        closest = None
        closest_dist = self.range
        
        for enemy in enemies:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= closest_dist:
                closest_dist = dist
                closest = enemy
        
        return closest
    
    def update(self):
        if game_time - self.last_shot_time < self.fire_rate:
            return
        
        target = self.find_target()
        if target is None:
            return
        
        arrow = Arrow(self.rect.centerx, self.rect.centery, target, speed = 20, damage = self.damage, max_distance = self.range + CELL_SIZE * 2)
        arrows.append(arrow)
        self.last_shot_time = game_time

#Стрела
class Arrow:
    def __init__(self, x, y, target, speed, damage, max_distance):
        self.x = x
        self.y = y
        self.target = target
        self.speed = speed
        self.damage = damage
        self.max_distance = max_distance
        self.traveled = 0
        
        dx = target.rect.centerx - x
        dy = target.rect.centery - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist
        else:
            self.dir_x = 0
            self.dir_y = -1

        angle = math.degrees(math.atan2(self.dir_y, self.dir_x)) + 90
        self.angle = -angle
        
        original = pygame.image.load('icons/arrow.png')
        original = pygame.transform.scale(original, (32, 32))
        self.image = pygame.transform.rotate(original, self.angle)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.alive = True
    
    def update(self):
        if not self.alive:
            return

        step_x = self.dir_x * self.speed
        step_y = self.dir_y * self.speed
        self.rect.x += step_x
        self.rect.y += step_y
        self.traveled += math.sqrt(step_x**2 + step_y**2)
        
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= self.damage
                if enemy.health <= 0:
                    enemy.kill()
                self.alive = False
                return
        
        if self.traveled >= self.max_distance:
            self.alive = False
            return
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

#Список стрел
arrows = []

#Верстак
class CraftingTable(Buildings):
    def __init__(self, x, y):
        super().__init__(x, y, health=50, image_path='icons/crafting table.png', building_type='crafting table')
        shrink = CELL_SIZE * 0.1
        self.rect = self.rect.inflate(-shrink, -shrink)

#Список зданий
buildings = []

#Словарь зданий
buildings_coordinates = {'buildings': {}}

#Добавление здания в словарь
def add_building_coordinates(obj, x, y):
    cell_x, cell_y = world_to_cell(x, y)
    key = (cell_x, cell_y)
    if key not in buildings_coordinates['buildings']:
        buildings_coordinates['buildings'][key] = []
    buildings_coordinates['buildings'][key].append(obj)

#Удаление здания из словаря
def remove_building_coordinates(obj, x, y):
    cell_x, cell_y = world_to_cell(x, y)
    key = (cell_x, cell_y)
    if key in buildings_coordinates['buildings']:
        if obj in buildings_coordinates['buildings'][key]:
            buildings_coordinates['buildings'][key].remove(obj)
        if not buildings_coordinates['buildings'][key]:
            del buildings_coordinates['buildings'][key]

#Проверка наличия ресурсов для строительства
def has_resources(cost):
    for resource_type, amount in cost.items():
        if resource_type == 'trees' and trees_count < amount:
            return False
        elif resource_type == 'rocks' and rocks_count < amount:
            return False
        elif resource_type == 'coppers' and coppers_count < amount:
            return False
        elif resource_type == 'irons' and irons_count < amount:
            return False
        elif resource_type == 'titaniums' and titaniums_count < amount:
            return False
    return True

#Списание ресурсов
def spend_resources(cost):
    global trees_count, rocks_count, coppers_count, irons_count, titaniums_count
    
    for resource_type, amount in cost.items():
        if resource_type == 'trees':
            trees_count -= amount
        elif resource_type == 'rocks':
            rocks_count -= amount
        elif resource_type == 'coppers':
            coppers_count -= amount
        elif resource_type == 'irons':
            irons_count -= amount
        elif resource_type == 'titaniums':
            titaniums_count -= amount

#Строительство
build_mode = False
build_selected = None
build_menu_open = False
build_message = ""
build_message_until = 0
BUILD_ICONS = {
    'wall':  load_icon('icons/wall.png',            ICON_SIZE),
    'xbow':  load_icon('icons/xbow.png',            ICON_SIZE),
    'table': load_icon('icons/crafting table.png',  ICON_SIZE)
}

#Список зданий для меню
def get_build_list():
    return [
        ('table', 'Верстак',  CraftingTable,  {'trees': 2}),
        ('xbow',  'Арбалет',  XBow,           {'trees': 3, 'coppers': 3}),
        ('wall',  'Стена',    Wall,           {'trees': 3})
    ]

def get_building_class(key):
    for k, name, cls, cost in get_build_list():
        if k == key:
            return cls
    return None

def get_building_cost(key):
    for k, name, cls, cost in get_build_list():
        if k == key:
            return cost
    return None

def get_building_name(key):
    for k, name, cls, cost in get_build_list():
        if k == key:
            return name
    return ''

#Можно ли строить в клетке
def can_build_at(cell_rect, cost):
    x, y = cell_rect.x, cell_rect.y

    if is_position_occupied(x, y, get_all_objects):
        return 'blocked'
    if cell_rect.colliderect(monolith_rect):
        return 'blocked'
    if check_collision(cell_rect, mountain_rects):
        return 'blocked'
    for b in buildings:
        if cell_rect.colliderect(b.rect):
            return 'blocked'
    for e in enemies:
        if cell_rect.colliderect(e.rect):
            return 'blocked'
    if player_rect.colliderect(cell_rect):
        return 'blocked'
    if not is_in_attack_area(cell_rect, player_rect):
        return 'out_of_range'
    if not has_resources(cost):
        return 'no_resources'
    return 'ok'

def get_build_menu_rects():
    menu_w, menu_h = 520, 380
    mx = SCREEN_WIDTH // 2 - menu_w // 2
    my = SCREEN_HEIGHT // 2 - menu_h // 2
    menu_rect = pygame.Rect(mx, my, menu_w, menu_h)

    item_w, item_h = menu_w - 60, 80
    gap_y = 15
    x0 = mx + 30
    y0 = my + 80

    rects = {}
    items = get_build_list()
    for i, (key, name, cls, cost) in enumerate(items):
        r = pygame.Rect(x0, y0 + i * (item_h + gap_y), item_w, item_h)
        rects[key] = r

    return menu_rect, rects

def draw_build_menu():

    menu_rect, rects = get_build_menu_rects()

    pygame.draw.rect(screen, (0, 0, 0), menu_rect)
    pygame.draw.rect(screen, (255, 255, 255), menu_rect, 2)

    title_font = pygame.font.Font(None, 52)
    title = title_font.render("СТРОИТЕЛЬСТВО", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(menu_rect.centerx, menu_rect.top + 35)))

    hint = small_font.render("ESC - закрыть", True, (255, 255, 255))
    screen.blit(hint, hint.get_rect(center=(menu_rect.centerx, menu_rect.top + 62)))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    RESOURCE_NAMES = {
        'trees': 'дерево',
        'rocks': 'камень',
        'coppers': 'медь',
        'irons': 'железо',
        'titaniums': 'титан',
    }

    for key, name, cls, cost in get_build_list():
        r = rects[key]
        hover = r.collidepoint(mouse_x, mouse_y)
        selected = (build_selected == key)
        affordable = has_resources(cost)

        bg = (70, 70, 90) if hover else (50, 50, 60)
        pygame.draw.rect(screen, bg, r)

        if selected:
            border = (0, 255, 0)
        elif hover:
            border = (255, 255, 0)
        else:
            border = (150, 150, 150)
        pygame.draw.rect(screen, border, r, 2)

        icon = BUILD_ICONS.get(key) if 'BUILD_ICONS' in globals() else None
        if icon is not None:
            screen.blit(icon, (r.x + 5, r.y + 10))

        name_color = (255, 255, 255) if affordable else (150, 150, 150)
        name_surf = font.render(name, True, name_color)
        screen.blit(name_surf, (r.x + 75, r.y + 10))

        cost_parts = []
        for res, amt in cost.items():
            cost_parts.append(f"{RESOURCE_NAMES[res]}: {amt}")
        cost_color = (0, 255, 0) if affordable else (255, 80, 80)
        cost_surf = small_font.render("  ".join(cost_parts), True, cost_color)
        screen.blit(cost_surf, (r.x + 75, r.y + 45))

        if selected:
            mark = small_font.render("выбрано", True, (0, 255, 0))
            screen.blit(mark, mark.get_rect(midright=(r.right - 10, r.centery)))

def draw_build_mode():
    if not build_mode or build_selected is None:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()
    world_mouse_x = mouse_x + camera_x
    world_mouse_y = mouse_y + camera_y

    cell_x = world_mouse_x // CELL_SIZE
    cell_y = world_mouse_y // CELL_SIZE

    if cell_x < 0 or cell_y < 0 or cell_x >= CELLS_COUNT or cell_y >= CELLS_COUNT:
        return

    x = cell_x * CELL_SIZE
    y = cell_y * CELL_SIZE
    cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    cost = get_building_cost(build_selected)
    status = can_build_at(cell_rect, cost)

    sx = x - camera_x
    sy = y - camera_y

    icon = BUILD_ICONS.get(build_selected)
    if icon is not None:
        ghost = pygame.transform.scale(icon, (CELL_SIZE, CELL_SIZE))
        ghost.set_alpha(140)
        if status in ('blocked', 'no_resources', 'out_of_range'):
            tint = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            tint.fill((100, 0, 0, 60))
            ghost.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        screen.blit(ghost, (sx, sy))

def draw_build_mode_hint(screen):
    if not build_mode:
        return

    line1_font = pygame.font.Font(None, 44)
    line2_font = pygame.font.Font(None, 28)

    line1 = line1_font.render("РЕЖИМ СТРОИТЕЛЬСТВА АКТИВИРОВАН", True, (255, 255, 255))
    line2 = line2_font.render("Чтобы выбрать здание, нажмите ПКМ", True, (255, 255, 255))

    cx = SCREEN_WIDTH // 2
    y1 = 20
    y2 = y1 + line1.get_height() + 4

    screen.blit(line1, line1.get_rect(center=(cx, y1 + line1.get_height() // 2)))
    screen.blit(line2, line2.get_rect(center=(cx, y2 + line2.get_height() // 2)))

#Сообщение, почему нельзя строить
TEXT_LIVE_TIME = 3000
def show_build_message(text, duration=TEXT_LIVE_TIME):
    global build_message, build_message_until
    build_message = text
    build_message_until = pygame.time.get_ticks() + duration

#Атака зданий
def attack_building(world_mouse_x, world_mouse_y):
    global buildings
    
    for building in buildings[:]:
        if building.rect.collidepoint(world_mouse_x, world_mouse_y):
            if is_in_attack_area(building.rect, player_rect):
                if building.take_damage(get_player_damage()):
                    world.blit(grass, (building.x, building.y))
                    buildings.remove(building)
                    remove_building_coordinates(building, building.x, building.y)
                    update_obstacles()
                return True
    return False

#Обновление списка препятствий
def update_obstacles():
    global obstacles
    obstacles = [monolith_rect, *mountain_rects]
    for tree in trees:
        obstacles.append(tree.rect)
    for rock in rocks:
        obstacles.append(rock.rect)
    for copper in coppers:
        obstacles.append(copper.rect)
    for iron in irons:
        obstacles.append(iron.rect)
    for titanium in titaniums:
        obstacles.append(titanium.rect)
    for building in buildings:
        obstacles.append(building.rect)
    return obstacles
obstacles = update_obstacles()

#Главный цикл
paused = False
debug_hitboxes = False
game_over = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if monolith_destroyed and not game_over:
            game_over = True

        #Кнопки
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if build_menu_open:
                    build_menu_open = False
                elif crafting_open:
                    crafting_open = False
                elif game_over:
                    pass
                elif help_open:
                    help_open = False
                else:
                    if not player_dead:
                        paused = not paused
            if event.key == pygame.K_TAB:
                build_mode = not build_mode
            if event.key == pygame.K_h:
                debug_hitboxes = not debug_hitboxes
            if event.key == pygame.K_p:
                trees_count = rocks_count = coppers_count = irons_count = titaniums_count = 1000

        #Мышь
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if build_menu_open:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                menu_rect, rects = get_build_menu_rects()
                for key, r in rects.items():
                    if r.collidepoint(mouse_x, mouse_y):
                        build_selected = key
                        build_menu_open = False
                        break
                continue

            if build_mode and build_selected is not None and not paused and not game_over and not player_dead and not crafting_open and not help_open:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x + camera_x
                world_mouse_y = mouse_y + camera_y
                cell_x = world_mouse_x // CELL_SIZE
                cell_y = world_mouse_y // CELL_SIZE
                x = cell_x * CELL_SIZE
                y = cell_y * CELL_SIZE
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                cost = get_building_cost(build_selected)
                status = can_build_at(cell_rect, cost)
                if status == 'ok':
                    spend_resources(cost)
                    cls = get_building_class(build_selected)
                    building = cls(x, y)
                    buildings.append(building)
                    building.draw(world)
                    add_building_coordinates(building, x, y)
                    update_obstacles()
                    build_last_cell = (cell_x, cell_y)
                elif status == 'blocked':
                    show_build_message("Место занято")
                elif status == 'no_resources':
                    show_build_message("Не хватает ресурсов")
                elif status == 'out_of_range':
                    show_build_message("Слишком далеко")
                continue
        if event.type == pygame.MOUSEMOTION:
            if build_mode and build_selected is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x + camera_x
                world_mouse_y = mouse_y + camera_y
                cell_x = world_mouse_x // CELL_SIZE
                cell_y = world_mouse_y // CELL_SIZE

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if build_menu_open:
                build_menu_open = False
            elif build_mode:
                build_menu_open = True
            elif not paused and not game_over and not player_dead:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x + camera_x
                world_mouse_y = mouse_y + camera_y
                for building in buildings:
                    if isinstance(building, CraftingTable) and building.rect.collidepoint(world_mouse_x, world_mouse_y):
                        if is_in_attack_area(building.rect, player_rect):
                            crafting_open = True
                            break
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if crafting_open:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                menu_rect, rects = get_craft_menu_rects()
                clicked_item = False
                for name, r in rects.items():
                    if r.collidepoint(mouse_x, mouse_y):
                        try_craft(name)
                        clicked_item = True
                        break
                continue
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y
            if game_over:
                if restart_button_rect.collidepoint(mouse_x, mouse_y):
                    restart_game()
                elif game_over_exit_button_rect.collidepoint(mouse_x, mouse_y):
                    running = False
            if paused:
                if not help_open:
                    if continue_button_rect.collidepoint(mouse_x, mouse_y):
                        paused = False
                    elif help_button_rect.collidepoint(mouse_x, mouse_y):
                        draw_help_board()
                        help_open = True
                    elif music_button_rect.collidepoint(mouse_x, mouse_y):
                        toggle_music()
                    elif pause_restart_button_rect.collidepoint(mouse_x, mouse_y):
                        restart_game()
                        paused = False 
                    elif exit_button_rect.collidepoint(mouse_x, mouse_y):
                        running = False
            else:
                #Проверяем, попали ли на ресурс
                if not player_dead:
                    hit = False
                    if not hit:
                        hit = handle_resource(trees, world_mouse_x, world_mouse_y, player_rect, world, grass, Tree)
                    if not hit:
                        hit = handle_resource(rocks, world_mouse_x, world_mouse_y, player_rect, world, grass, Rock)
                    if not hit:
                        hit = handle_resource(coppers, world_mouse_x, world_mouse_y, player_rect, world, grass, Copper)
                    if not hit:
                        hit = handle_resource(irons, world_mouse_x, world_mouse_y, player_rect, world, grass, Iron)
                    if not hit:
                        hit = handle_resource(titaniums, world_mouse_x, world_mouse_y, player_rect, world, grass, Titanium)
                    if not hit:
                        hit = attack_building(world_mouse_x, world_mouse_y)
                    #Проверяем, попали ли на врага
                    if not hit:
                        for enemy in reversed(enemies.sprites()):
                            if enemy.rect.collidepoint(world_mouse_x, world_mouse_y):
                                if is_in_attack_area(enemy.rect, player_rect):
                                    enemy.health -= get_player_damage()
                                    if enemy.health <= 0:
                                        enemy.kill()
                                    break

    if game_over:
        screen.blit(world_surface, (0, 0), (camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_game_over_screen()
        pygame.display.flip()
        clock.tick(60)
        continue

    update_game_time()  
    if not paused:
        if not player_dead:

            #Управление
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            if not build_menu_open and not crafting_open:
                if keys[pygame.K_w]:
                    dy -= player_speed
                if keys[pygame.K_s]:
                    dy += player_speed
                if keys[pygame.K_a]:
                    dx -= player_speed
                if keys[pygame.K_d]:
                    dx += player_speed

            #Движение игрока
            if dx != 0 or dy != 0:
                player_collision(dx, dy)
                player_cell_x, player_cell_y = world_to_cell(player_rect.centerx, player_rect.centery)

            #Вызовы функций
            for enemy in enemies:
                enemy.move_to_target(enemies, player_rect)

            #Обновление арбалетов
            for building in buildings:
                if isinstance(building, XBow):
                    building.update()

            #Обновление стрел
            for arrow in arrows[:]:
                arrow.update()
                if not arrow.alive:
                    arrows.remove(arrow)

            #Обновление частиц
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)
            update_wave_system()
            dead_player()
            destruction_monolith()
            world_border()
            camera()

            #Элементы на экране
            world_surface.blit(world, (0, 0))
            for enemy in enemies:
                world_surface.blit(enemy.image, enemy.image_rect)
            for arrow in arrows:
                arrow.draw(world_surface)
            world_surface.blit(player, player_visual_rect)

            #Камера
            screen.blit(world_surface, (0, 0), (camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))

            #Вызов частиц
            for p in particles:
                p.draw(screen, camera_x, camera_y)

            #Вызов строительства
            draw_build_mode()
            draw_build_mode_hint(screen)

            #Подсветка клетки под курсором
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            hovered_cell_x = world_mouse_x // CELL_SIZE
            hovered_cell_y = world_mouse_y // CELL_SIZE

            sx = hovered_cell_x * CELL_SIZE - camera_x
            sy = hovered_cell_y * CELL_SIZE - camera_y

            if (hovered_cell_x, hovered_cell_y) in get_attack_cells(player_rect):
                sx = hovered_cell_x * CELL_SIZE - camera_x
                sy = hovered_cell_y * CELL_SIZE - camera_y
                pygame.draw.rect(screen, (150, 100, 110), (sx, sy, CELL_SIZE, CELL_SIZE), 2)

            #Отрисовка хитбоксов
            if debug_hitboxes:
                draw_debug_hitboxes(screen, camera_x, camera_y)

        else:

            #Вызовы функций при смерти
            for enemy in enemies:
                enemy.move_to_target(enemies, player_rect)

            # Обновление арбалетов
            for building in buildings:
                if isinstance(building, XBow):
                    building.update()

            # Обновление стрел
            for arrow in arrows[:]:
                arrow.update()
                if not arrow.alive:
                    arrows.remove(arrow)
            update_wave_system()
            destruction_monolith()

            #Камера
            screen.blit(world_surface, (0, 0), (camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #Элементы на экране при смерти
            world_surface.blit(world, (0, 0))
            for enemy in enemies:
                world_surface.blit(enemy.image, enemy.image_rect)
            for arrow in arrows:
                arrow.draw(world_surface)
            screen.blit(dark_overlay, (0, 0))

            #Возрождение
            current_time = pygame.time.get_ticks()
            if current_time - player_death_time >= RESPAWN_DELAY:
                respawn_player()

        #Отрисовка интерфейса
        draw_resource_counter(screen)
        draw_tool_slot(screen)
        draw_weapon_slot(screen)
        draw_wave_info(screen)
        draw_player_health_bar(screen, player_visual_rect, camera_x, camera_y)
        draw_monolith_world_health_bar(screen)
        if player_dead:
            draw_dead_screen(player_death_time)
        for enemy in enemies:
            enemy.draw_health_bar(screen, camera_x, camera_y)
        for building in buildings:
            building.draw_health_bar(screen, camera_x, camera_y)
        if build_message and pygame.time.get_ticks() < build_message_until:
            now = pygame.time.get_ticks()
            total = TEXT_LIVE_TIME
            remain = max(0, build_message_until - now)
            alpha = int(255 * remain / total)
            alpha = max(0, min(255, alpha))

            msg_surf = font.render(build_message, True, (255, 255, 255))
            msg_surf.set_alpha(alpha)

            px = player_visual_rect.centerx - camera_x
            py = player_visual_rect.top - 50 - camera_y
            screen.blit(msg_surf, msg_surf.get_rect(center=(px, py)))

    if build_menu_open:
        draw_build_menu()
    elif crafting_open:
        draw_crafting_menu()
    elif paused:
        if help_open:
            draw_help_board()
        else:
            draw_pause_menu()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()