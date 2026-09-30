from manim import *

config.disable_caching = True

class WitchAgnesiCurve(MovingCameraScene):

    def construct(self):
        self.default_color = '#613805'
        self.show_circle()
        self.show_origin()
        self.show_axis()
        self.move_dot()

     
    def show_circle(self):
        self.radius = 1

        self.origin = np.array([0, -1, 0])
        self.center = self.origin + np.array([0, self.radius, 0])

        circle = Circle(radius=self.radius, color= self.default_color)
        circle.move_to(self.center)

        self.add(circle)
        self.circle = circle

    def show_origin(self):
        origin = Dot(self.origin, color= self.default_color)

        self.add(origin)

    def show_axis(self):
        dx = 10
        origin = self.origin
        radius = self.radius

        start = origin + np.array([-dx, 2*radius, 0])
        end = origin + np.array([dx, 2*radius, 0])

        self.horizontal_line = [start, end]

        self.add(Line(*self.horizontal_line, color=self.default_color))

    def move_dot(self):
        orbit = self.circle
        origin = self.origin
        dot_color = '#fcb863' 
        curve_color = '#ff6464' 
        triangle_color = '#6f9cff' 

        alpha = ValueTracker(0)

        def get_dot():
            dot = []
            if alpha.get_value() < 0.75:
                dot = Dot(orbit.point_from_proportion(alpha.get_value()))
            elif alpha.get_value() == 0.75:
                dot = dot(orbit.point_from_proportion(0.74))
            elif alpha.get_value() <= 1.5:
                dot = Dot(orbit.point_from_proportion(1.5 - alpha.get_value()))
            elif 1.5 < alpha.get_value() < 1.75:
                dot = Dot(orbit.point_from_proportion( 15 / 6 - alpha.get_value()))
            else:
                dot = Dot(orbit.point_from_proportion(0.751)) 

            dot.set_color(dot_color)

            return dot

        def get_intersection_point():
            secant_line = [origin, get_dot().get_center()]
            if cross2d(Line(*secant_line).get_unit_vector(), Line(*self.horizontal_line).get_unit_vector()) == 0:
                return  np.array(self.origin)
            else :
                intersection_point = line_intersection(secant_line, self.horizontal_line)
                return np.array(intersection_point)

        def get_secant_line():
            return  Line(self.origin, get_intersection_point(), color=dot.color)

        def get_curve_point():
            third_point = get_intersection_point() + np.array([0, -1, 0])
            triangle_vertical_side = Line(get_intersection_point(), third_point)
            curve_point = triangle_vertical_side.get_projection(get_dot().get_center())

            return curve_point

        def get_curve_dot():
            return Dot(get_curve_point(), color=curve_color, radius=0.05)

        def get_triangle_sides():
            vertical_side =  Line(get_intersection_point(), get_curve_point(), color=triangle_color)
            horizontal_side = Line(get_dot(), get_curve_point(), color=triangle_color)

            return [vertical_side, horizontal_side]

        def get_triangle():
            return VGroup(*get_triangle_sides())

        def get_right_angle():
            return Angle(
                    *get_triangle_sides(), 
                    dot=True, 
                    radius=.3, 
                    quadrant=(-1, -1), 
                    color=triangle_color, 
                    dot_color=triangle_color,
                    other_angle=False
                    )


        self.curve_start = get_curve_point()
        self.curve = VGroup()
        self.curve.add(Line(self.curve_start, self.curve_start))

        def get_curve():
            last_segment = self.curve[-1]
            new_segment = Line(last_segment.get_end(), get_curve_point(), color=curve_color)
            self.curve.add(new_segment)

            return self.curve

        dot = always_redraw(get_dot)
        secant = always_redraw(get_secant_line)
        triangle = always_redraw(get_triangle)
        angle = get_right_angle()
        curve_point = always_redraw(get_curve_dot)
        curve = always_redraw(get_curve)

        construct = AnimationGroup(
            Create(secant),
            FadeIn(dot),
            Create(triangle),
            FadeIn(angle),
            run_time=8,
            lag_ratio=1.0
        )

        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.set(width=8))

        # initiate construction
        self.play(construct)

        # indication right angle and show relevant point
        self.play(Indicate(angle), color='#ff4be2')
        self.play(FadeOut(angle))
        self.play(FadeIn(curve_point))

        self.play(Restore(self.camera.frame))

        # add and show curve
        self.add(curve)
        self.play(alpha.animate.set_value(1.75), rate_func=linear, run_time=15)
        self.play(FadeOut(triangle), FadeOut(secant), FadeOut(dot), run_time=.2)

        self.wait(2)

