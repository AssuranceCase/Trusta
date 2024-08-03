import pygame
import math
import time
from z3 import *

WIDTH = 1200 # 地图宽度
HEIGHT = 800 # 地图高度
WINDOW_SIZE = (WIDTH, HEIGHT)

RADIUS = 10 # 物体半径
V_MAX = 1 * RADIUS # 最大移动速度每帧 V_MAX像素
A_LEN = 1 # 加速度大小为 A_LEN 像素/帧
A_MAX = 2 * A_LEN # 物体最大加速度
T_UNIT = 1 # 帧

MIN_DIST = RADIUS*2 # 物体间最小距离
MAX_DIST = RADIUS*15 # 物体间最大距离

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
    
    def move_obj(self, ax, ay, t):
        self.x, self.y, self.vx, self.vy = self._motion(self.x, self.y, self.vx, self.vy, ax, ay, t)
        self.ax = ax
        self.ay = ay

    def distance(self, obj):
        return math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)
    
    def _motion(self, x0, y0, vx0, vy0, ax, ay, t):
        x = x0 + vx0 * t + 0.5 * ax * t**2
        y = y0 + vy0 * t + 0.5 * ay * t**2
        vx = vx0 + ax * t
        vy = vy0 + ay * t

        # if vx > V_MAX:
        #     vx = V_MAX
        # if vx < -V_MAX:
        #     vx = -V_MAX
        # if vy > V_MAX:
        #     vy = V_MAX
        # if vy < -V_MAX:
        #     vy = -V_MAX
        return (int(x), int(y), round(vx, 4), round(vy, 4)) # 速度保留4位小数


class Square(Base):
    def __init__(self, x, y, size):
        super().__init__(x, y)
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x-self.size/2, self.y-self.size/2, self.size, self.size))
        # 插入一个图片
        # image = pygame.image.load('./plane1.png')
        # d_size = self.size*1.5
        # image = pygame.transform.scale(image, (d_size, d_size))
        # surface.blit(image, (self.x-d_size/2, self.y-d_size/2))

        pygame.draw.circle(surface, RED, (self.x, self.y), MAX_DIST, 1)
        pygame.draw.circle(surface, RED, (self.x, self.y), MIN_DIST, 1)


    def __str__(self):        
        return '红方：x={}, y={}, vx={}, vy={}'.format(self.x, self.y, self.vx, self.vy)

class Circle(Base):
    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius

    def draw(self, surface):
        pygame.draw.circle(surface, BLUE, (self.x, self.y), self.radius)
        # pygame.draw.circle(surface, BLUE, (self.x, self.y), MAX_DIST, 1)
        # pygame.draw.circle(surface, BLUE, (self.x, self.y), MIN_DIST, 1)

    def __str__(self):        
        return '蓝圆：x={}, y={}, vx={}, vy={}'.format(self.x, self.y, self.vx, self.vy)
        
class Hexagon(Base):
    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius

    def draw(self, surface):
        # 画一个六边形
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.pi / 180 * angle_deg
            x = self.x + self.radius * math.cos(angle_rad)
            y = self.y + self.radius * math.sin(angle_rad)
            points.append((x, y))
        pygame.draw.polygon(surface, BLACK, points)

    def __str__(self):        
        return '黑六边形位置：x={}, y={}, r={}'.format(self.x, self.y, self.radius)

'''
初始化物体
'''
def init():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    NUM_CIRCLES = 3
    square = Square(int(WIDTH/4), int(HEIGHT/2), RADIUS * 2)

    circles = []
    ORBIT_RADIUS = square.size + RADIUS*4
    ANGLE_INCREMENT = 2 * math.pi / NUM_CIRCLES
    for i in range(NUM_CIRCLES):
        angle = i * ANGLE_INCREMENT
        x = square.x + ORBIT_RADIUS * math.cos(angle)
        y = square.y + ORBIT_RADIUS * math.sin(angle)

        circle = Circle(x, y, RADIUS)
        circles.append(circle)

    hexagons = []
    hexagons.append(Hexagon(int(WIDTH/2), int(HEIGHT/3), RADIUS * 3))
    hexagons.append(Hexagon(int(WIDTH/2), int(HEIGHT/3*2), RADIUS * 2))

    return pygame, screen, square, circles, hexagons

