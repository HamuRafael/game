import pygame
import sys

# -----------------------
# CONFIGURAÇÕES INICIAIS
# -----------------------
WIDTH = 800
HEIGHT = 600
FPS = 60

PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_FORCE = 15

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

# Tamanho do sprite do inimigo
ENEMY_WIDTH  = 40
ENEMY_HEIGHT = 40

def load_image(path, w=None, h=None, alpha=True):
    """Carrega uma imagem com ou sem transparência."""
    try:
        img = pygame.image.load(path)  # Carrega a imagem
        if w and h:
            img = pygame.transform.scale(img, (w, h))  # Redimensiona
        if alpha:
            return img.convert_alpha()  # Mantém a transparência
        else:
            return img.convert()  # Sem transparência
    except:
        print(f"[Aviso] Não foi possível carregar '{path}'. Usando fallback.")
        surf = pygame.Surface((w or 50, h or 50), pygame.SRCALPHA)
        surf.fill((255, 0, 0, 120))
        return surf


# -----------------------
# CLASSES
# -----------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image, keys):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.keys = keys

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def handle_input(self):
        keys_pressed = pygame.key.get_pressed()
        self.vel_x = 0

        if keys_pressed[self.keys['left']]:
            self.vel_x = -PLAYER_SPEED
        if keys_pressed[self.keys['right']]:
            self.vel_x = PLAYER_SPEED

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_FORCE

    def update(self, platforms):
        # Gravidade
        self.vel_y += GRAVITY

        # Movimento horizontal
        self.rect.x += self.vel_x
        self.collide(self.vel_x, 0, platforms)

        # Movimento vertical
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide(0, self.vel_y, platforms)

        # Impedir de sair da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def collide(self, vel_x, vel_y, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                # Colisão horizontal
                if vel_x > 0:
                    self.rect.right = p.rect.left
                elif vel_x < 0:
                    self.rect.left = p.rect.right

                # Colisão vertical
                if vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image=None):
        super().__init__()
        if image:
            self.image = pygame.transform.scale(image, (w, h))
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill((150, 75, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        pass

class Enemy(pygame.sprite.Sprite):
    """
    Aqui só usamos movimento horizontal,
    com min_val e max_val como limites de X.
    """
    def __init__(self, x, y, image, min_val, max_val, speed):
        super().__init__()
        self.image = image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.min_val = min_val
        self.max_val = max_val
        self.speed   = speed

    def update(self, *args):
        self.rect.x += self.speed
        # Inverter direção se passou do limite
        if self.rect.x < self.min_val or self.rect.x > self.max_val:
            self.speed = -self.speed

class Olivia(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect  = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        pass

# -----------------------
# FASES (LEVEL DESIGN)
# -----------------------
def create_level_data(level):
    """
    Retorna (lista_plataformas, start_pos1, start_pos2, inimigos_data, olivia_data ou None)
    inimigos_data é uma lista de tuplas: (x, y, min_val, max_val, speed)
    """
    if level == 0:  # Fase de tutorial
        # Uma grande plataforma ocupando o "chão" (y=550, 800 de largura)
        level_platforms = [
            (0, 550, 800, 50),
        ]
        start_pos1 = (50, 450)
        start_pos2 = (120, 450)
        inimigos_data = [
            (700, 510, 700, 700, 0),
        ]
        olivia_data = None

    elif level == 1:
        level_platforms = [
            (0, 550, 800, 50),
        ]
        start_pos1 = (50, 450)
        start_pos2 = (120, 450)
        inimigos_data = [
            (300, 510, 50, 750, 2),
            (500, 510, 50, 750, 3),
        ]
        olivia_data = None

    elif level == 2:
        level_platforms = [
            (0, 550, 400, 50),
            (500, 450, 300, 50),
        ]
        start_pos1 = (50, 450)
        start_pos2 = (120, 450)
        inimigos_data = [
            (190, 510, 50, 360, 2),
            (600, 410, 500, 760, 3),
        ]
        olivia_data = None

    elif level == 3:
        level_platforms = [
            (0, 550, 200, 50),
            (300, 450, 200, 50),
            (600, 350, 200, 50),
        ]
        start_pos1 = (50, 450)
        start_pos2 = (100, 450)
        inimigos_data = [
            (190, 510, 0, 160, 1),
            (350, 410, 300, 460, 1),
            (650, 310, 600, 760, 1),
        ]
        olivia_data = None

    else:  # level == 4 (fase final)
        level_platforms = [
            (0, 550, 800, 50),
            (200, 450, 150, 50),
            (400, 350, 150, 50),
            (600, 250, 150, 50),
        ]
        start_pos1 = (50, 450)
        start_pos2 = (120, 450)
        inimigos_data = [
            (200, 510, 50, 760, 0),
            (230, 410, 200, 310, 0),
            (430, 310, 400, 510, 0),
            (630, 210, 600, 710, 0),
        ]
        olivia_data = (700, 150)

    return (level_platforms, start_pos1, start_pos2, inimigos_data, olivia_data)


# -----------------------
# LOOP PRINCIPAL (MAIN)
# -----------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Aventuras de Ana e Rafa (Horizontais + Mensagem Final 2 telas)")
    clock = pygame.time.Clock()

    # Carrega imagens
    game_over_bg = load_image("assets/game_over_bg.png", WIDTH, HEIGHT)
    bg_image = load_image("assets/background.png", WIDTH, HEIGHT)
    bg_menu = load_image("assets/menu_background.png", WIDTH, HEIGHT)
    p1_image     = load_image("assets/menino.png", 50, 50)
    p2_image     = load_image("assets/menina.png", 50, 50)
    enemy_image  = load_image("assets/weight.png", ENEMY_WIDTH, ENEMY_HEIGHT)
    ground_image = load_image("assets/ground.png", 50, 50, alpha=False)
    olivia_image = load_image("assets/olivia.png", 80, 120)
    bg_final1 = load_image("assets/final1.png", WIDTH, HEIGHT)
    bg_final2 = load_image("assets/final2.png", WIDTH, HEIGHT)

    # NOVO: background da história
    story_bg = load_image("assets/story_bg.png", WIDTH, HEIGHT)

    arrow_image  = load_image("assets/arrow.png", 60, 60)
    arrow_rect = pygame.Rect(WIDTH - 70, HEIGHT - 70, 60, 60)

    font_title = pygame.font.SysFont("Arial", 60, bold=True)
    font_menu  = pygame.font.SysFont("Arial", 50, bold=True)
    font_small = pygame.font.SysFont("Arial", 30)

    player1_keys = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}
    player2_keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}

    # Estados do jogo (ADICIONAMOS "STORY")
    game_state = "MENU"
    current_level = 0
    max_levels = 5

    menu_options = ["Iniciar", "Sair"]
    selected_option = 0

    p1_touched_olivia = False
    p2_touched_olivia = False
    olivia_sprite = None

    final_messages = [
        "Parabéns por salvar a Olivia! Vocês foram incríveis!",
        "Quer namorar comigo?"
    ]
    final_page = 0

    platforms = pygame.sprite.Group()
    enemies   = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    player1 = None
    player2 = None
    level_end_x = 750

    def start_level(level):
        nonlocal p1_touched_olivia, p2_touched_olivia, olivia_sprite
        p1_touched_olivia = False
        p2_touched_olivia = False
        olivia_sprite = None

        data = create_level_data(level)
        (plats_data, sp1, sp2, enem_data, oli_data) = data

        platforms.empty()
        enemies.empty()
        all_sprites.empty()

        for (px, py, w, h) in plats_data:
            pf = Platform(px, py, w, h, ground_image)
            platforms.add(pf)
            all_sprites.add(pf)

        for (ex, ey, minv, maxv, spd) in enem_data:
            e = Enemy(ex, ey, enemy_image, minv, maxv, spd)
            enemies.add(e)
            all_sprites.add(e)

        pl1 = Player(sp1[0], sp1[1], p1_image, player1_keys)
        pl2 = Player(sp2[0], sp2[1], p2_image, player2_keys)
        all_sprites.add(pl1, pl2)

        if oli_data is not None:
            ox, oy = oli_data
            oli = Olivia(ox, oy, olivia_image)
            all_sprites.add(oli)
            olivia_sprite = oli

        end_x = 750 if level < max_levels else 9999
        return pl1, pl2, end_x

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "MENU":
                screen.blit(bg_menu, (0, 0))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if selected_option == 0:  # Iniciar
                            # Agora, antes de jogar, vamos pra "STORY"
                            game_state = "STORY"
                        else:  # Sair
                            pygame.quit()
                            sys.exit()

            elif game_state == "STORY":
                # Se apertar ENTER, começamos a fase 0
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                        current_level = 0
                        player1, player2, level_end_x = start_level(current_level)
                        game_state = "PLAY"

            elif game_state == "PLAY":
                if event.type == pygame.KEYDOWN:
                    if event.key == player1.keys['jump']:
                        player1.jump()
                    if event.key == player2.keys['jump']:
                        player2.jump()

            elif game_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    current_level = 0
                    player1, player2, level_end_x = start_level(current_level)
                    game_state = "PLAY"

            elif game_state == "WIN":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if final_page < len(final_messages) - 1:
                        if arrow_rect.collidepoint(mx, my):
                            final_page += 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"
                        final_page = 0

        if game_state == "PLAY":
            player1.handle_input()
            player2.handle_input()

            all_sprites.update(platforms)
            enemies.update()

            if pygame.sprite.spritecollide(player1, enemies, False) or \
               pygame.sprite.spritecollide(player2, enemies, False):
                game_state = "GAME_OVER"

            if player1.rect.top > HEIGHT or player2.rect.top > HEIGHT:
                game_state = "GAME_OVER"

            if current_level < 4:
                if (player1.rect.x >= level_end_x) and (player2.rect.x >= level_end_x):
                    current_level += 1
                    player1, player2, level_end_x = start_level(current_level)
            else:
                if olivia_sprite:
                    if olivia_sprite.rect.colliderect(player1.rect):
                        p1_touched_olivia = True
                    if olivia_sprite.rect.colliderect(player2.rect):
                        p2_touched_olivia = True
                    if p1_touched_olivia and p2_touched_olivia:
                        game_state = "WIN"
                        final_page = 0

        # DESENHO
        if game_state == "MENU":
            screen.blit(bg_menu, (0,0))
            title_surf = font_title.render("", True, BLACK)
            title_rect = title_surf.get_rect(center=(WIDTH//2, 120))
            screen.blit(title_surf, title_rect)

            for i, opt in enumerate(menu_options):
                color = RED if i == selected_option else BLACK
                surf_opt = font_menu.render(opt, True, color)
                rect_opt = surf_opt.get_rect(center=(WIDTH//2, 300 + i*60))
                screen.blit(surf_opt, rect_opt)

        elif game_state == "STORY":
            # Exibe o background de história
            screen.blit(story_bg, (0,0))
            # Se quiser, desenhe algo como "Press ENTER to continue"
            press_surf = font_small.render("", True, RED)
            press_rect = press_surf.get_rect(center=(WIDTH//2, HEIGHT - 50))
            screen.blit(press_surf, press_rect)

        elif game_state == "PLAY":
            screen.blit(bg_image, (0, 0))
            all_sprites.draw(screen)
            enemies.draw(screen)

        elif game_state == "GAME_OVER":
            screen.blit(game_over_bg, (0, 0))
            font_small2 = pygame.font.SysFont("Arial", 30)
            msg = font_small2.render("", True, BLACK)
            rect_msg = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(msg, rect_msg)

        elif game_state == "WIN":
            if final_page == 0:
                screen.blit(bg_final1, (0, 0))
            else:
                screen.blit(bg_final2, (0, 0))
            if final_page < len(final_messages) - 1:
                screen.blit(arrow_image, arrow_rect)

        pygame.display.flip()

if __name__ == "__main__":
    main()
