import sys
from time import sleep
import pygame as pg
from settings import Settings
from game_stat import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    def __init__(self):
        pg.init()
        self.settings = Settings()
        self.screen = pg.display.set_mode((0,0),pg.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pg.display.set_caption("AlienInvasion")
        self.ship = Ship(self)
        self.bullets = pg.sprite.Group()
        self.aliens = pg.sprite.Group()
        self._create_fleet()
        self.bg_image = pg.image.load('imgs/fon.jpg')
        self.shoot_sound = pg.mixer.Sound('sounds/shot.wav')
        self.shoot_sound.set_volume(0.5)
        self.boom_sound = pg.mixer.Sound('sounds/boom.wav')
        self.boom_sound.set_volume(0.5)
        self.fon_sound = pg.mixer.Sound('sounds/fon.wav')
        self.fon_sound.set_volume(0.5)
        self.stats = GameStats(self)
        self.play_button = Button(self, 'Начать игру!')
        self.cur_img = pg.image.load("imgs/cursor.png")
        self.cursor = pg.transform.scale(self.cur_img, (self.cur_img.get_rect().width//10, self.cur_img.get_rect().height//10))
        self.cursor_rect = self.cursor.get_rect()
        self.x = self.y = 0
        self.sb = Scoreboard(self)
        pg.mouse.set_visible(False)
    def _ship_hit(self):
        self.aliens.empty()
        self.bullets.empty()
        self._create_fleet()
        self.ship.center_ship()
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
        else:
            self.stats.game_active = False
            self.fon_sound.stop()
            self.stats.reset_stats()


    def _create_fleet(self):
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        ship_height = self.ship.rect.height
        available_spase_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_spase_x // (2 * alien_width)
        available_space_y = self.settings.screen_height - 3 * alien_height - ship_height
        number_rows = available_space_y // (2 * alien_height)
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.y = alien_height + 2 * alien_height * row_number
        alien.rect.x = alien.x
        alien.rect.y = alien.y
        self.aliens.add(alien)

    def _change_fleet_direction(self):
        for aline in self.aliens:
            aline.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _fire_bullet(self):
        new_bullet = Bullet(self)
        self.bullets.add(new_bullet)
    def _check_key_down_events(self, event):
        """Обработка нажатия клавиши"""
        if event.key == pg.K_q:
            sys.exit()
        if event.key == pg.K_SPACE:
            if len(self.bullets) < 3:
                self.shoot_sound.play()
                self._fire_bullet()

        if event.key == pg.K_LEFT:
            self.ship.moving_left = True
        if event.key == pg.K_RIGHT:
            self.ship.moving_right = True

    def _check_key_up_events(self, event):
        """Обработка отжатия клавиши"""
        if event.key == pg.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pg.K_LEFT:
            self.ship.moving_left = False

    def _check_evens(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                self._check_key_down_events(event)

            if event.type == pg.KEYUP:
                self._check_key_up_events(event)

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self._check_play_button(mouse_pos)

            if event.type == pg.MOUSEMOTION:
                mouse_pos = pg.mouse.get_pos()
                self.x, self.y = mouse_pos

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.stats.game_active = True
            self.fon_sound.play(loops=-1)
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(self.bg_image, (0,0,self.screen.get_width(), self.screen.get_height()))
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        if not self.stats.game_active:
            self.play_button.draw_button()
        if not self.stats.game_active:
            self.screen.blit(self.cursor, (self.x, self.y))
        self.sb.show_score()
        pg.display.flip()

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        collisions = pg.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            self.boom_sound.play()
            for aliens in collisions.values():
                self.stats.score += len(aliens)
            self.sb.prep_score()
            if not self.aliens:
                self.stats.level += 1
                self.sb.prep_level()

                self.bullets.empty()
                self._create_fleet()
                self.settings.increase_speed()
            self.sb.check_high_score()


    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pg.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()


    def run_game(self):
        while True:
            self._check_evens()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()



app = AlienInvasion()
app.run_game()