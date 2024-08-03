'''
用pygame创建一个小车刹车撞到障碍物的动画

'''

import pygame
import sys, os
os.chdir(os.path.dirname(__file__))

class CarCrashGame:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Car Crash Animation')
        self.running = True

        self.car_image = pygame.image.load('car.png')
        self.car_image = pygame.transform.scale(self.car_image, (50, 50))
        self.obstacle_image = pygame.image.load('car.png')
        self.obstacle_image = pygame.transform.scale(self.obstacle_image, (50, 50))
        self.cargo_image = pygame.image.load('box.png')  # 请替换为你自己的货物图片
        self.cargo_image = pygame.transform.scale(self.cargo_image, (30, 30))  # 调整货物大小

        # 屏幕宽8米，设置初始小车位置
        self.car_x = self.m2pix(1) # 距离左侧1米的位置
        self.car_y = self.screen_height // 2
        self.obstacle_x = self.car_x + self.m2pix(5) # 距离小车右侧5米的位置
        self.obstacle_y = self.screen_height // 2
        self.cargo_x = self.car_x + self.car_image.get_width() // 2 - self.cargo_image.get_width() // 2
        self.cargo_y = self.car_y - self.cargo_image.get_height()

        # 货物运动
        self.cargo_vx = False # False 代表跟随car，否则已脱离
        self.cargo_vy = False
        self.cargo_ax = False
        self.cargo_ay = 9.8  # 重力加速度
        self.cargo_on_ground = False
        self.cargo_drop_out = False
        self.cargo_first_drop = False

        # 字体显示
        self.font = pygame.font.Font(None, 30)  # 创建字体对象，参数：字体文件路径, 字体大小

        # 图表显示
        self.speed_history = []
        self.max_history_length = 100
        self.font = pygame.font.Font(None, 30)
        self.axis_font = pygame.font.Font(None, 15)

        # 地面标记
        self.ground_font = pygame.font.Font(None, 15)


        # 基础参数
        self.speed = 1  # 小车 初始速度1米每秒
        self.acceleration = 0.017 # 加速度 0.18米每两次方秒
        self.obstacle_detection_distance = 3 # 障碍物检测距离 3米
        self.braking = False # 是否开始制动
        self.braking_reaction_time = 0.1 # 制动反应时间 0.1秒


    def pix2m(self, pix):
        return pix / 100 # 100像素对应1米
    def m2pix(self, pix):
        return pix * 100 # 100像素对应1米
    def unit_t(self): 
        return 0.1 # 一次循环消耗时间0.1秒

    def run(self):
        while self.running:
            self.screen.fill((255, 255, 255))
            self.move_car()
            self.move_cargo()
            self.update()
            self.draw_images()
            pygame.display.update()
            self.handle_events()
            pygame.time.delay(int(1000*self.unit_t())) # 100毫秒1帧

        pygame.quit()
        sys.exit()

    def need_cargo_drop_out(self):
        print('是否掉落判断')
        return False

    def move_cargo(self):
        dt = self.unit_t()
        # 第一次制动的时候计算
        if self.cargo_first_drop == False and self.braking:
            self.cargo_first_drop = True # 当前if只执行一次
            self.cargo_vx = self.speed
            self.cargo_vy = 0
            self.cargo_x = self.car_x + self.car_image.get_width()
            self.cargo_drop_out = self.need_cargo_drop_out() # 经过判断，要掉落

        # 箱子掉落
        if self.cargo_drop_out:
            if not self.cargo_on_ground: # 未掉落地面
                self.cargo_vy += self.cargo_ay * dt
                self.cargo_x += self.m2pix(self.cargo_vx * dt)
                self.cargo_y += self.m2pix(self.cargo_vy * dt)

                # Check if cargo is on the ground
                if self.cargo_y >= self.car_y + self.car_image.get_height() - self.cargo_image.get_height():
                    self.cargo_y = self.car_y + self.car_image.get_height() - self.cargo_image.get_height()
                    self.cargo_on_ground = True

        else:
            # 货物同步移动
            self.cargo_x = self.car_x + self.car_image.get_width() // 2 - self.cargo_image.get_width() // 2

    def distance(self):
        return self.pix2m(self.obstacle_x - self.car_x - self.car_image.get_width())

    def is_collided(self):
        return self.distance() <= 0.02 # 0.02米代表碰撞
    
    def detect_collision_cargo(self): # 车和箱子碰撞
        car_rect = self.car_image.get_rect(topleft=(self.car_x, self.car_y))
        cargo_rect = self.cargo_image.get_rect(topleft=(self.cargo_x, self.cargo_y))
        if car_rect.colliderect(cargo_rect): # 矩形有重叠
            return True
        return False
    
    def move_car(self):
        if self.is_collided():
            self.speed = 0
        if self.distance() <= self.obstacle_detection_distance:
            self.braking = True
            self.braking_reaction_time -= self.unit_t()
        else:
            self.car_x += self.m2pix(self.speed * self.unit_t())
        
        if self.braking and self.braking_reaction_time <= 0:
            # 真正开始制动
            self.speed -= self.acceleration
            if self.speed < 0 or self.detect_collision_cargo():
                self.speed = 0
            self.car_x += self.m2pix(self.speed * self.unit_t())

    def update(self):
        if len(self.speed_history) == self.max_history_length:
            return
            
        self.speed_history.append(self.speed)
        if len(self.speed_history) > self.max_history_length:
            self.speed_history.pop(0)

    def draw_images(self):
        self.screen.blit(self.car_image, (self.car_x, self.car_y))
        self.screen.blit(self.cargo_image, (self.cargo_x, self.cargo_y))
        self.screen.blit(self.obstacle_image, (self.obstacle_x, self.obstacle_y))

        # 在左上角显示小车速度
        speed_text = f"Speed: {self.speed:.2f} m/s"
        speed_text_image = self.font.render(speed_text, True, (0, 0, 0))
        self.screen.blit(speed_text_image, (10, 10))  # 绘制速度文本，参数：文本图像, 位置
        # 右上角显示图表
        self.draw_speed_graph()
        # 画地面
        self.draw_ground_marks()
        # 画检测线
        if self.speed == 0:
            if self.is_collided() or self.detect_collision_cargo():
                self.draw_distance_lines('red')
            else:
                self.draw_distance_lines('green')

    def draw_speed_graph(self):
        graph_width = 200
        graph_height = 100
        graph_x = self.screen_width - graph_width - 10
        graph_y = 10

        # Draw graph background
        graph_background = pygame.Surface((graph_width, graph_height))
        graph_background.fill((255, 255, 255))
        graph_background.set_alpha(128)
        self.screen.blit(graph_background, (graph_x, graph_y))

        # Draw graph lines
        max_speed = max(self.speed_history)
        data_points = []
        for i, speed in enumerate(self.speed_history):
            x = graph_x + i * graph_width / self.max_history_length
            y = graph_y + graph_height - (speed / max_speed) * graph_height
            data_points.append((x, y))

        if len(data_points) > 2:
            # 画数据
            pygame.draw.lines(self.screen, (0, 0, 255), False, data_points, 2)

            # Draw coordinate axes
            pygame.draw.line(self.screen, (0, 0, 0), (graph_x, graph_y + graph_height), (graph_x, graph_y), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (graph_x, graph_y + graph_height), (graph_x + graph_width, graph_y + graph_height), 2)

            # Draw tick marks and labels
            num_ticks_y = 5
            for i in range(1, num_ticks_y + 1):
                tick_length = 5
                tick_y = graph_y + graph_height - (graph_height / num_ticks_y) * i
                pygame.draw.line(self.screen, (0, 0, 0), (graph_x - tick_length, tick_y), (graph_x, tick_y), 2)

                tick_label = f"{max_speed / num_ticks_y * i:.1f} m/s"
                tick_label_image = self.axis_font.render(tick_label, True, (0, 0, 0))
                label_width, label_height = self.axis_font.size(tick_label)
                self.screen.blit(tick_label_image, (graph_x - tick_length - label_width - 5, tick_y - label_height / 2))

            num_ticks_x = 4
            for i in range(1, num_ticks_x + 1):
                tick_length = 5
                tick_x = graph_x + (graph_width / num_ticks_x) * i
                pygame.draw.line(self.screen, (0, 0, 0), (tick_x, graph_y + graph_height), (tick_x, graph_y + graph_height + tick_length), 2)

                tick_label = f"{self.unit_t() * i * self.max_history_length / num_ticks_x:.0f} s"
                tick_label_image = self.axis_font.render(tick_label, True, (0, 0, 0))
                label_width, label_height = self.axis_font.size(tick_label)
                self.screen.blit(tick_label_image, (tick_x - label_width / 2, graph_y + graph_height + tick_length + 5))

    def draw_ground_marks(self):
        mark_width = 10
        mark_height = 2
        mark_spacing = 10
        num_marks = self.screen_width // (mark_width + mark_spacing)

        for i in range(num_marks):
            mark_x = i * (mark_width + mark_spacing)
            mark_y = self.car_y + self.car_image.get_height() + 5
            pygame.draw.rect(self.screen, (0, 0, 0), (mark_x, mark_y, mark_width, mark_height))

            mark_y = self.obstacle_y + self.obstacle_image.get_height() + 5
            pygame.draw.rect(self.screen, (0, 0, 0), (mark_x, mark_y, mark_width, mark_height))

            # Draw scale label for every 100 pixels
            if mark_x % 100 == 0:
                if mark_x != 0:
                    scale_label = f"{mark_x // 100}m"
                    scale_label_image = self.ground_font.render(scale_label, True, (0, 0, 0))
                    label_width, label_height = self.ground_font.size(scale_label)
                    self.screen.blit(scale_label_image, (mark_x - label_width / 2, mark_y + mark_height + 5))

    def draw_distance_lines(self, color='red'):
        if color == 'red':
            line_color = (255, 0, 0)
        else:
            line_color = (0, 255, 0)
        line_thickness = 2

        # Draw red line on the right side of the car
        car_right_x = self.car_x + self.car_image.get_width()
        pygame.draw.line(self.screen, line_color, (car_right_x, self.car_y), (car_right_x, self.car_y + self.car_image.get_height()), line_thickness)

        # Draw red line on the left side of the obstacle
        if color != 'red':
            obstacle_left_x = self.obstacle_x
            pygame.draw.line(self.screen, line_color, (obstacle_left_x, self.obstacle_y), (obstacle_left_x, self.obstacle_y + self.obstacle_image.get_height()), line_thickness)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.cargo_drop_out = True

if __name__ == '__main__':
    game = CarCrashGame()
    game.run()