def draw_all(pygame, screen, square, circles, hexagons):
    screen.fill((255, 255, 255))
    square.draw(screen)
    for circle in circles:
        circle.draw(screen)
    for hexagon in hexagons:
        hexagon.draw(screen)
    pygame.display.update()

'''逻辑操作函数'''
def dist_greater(x1, y1, x2, y2, min_dist):
    return ((x1 - x2)**2 + (y1 - y2)**2) > min_dist**2
def dist_less(x1, y1, x2, y2, max_dist):
    return ((x1 - x2)**2 + (y1 - y2)**2) < max_dist**2

def abs_greater(A, B): # 绝对值大小比较
    return A**2 >= B**2
def abs_less(A, B): # 绝对值大小比较
    return A**2 <= B**2
    
def xor(A, B): # 异或
    return Or(And(A, Not(B)), And(Not(A), B))
def same_sign(n1, n2): # 同正同负
    return Not(xor(n1 > 0, n2 > 0))
def if_else(cond, t_exe, f_exe):
    return Or(And(cond, t_exe),  And(Not(cond), f_exe))
def same_direction(sx, sy, cx, cy, cax, cay): # ca 指向 c->s 的方向
    dx = cx - sx
    dy = cy - sy
    return (dy/dx - cay/cax) ** 2 < 0.1

