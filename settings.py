class Settings():
    def initialize_dynamic_settings(self):
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0
        self.fleet_direction = 1


    def __init__(self):
        self.screen_width = 1000
        self.screen_height = 600
        self.bg_color = (255, 233, 111)
        self.bullet_width = 15
        self.bullet_height = 15
        self.bullet_color = (255, 0, 0)
        self.bullets_allowerd = 3
        self.fleet_drop_speed = 40
        self.ship_limit = 3
        self.speed_scale = 1.1
        self.initialize_dynamic_settings()


    def increase_speed(self):
        self.ship_speed = self.ship_speed * self.speed_scale
        self.bullet_speed = self.bullet_speed * self.speed_scale
        self.alien_speed = self.alien_speed * self.speed_scale