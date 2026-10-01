from manim import *
import colors

config.disable_caching = True
config.flush_cache = True

class WitchAgnesiCurve(MovingCameraScene):

    def construct(self):
        self.default_color = colors.VERY_DARK_ORANGE_BROWN_TONE
        self.show_circle()
        self.show_origin()
        self.show_axis()
        self.draw_curve()    


    def show_circle(self):
        self.radius = 1

        self.origin = np.array(DOWN)
        self.center = self.origin + UP * self.radius 

        circle = Circle(radius=self.radius, color= self.default_color, z_index=-1)
        circle.move_to(self.center)

        self.circle = circle
        self.add(circle)

    def show_origin(self):
        origin = Dot(self.origin, color= self.default_color)
        origin.set_z_index(2)

        self.origin_dot = origin
        self.add(origin)

    def show_axis(self):
        dx = 10
        origin = self.origin
        radius = self.radius

        start = origin + LEFT * dx + UP * 2 * radius
        end = origin + RIGHT * dx + UP *  2 *radius

        self.horizontal_line = [start, end]
        self.axis = Line(*self.horizontal_line, color=self.default_color, z_index=-1)

        self.add(self.axis)

    def draw_curve(self):
        orbit = self.circle
        origin = self.origin
        dot_color = colors.SOFT_ORANGE 
        curve_color = colors.LIGHT_RED
        triangle_color = colors.VERY_LIGHT_BLUE
        text_color = colors.VERY_DARK_ORANGE_BROWN_TONE

        self.curve_point_color = triangle_color

        alpha = ValueTracker(0)

        def get_dot_on_circle():
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
            dot.set_z_index(2)

            return dot

        def get_intersection_point():
            secant_line = [origin, get_dot_on_circle().get_center()]
            if cross2d(Line(*secant_line).get_unit_vector(), Line(*self.horizontal_line).get_unit_vector()) == 0:
                return  np.array(self.origin)
            else :
                intersection_point = line_intersection(secant_line, self.horizontal_line)
                return np.array(intersection_point)

        def get_secant():
            return  Line(self.origin, get_intersection_point(), color=dot_color, z_index=1)

        def get_curve_point():
            third_point = get_intersection_point() + DOWN
            triangle_vertical_side = Line(get_intersection_point(), third_point)
            curve_point = triangle_vertical_side.get_projection(get_dot_on_circle().get_center())

            return curve_point

        def get_triangle_sides():
            vertical_side =  Line(get_intersection_point(), get_curve_point(), color=triangle_color)
            horizontal_side = Line(get_dot_on_circle(), get_curve_point(), color=triangle_color)

            return [vertical_side, horizontal_side]

        def get_triangle():
            return VGroup(
                    *get_triangle_sides(), 
                    Dot(get_curve_point(), color=self.curve_point_color, radius=0.05)
                    )

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

        def get_labels():
            offset = 0.3
            coordinates = [
                self.origin + DOWN * offset,
                get_dot_on_circle().get_center() + LEFT * offset + UP * 0.1,
                get_intersection_point() + UP * offset,
                get_curve_point() + DOWN * offset,
            ]
            colors = [text_color, dot_color, dot_color, curve_color]
            names_regex = [r"O", r"N", r"P", r"M"]
            names_mobjects = map(
                lambda x: 
                    Typst(
                        x, 
                        typst_preamble="#set text(font: \"New Computer Modern Sans\")"
                    ), 
                    names_regex
            )
            return VGroup(*[
                name.move_to(coordinate).set_color(color)
                for name, coordinate, color in zip(names_mobjects, coordinates, colors)
            ])


        def get_title():
            typst = Typst(
                r"Versiera der Agnesi",
                typst_preamble="#set text(font: \"New Computer Modern Sans\")"
            )
            return typst.move_to(3 * UP).set_color(text_color)

        moving_figure_parts = [
            get_dot_on_circle, 
            get_secant, 
            get_triangle, 
            get_right_angle, 
            get_curve
        ]
        
        dot_on_circle, secant, triangle, right_angle, curve = map(always_redraw, moving_figure_parts)
        curve_dot = triangle[-1]

        show_secant = AnimationGroup(
            Create(secant, run_time = 2),
            FadeIn(dot_on_circle, run_time = 0.5),
            lag_ratio=.4
        )

        show_curve = AnimationGroup(
            alpha.animate(rate_func=linear, run_time=25).set_value(1.75), 
            Restore(self.camera.frame, run_time=7, rate_func=rate_functions.ease_in_out_cubic),
            lag_ratio=.2
        )

        remove_construction_artifacts = AnimationGroup(
            FadeOut(triangle),
            FadeOut(secant),
            FadeOut(dot_on_circle),
            run_time=2
        )

        # show title and equation
        title = get_title()
        self.play(Write(title))

        self.wait(2)

        # zoom in on circle
        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.set(width=8))

        # initiate triangle construction
        self.play(show_secant)
        self.play(Create(triangle, run_time = 2))
        self.play(FadeIn(right_angle, run_time = 1))

        # indication right angle and show curve point
        self.play(Indicate(right_angle, color=colors.LIGHT_MAGENTA))
        self.play(FadeOut(right_angle))
        self.curve_point_color = curve_color
        self.play(curve_dot.animate.set_color(curve_color))

        # show temporarily important points names as indicators
        labels = get_labels()
        self.play(Write(labels))

        self.wait(3)

        self.play(FadeOut(labels))

        # add and show curve
        self.add(curve)
        self.play(show_curve)
        self.play(remove_construction_artifacts)

        self.wait(1)

        # remove background axis and circle
        self.play(FadeOut(self.circle, self.origin_dot, self.axis))

        self.wait(3)