class AcceleratedSpeedSolve:
    def solve_circles(self, square, circles, hexagons):
        # Create Z3 variables for ax and ay
        sx, sy, svx, svy, sax, say, t, min_dist, max_dist = Reals('sx sy svx svy sax say t min_dist max_dist')
        c1x0, c1y0, c1vx0, c1vy0 = Reals('c1x0 c1y0 c1vx0 c1vy0')
        c2x0, c2y0, c2vx0, c2vy0 = Reals('c2x0 c2y0 c2vx0 c2vy0')
        c3x0, c3y0, c3vx0, c3vy0 = Reals('c3x0 c3y0 c3vx0 c3vy0')
        c1x, c1y, c1ax, c1ay, c1vx, c1vy = Reals('c1x c1y c1ax c1ay c1vx c1vy')
        c2x, c2y, c2ax, c2ay, c2vx, c2vy = Reals('c2x c2y c2ax c2ay c2vx c2vy')
        c3x, c3y, c3ax, c3ay, c3vx, c3vy = Reals('c3x c3y c3ax c3ay c3vx c3vy')

        h1x, h1y, h1r = Reals('h1x h1y h1r')
        h2x, h2y, h2r = Reals('h2x h2y h2r')


        # Create Z3 solver
        s = Solver()

        # 初始化-固定运算
        s.add(sx == square.x)
        s.add(sy == square.y)
        s.add(svx == square.vx)
        s.add(svy == square.vy)
        s.add(sax == square.ax)
        s.add(say == square.ay)
        s.add(t == 1)
        s.add(min_dist == MIN_DIST) # 最小距离
        s.add(max_dist == MAX_DIST) # 最大距离

        s.add(c1x0 == circles[0].x)
        s.add(c1y0 == circles[0].y)
        s.add(c1vx0 == circles[0].vx)
        s.add(c1vy0 == circles[0].vy)

        s.add(c2x0 == circles[1].x)
        s.add(c2y0 == circles[1].y)
        s.add(c2vx0 == circles[1].vx)
        s.add(c2vy0 == circles[1].vy)

        s.add(c3x0 == circles[2].x)
        s.add(c3y0 == circles[2].y)
        s.add(c3vx0 == circles[2].vx)
        s.add(c3vy0 == circles[2].vy)

        s.add(h1x == hexagons[0].x)
        s.add(h1y == hexagons[0].y)
        s.add(h1r == hexagons[0].radius)
        s.add(h2x == hexagons[1].x)
        s.add(h2y == hexagons[1].y)
        s.add(h2r == hexagons[1].radius)

        # c1
        s.add(c1x == c1x0 + c1vx0 * t + 0.5 * c1ax * t**2)
        s.add(c1y == c1y0 + c1vy0 * t + 0.5 * c1ay * t**2)
        s.add(c1vx == c1vx0 + c1ax * t)
        s.add(c1vy == c1vy0 + c1ay * t)

        # c2
        s.add(c2x == c2x0 + c2vx0 * t + 0.5 * c2ax * t**2)
        s.add(c2y == c2y0 + c2vy0 * t + 0.5 * c2ay * t**2)
        s.add(c2vx == c2vx0 + c2ax * t)
        s.add(c2vy == c2vy0 + c2ay * t)

        # c3
        s.add(c3x == c3x0 + c3vx0 * t + 0.5 * c3ax * t**2)
        s.add(c3y == c3y0 + c3vy0 * t + 0.5 * c3ay * t**2)
        s.add(c3vx == c3vx0 + c3ax * t)
        s.add(c3vy == c3vy0 + c3ay * t)

        # 不跑出范围、距离一定
        s.add(sx > 0, sy > 0, sx < WIDTH, sy < HEIGHT)
        s.add(c1x > 0, c1y > 0, c1x < WIDTH, c1y < HEIGHT)
        s.add(c2x > 0, c2y > 0, c2x < WIDTH, c2y < HEIGHT)
        s.add(c3x > 0, c3y > 0, c3x < WIDTH, c3y < HEIGHT)

        # s-dist
        s.add(((sx - c1x)**2 + (sy - c1y)**2) > min_dist**2)
        s.add(((sx - c1x)**2 + (sy - c1y)**2) < max_dist**2)
        
        s.add(((sx - c2x)**2 + (sy - c2y)**2) > min_dist**2)
        s.add(((sx - c2x)**2 + (sy - c2y)**2) < max_dist**2)
        
        s.add(((sx - c3x)**2 + (sy - c3y)**2) > min_dist**2)
        s.add(((sx - c3x)**2 + (sy - c3y)**2) < max_dist**2)

        # c*-dist
        s.add(((c2x - c3x)**2 + (c2y - c3y)**2) > min_dist**2)
        # s.add(((c2x - c3x)**2 + (c2y - c3y)**2) < max_dist**2)
        
        s.add(((c1x - c2x)**2 + (c1y - c2y)**2) > min_dist**2)
        # s.add(((c1x - c2x)**2 + (c1y - c2y)**2) < max_dist**2)
        
        s.add(((c1x - c3x)**2 + (c1y - c3y)**2) > min_dist**2)
        # s.add(((c1x - c3x)**2 + (c1y - c3y)**2) < max_dist**2)

        # 与障碍物保持距离
        s.add(dist_greater(sx, sy, h1x, h1y, h1r))
        s.add(dist_greater(sx, sy, h2x, h2y, h2r))

        s.add(dist_greater(c1x, c1y, h1x, h1y, h1r))
        s.add(dist_greater(c1x, c1y, h2x, h2y, h2r))
        s.add(dist_greater(c2x, c2y, h1x, h1y, h1r))
        s.add(dist_greater(c2x, c2y, h2x, h2y, h2r))
        s.add(dist_greater(c3x, c3y, h1x, h1y, h1r))
        s.add(dist_greater(c3x, c3y, h2x, h2y, h2r))



        # 物体性能
        # 速度
        s.add(-V_MAX < c1vx, c1vx < V_MAX)
        s.add(-V_MAX < c2vx, c2vx < V_MAX)
        s.add(-V_MAX < c3vx, c3vx < V_MAX)
        
        s.add(-V_MAX < c1vy, c1vy < V_MAX)
        s.add(-V_MAX < c2vy, c2vy < V_MAX)
        s.add(-V_MAX < c3vy, c3vy < V_MAX)

        # 加速度
        s.add(-A_MAX < c1ax, c1ax < A_MAX)
        s.add(-A_MAX < c2ax, c2ax < A_MAX)
        s.add(-A_MAX < c3ax, c3ax < A_MAX)

        s.add(-A_MAX < c1ay, c1ay < A_MAX)
        s.add(-A_MAX < c2ay, c2ay < A_MAX)
        s.add(-A_MAX < c3ay, c3ay < A_MAX)

        # 速度方向一致
        s.add(if_else(dist_greater(sx, sy, c1x, c1y, max_dist/3*2), \
                And(abs_greater(sax, c1ax), abs_greater(say, c1ay)), \
                if_else(dist_less(sx, sy, c1x, c1y, max_dist/3), \
                    And(abs_less(sax, c1ax), abs_less(say, c1ay)), \
                    True) \
              ))
        s.add(if_else(dist_greater(sx, sy, c2x, c2y, max_dist/3*2), \
                And(abs_greater(sax, c2ax), abs_greater(say, c2ay)), \
                if_else(dist_less(sx, sy, c2x, c2y, max_dist/3), \
                    And(abs_less(sax, c2ax), abs_less(say, c2ay)), \
                    True) \
              ))
        s.add(if_else(dist_greater(sx, sy, c3x, c3y, max_dist/3*2), \
                And(abs_greater(sax, c3ax), abs_greater(say, c3ay)), \
                if_else(dist_less(sx, sy, c3x, c3y, max_dist/3), \
                    And(abs_less(sax, c3ax), abs_less(say, c3ay)), \
                    True) \
              ))
        
        s.add(Not(xor(sax == 0, c1ax == 0)), Not(xor(say == 0, c1ay == 0)))
        s.add(Not(xor(sax == 0, c2ax == 0)), Not(xor(say == 0, c2ay == 0)))
        s.add(Not(xor(sax == 0, c3ax == 0)), Not(xor(say == 0, c3ay == 0)))

        s.add(Not(xor(sax > 0, c1ax > 0)), Not(xor(say > 0, c1ay > 0)))
        s.add(Not(xor(sax > 0, c2ax > 0)), Not(xor(say > 0, c2ay > 0)))
        s.add(Not(xor(sax > 0, c3ax > 0)), Not(xor(say > 0, c3ay > 0)))

        # Check if there is a solution
        set_option(rational_to_decimal=True)
        if s.check() == sat:
            # Get the solution
            m = s.model()
            # for d in m.decls():
            #     print("%s = %s" % (d.name(), m[d]))

            list_a = [[m[c1ax], m[c1ay]], [m[c2ax], m[c2ay]], [m[c3ax], m[c3ay]]]
            for pair in list_a:
                pair[0] = round(float(pair[0].as_fraction()), 4) # 保留4位小数
                pair[1] = round(float(pair[1].as_fraction()), 4)
            return list_a

        else:
            print('无解')
            return None

