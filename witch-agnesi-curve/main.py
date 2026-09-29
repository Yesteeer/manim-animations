from manim import *

config.disable_caching = True

class WitchAgnesiCurve(Scene):

    def construct(self):
        self.show_circle()
        self.show_origin()
        self.show_axis()
        self.move_dot()
     
    def show_circle(self):
        self.radius = 1

        self.origin = np.array([0, 0, 0])
        self.center = self.origin + np.array([0, self.radius, 0])

        circle = Circle(radius=self.radius, color=WHITE)
        circle.move_to(self.center)

        self.add(circle)
        self.circle = circle

    def show_origin(self):
        origin = Dot(self.origin, color=WHITE)

        self.add(origin)

    def show_axis(self):
        dx = 10
        origin = self.origin
        radius = self.radius

        start = origin + np.array([-dx, 2*radius, 0])
        end = origin + np.array([dx, 2*radius, 0])

        self.horizontal_line = [start, end]

        self.add(Line(*self.horizontal_line))

    def move_dot(self):
        orbit = self.circle
        origin = self.origin

        dot = Dot(color=YELLOW)
        dot.move_to(orbit.point_from_proportion(0.76))
        self.t_offset = 0.76
        rate = 1 / 8

        def go_around_circle(mob, dt):
            self.t_offset += dt * rate

            mob.move_to(orbit.point_from_proportion(self.t_offset % 1))

        def get_secant_line():
            secant_line = [origin, dot.get_center()]
            if cross2d(Line(*secant_line).get_unit_vector(), Line(*self.horizontal_line).get_unit_vector()) == 0:
                self.intersection_point = np.array(self.origin)
            else :
                intersection_point = line_intersection(secant_line, self.horizontal_line)
                self.intersection_point = np.array(intersection_point)

            return Line(self.origin, self.intersection_point, color=YELLOW)
        
        def get_new_curve_point():
            get_secant_line()
            third_point = self.intersection_point + np.array([0, -1, 0])
            triangle_vertical_side = Line(self.intersection_point, third_point)
            curve_point = triangle_vertical_side.get_projection(dot.get_center())

            self.curve_point = curve_point

            return Dot(curve_point, color=RED)

        def get_triangle():
            vertical_side =  Line(self.intersection_point, self.curve_point, color=BLUE)
            horizontal_side = Line(dot.get_center(), self.curve_point, color=BLUE)

            return VGroup(vertical_side, horizontal_side)

        get_new_curve_point()
            
        self.curve_start = self.curve_point
        self.curve = VGroup()
        self.curve.add(Line(self.curve_start, self.curve_start))

        def get_curve():
            last_segment = self.curve[-1]
            new_segment = Line(last_segment.get_end(), self.curve_point, color=RED)
            self.curve.add(new_segment)

            return self.curve


        dot.add_updater(go_around_circle)

        secant_line = always_redraw(get_secant_line)
        curve_point = always_redraw(get_new_curve_point)
        triangle = always_redraw(get_triangle)
        curve = always_redraw(get_curve)


        self.add(dot)
        self.add(secant_line, curve_point, triangle, curve)
        self.wait(7.95)

        dot.remove_updater(go_around_circle)

