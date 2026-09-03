from math import comb
from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 128
SCALE = 4
WHITE = (255, 255, 255, 255)
DIM = (255, 255, 255, 150)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "freebird_curve_editor" / "assets" / "icons"


def scaled(value):
    if isinstance(value, (tuple, list)):
        return tuple(round(component * SCALE) for component in value)
    return round(value * SCALE)


def canvas():
    return Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))


def line(draw, points, fill=WHITE, width=8):
    draw.line([scaled(point) for point in points], fill=fill, width=scaled(width), joint="curve")


def ellipse(draw, box, outline=WHITE, width=8, fill=None):
    draw.ellipse(scaled(box), fill=fill, outline=outline, width=scaled(width))


def bezier_points(control_points, steps=32):
    degree = len(control_points) - 1
    for step in range(steps + 1):
        t = step / steps
        yield tuple(
            sum(
                comb(degree, index)
                * ((1.0 - t) ** (degree - index))
                * (t**index)
                * control_points[index][axis]
                for index in range(degree + 1)
            )
            for axis in range(2)
        )


def save(image, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUTPUT_DIR / name, optimize=True)


def draw_curve_icon(editing):
    image = canvas()
    draw = ImageDraw.Draw(image)
    curve = list(bezier_points(((17, 92), (43, 12), (81, 116), (112, 39))))
    line(draw, curve, width=8)
    if editing:
        for point in ((17, 92), (64, 67), (112, 39)):
            ellipse(draw, (point[0] - 8, point[1] - 8, point[0] + 8, point[1] + 8), width=5, fill=(0, 0, 0, 255))
    else:
        line(draw, ((78, 94), (106, 66)), width=13)
        line(draw, ((73, 103), (78, 94)), width=9)
        line(draw, ((106, 66), (113, 73)), width=9)
    return image


def draw_falloff_icon(enabled):
    image = canvas()
    draw = ImageDraw.Draw(image)
    ellipse(draw, (18, 18, 110, 110), outline=DIM, width=7)
    ellipse(draw, (41, 41, 87, 87), outline=WHITE, width=7)
    ellipse(draw, (57, 57, 71, 71), outline=WHITE, width=3, fill=WHITE)
    if not enabled:
        line(draw, ((25, 105), (104, 26)), fill=(255, 255, 255, 230), width=9)
    return image


def draw_add_point_icon():
    image = canvas()
    draw = ImageDraw.Draw(image)
    line(draw, ((16, 69), (112, 69)), width=8)
    for x in (18, 110):
        ellipse(draw, (x - 8, 61, x + 8, 77), width=5, fill=(0, 0, 0, 255))
    ellipse(draw, (43, 43, 95, 95), outline=None, fill=(35, 35, 35, 255))
    line(draw, ((52, 69), (86, 69)), width=8)
    line(draw, ((69, 52), (69, 86)), width=8)
    return image


def draw_radius_icon(symbol=None):
    image = canvas()
    draw = ImageDraw.Draw(image)
    ellipse(draw, (26, 26, 102, 102), outline=WHITE, width=8)
    ellipse(draw, (55, 55, 73, 73), outline=WHITE, width=3, fill=WHITE)
    if symbol:
        ellipse(draw, (78, 78, 120, 120), outline=None, fill=(35, 35, 35, 255))
        line(draw, ((86, 99), (112, 99)), width=7)
        if symbol == "plus":
            line(draw, ((99, 86), (99, 112)), width=7)
    return image


def main():
    save(draw_curve_icon(False), "draw_in.png")
    save(draw_curve_icon(True), "edit_curve.png")
    save(draw_add_point_icon(), "add_point.png")
    save(draw_falloff_icon(True), "falloff_on.png")
    save(draw_falloff_icon(False), "falloff_off.png")
    save(draw_radius_icon("minus"), "radius_down.png")
    save(draw_radius_icon(), "radius_value.png")
    save(draw_radius_icon("plus"), "radius_up.png")


if __name__ == "__main__":
    main()