def move_circles(square, circles, hexagons):
    acc_solve = AcceleratedSpeedSolve()
    a_circles = acc_solve.solve_circles(square, circles, hexagons)
    if a_circles == None:
        return False
    
    print('蓝圆加速度：', a_circles)
    for circle, acc in zip(circles, a_circles):
        circle.move_obj(ax=acc[0], ay=acc[1], t=T_UNIT)
        print(circle)
    return True


def main():

    pygame, screen, square, circles, hexagons = init()

    while True:
        time.sleep(0.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        m_ok = True
        if keys[pygame.K_LEFT]:
            square.move_obj(ax=-A_LEN, ay=0, t=T_UNIT)
            print(square)
            m_ok = move_circles(square, circles, hexagons)
        if keys[pygame.K_RIGHT]:
            square.move_obj(ax=A_LEN, ay=0, t=T_UNIT)
            print(square)
            m_ok = move_circles(square, circles, hexagons)
        if keys[pygame.K_UP]:
            square.move_obj(ax=0, ay=-A_LEN, t=T_UNIT)
            print(square)
            m_ok = move_circles(square, circles, hexagons)
        if keys[pygame.K_DOWN]:
            square.move_obj(ax=0, ay=A_LEN, t=T_UNIT)
            print(square)
            m_ok = move_circles(square, circles, hexagons)
        if keys[pygame.K_SPACE]:
            square.move_obj(ax=0, ay=0, t=T_UNIT)
            print(square)
            m_ok = move_circles(square, circles, hexagons)
        
        if not m_ok:
            time.sleep(5)
            pygame, screen, square, circles, hexagons = init()

        draw_all(pygame, screen, square, circles, hexagons)


if __name__ == '__main__':
    main()

