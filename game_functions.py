import sys
from time import sleep
import pygame
from bullet import Bullet
from alien import Alien


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    # Responde a pressionamentos de tecla.
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullets(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def fire_bullets(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        # Cria um novo projétil e adiciona ao grupo de projéteis
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    # Atualiza a posição dos projéteis
    bullets.update()
    # Livra- se dos projéteis que desapareceram
    for bullet in bullets.copy():
        if bullet.rect.bottom <=0:
            bullets.remove(bullet)

    check_bullets_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_bullets_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    # Remove os projéteis e aliens que colidam
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
            check_high_score(stats, sb)

    if len(aliens) == 0:
        # Novo nível por frota destruída
        stats.level += 1
        sb.prep_level()
        # Destrói projéteis existentes, aumenta a velocidade do game e cria uma nova frota
        ai_settings.increase_speed()
        bullets.empty()
        create_fleet(ai_settings, screen, ship, aliens)


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Responde quando um alien atingir a espaçonave"""
    if stats.ships_left > 0:
        stats.ships_left -= 1
        # Resposta para quando a nave for atingida
        # Perde uma "vida"

        # Atualiza  o painel de pontuações
        sb.prep_ships()

        # Esvazia a lista de aliens e de projéteis
        aliens.empty()
        bullets.empty()

        # Cria uma nova frota e centraliza a nave
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
        # Então temos uma pausa
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    # Responde a eventos de pressionamento de teclas e de mouse
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:

        # Reinicia as configurações do jogo
        ai_settings.initialize_dynamic_settings()

        # Oculta o cursor do mouse
        pygame.mouse.set_visible(False)
        stats.reset_stats()
        stats.game_active = True

        # Limpamos e reposicionamos os objetos do jogo
        aliens.empty()
        bullets.empty()

        # Reinicia as imagens do painel de pontuação
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

def check_high_score(stats, sb):
    # Verifica se há uma nova pontuação máxima
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    # Redesenha a tela a cada passagem pelo laço
    screen.fill(ai_settings.bg_color)

    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()

    aliens.draw(screen)

    # Desenha a informação sobre pontuação
    sb.show_score()

    # Desenha o botão play, se o jogo estiver inativo
    if not stats.game_active:
        play_button.draw_button()

    # Deixa a tela mais recente visível
    pygame.display.flip()


def check_fleet_edges(ai_settings, aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def get_number_rows(ai_settings, ship_height, alien_height):
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def get_number_aliens_x(ai_settings, alien_width):
    # Determina o numero de aliens por linha (que cabem)
    avaible_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(avaible_space_x / (2 * alien_width))
    return number_aliens_x


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    # Cria um alien e o posiciona na linha
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * (alien_width * alien_number)
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    alien = Alien(ai_settings, screen)
    # O livro estava com problema de impressão nessa parte, mas  resultado ficou igual
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.x)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    for row_number in range(number_rows):
        # Cria a primeira linha de aliens
        for alien_number in range(number_aliens_x):
            # Cria um alien e o posiciona na linha
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

            # O livro estava com problema de impressão nessa parte, mas  resultado ficou igual


def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets):
    # Verifica se algum alien chegou ao canto inferior da tela
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # É tratado da mesma forma se atingir a nave
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
            break


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    # Verifica se houve colisões entre alienígenas e aespaçonave
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)

    # Verifica a colisão do alien com a parte inferior da tela
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)
