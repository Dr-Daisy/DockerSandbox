"""Generate DockerSandbox logo assets."""
from PIL import Image, ImageDraw, ImageFont
import os

SIZE = 256
CORNER_RADIUS = 48
BG_COLOR = "#2196f3"
ACCENT_COLOR = "#1976d2"
FG_COLOR = "#ffffff"
SAND_COLOR = "#ffcc80"


def rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_logo(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    scale = size / 256.0
    r = int(CORNER_RADIUS * scale)

    # Background rounded rect with subtle gradient simulation
    for y in range(size):
        ratio = y / size
        r_col = int(33 + (25 - 33) * ratio)
        g_col = int(150 + (118 - 150) * ratio)
        b_col = int(243 + (210 - 243) * ratio)
        color = (r_col, g_col, b_col, 255)
        draw.line([(0, y), (size, y)], fill=color)

    # Mask to rounded rect
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=r, fill=255)
    img.putalpha(mask)

    draw = ImageDraw.Draw(img)

    # Draw a container box (white outline)
    box_left = int(64 * scale)
    box_top = int(70 * scale)
    box_right = int(192 * scale)
    box_bottom = int(186 * scale)
    line_w = max(1, int(6 * scale))

    # Main box
    draw.rectangle(
        [box_left, box_top, box_right, box_bottom],
        outline=FG_COLOR,
        width=line_w,
    )

    # Container vertical lines (door ribs)
    ribs = 3
    for i in range(1, ribs):
        x = box_left + (box_right - box_left) * i // ribs
        draw.line(
            [(x, box_top), (x, box_bottom)],
            fill=FG_COLOR,
            width=max(1, int(3 * scale)),
        )

    # Draw "sand" at bottom - a gentle mound inside the box
    sand_y = box_bottom - int(18 * scale)
    sand_points = [
        (box_left + line_w, box_bottom - line_w),
        (box_left + int(40 * scale), sand_y),
        (box_left + int(80 * scale), sand_y - int(8 * scale)),
        (box_left + int(128 * scale), sand_y - int(4 * scale)),
        (box_right - int(40 * scale), sand_y),
        (box_right - line_w, box_bottom - line_w),
    ]
    draw.polygon(sand_points, fill=SAND_COLOR)

    # Draw sand grains (little dots)
    grains = [
        (box_left + int(50 * scale), sand_y - int(2 * scale)),
        (box_left + int(70 * scale), sand_y - int(6 * scale)),
        (box_left + int(100 * scale), sand_y - int(3 * scale)),
        (box_left + int(120 * scale), sand_y - int(7 * scale)),
        (box_left + int(140 * scale), sand_y - int(2 * scale)),
    ]
    for gx, gy in grains:
        r_grain = max(1, int(3 * scale))
        draw.ellipse([gx - r_grain, gy - r_grain, gx + r_grain, gy + r_grain], fill=SAND_COLOR)

    # Draw a small cube floating above (representing container/sandbox element)
    cube_size = int(24 * scale)
    cube_cx = (box_left + box_right) // 2
    cube_cy = box_top - int(22 * scale)
    cs = cube_size // 2
    # Front face
    draw.polygon(
        [
            (cube_cx, cube_cy - cs),
            (cube_cx + cs, cube_cy),
            (cube_cx, cube_cy + cs),
            (cube_cx - cs, cube_cy),
        ],
        fill=FG_COLOR,
    )
    # Top highlight
    draw.polygon(
        [
            (cube_cx, cube_cy - cs),
            (cube_cx + cs - int(4 * scale), cube_cy - int(4 * scale)),
            (cube_cx, cube_cy),
            (cube_cx - cs + int(4 * scale), cube_cy - int(4 * scale)),
        ],
        fill=(255, 255, 255, 200),
    )

    return img


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate main PNG
    logo_256 = draw_logo(256)
    logo_256.save(os.path.join(base_dir, "logo.png"))
    print("Saved logo.png (256x256)")

    # Generate smaller sizes
    for s in (128, 64, 32, 16):
        logo = draw_logo(s)
        logo.save(os.path.join(base_dir, f"logo_{s}.png"))
        print(f"Saved logo_{s}.png")

    # Generate ICO for Windows
    sizes = [16, 32, 48, 64, 128, 256]
    icons = [draw_logo(s) for s in sizes]
    icons[0].save(
        os.path.join(base_dir, "logo.ico"),
        format="ICO",
        sizes=[(s, s) for s in sizes],
    )
    print("Saved logo.ico")


if __name__ == "__main__":
    main()
