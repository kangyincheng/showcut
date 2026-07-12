"""
Generate ShowCut application icon - jeo logo style
Generates standard multi-resolution ICO file (16/32/48/64/128/256)
"""

from PIL import Image, ImageDraw
import os
import math
import struct
import io


def create_jeo_logo(size=1024, bg_color=(255, 255, 255, 255), fg_color=(0, 0, 0)):
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    s = size
    fg = fg_color
    bg = bg_color

    col_left_x = int(s * 0.20)
    col_right_x = int(s * 0.80)
    col_w = int(s * 0.08)
    beam_y = int(s * 0.38)
    beam_h = int(s * 0.035)
    letter_r = int(s * 0.085)
    e_cx = int(s * 0.38)
    o_cx = int(s * 0.62)
    letter_cy = beam_y - int(letter_r * 0.6)
    col_bottom = int(s * 0.76)
    hook_r = int(s * 0.09)
    ball_r = int(s * 0.038)
    cap_h = int(s * 0.05)
    cap_ext = int(s * 0.10)
    stroke = int(s * 0.03)

    # Left column
    draw.rectangle(
        [col_left_x, beam_y + beam_h // 2, col_left_x + col_w, col_bottom],
        fill=fg,
    )
    draw.rectangle(
        [col_left_x - cap_ext, beam_y - cap_h - beam_h // 2, col_left_x + col_w, beam_y - beam_h // 2],
        fill=fg,
    )

    # Left hook
    hook_cx_left = col_left_x + hook_r
    hook_cy_left = col_bottom - hook_r
    outer_pts = []
    inner_pts = []
    for a in range(180, -1, -1):
        rad = math.radians(a)
        outer_pts.append((hook_cx_left + hook_r * math.cos(rad), hook_cy_left + hook_r * math.sin(rad)))
    inner_r_left = hook_r - col_w
    for a in range(0, 181):
        rad = math.radians(a)
        inner_pts.append((hook_cx_left + inner_r_left * math.cos(rad), hook_cy_left + inner_r_left * math.sin(rad)))
    all_pts = outer_pts + inner_pts
    if len(all_pts) > 2:
        draw.polygon(all_pts, fill=fg)
    ball_cx = hook_cx_left + hook_r
    ball_cy = hook_cy_left
    draw.ellipse([ball_cx - ball_r, ball_cy - ball_r, ball_cx + ball_r, ball_cy + ball_r], fill=fg)

    # Right column
    right_col_left = col_right_x - col_w
    draw.rectangle(
        [right_col_left, beam_y + beam_h // 2, col_right_x, col_bottom],
        fill=fg,
    )
    draw.rectangle(
        [right_col_left, beam_y - cap_h - beam_h // 2, col_right_x + cap_ext, beam_y - beam_h // 2],
        fill=fg,
    )

    # Right hook
    hook_cx_right = right_col_left - hook_r
    hook_cy_right = col_bottom - hook_r
    outer_pts_r = []
    inner_pts_r = []
    for a in range(0, 181):
        rad = math.radians(a)
        outer_pts_r.append((hook_cx_right + hook_r * math.cos(rad), hook_cy_right + hook_r * math.sin(rad)))
    inner_r_right = hook_r - col_w
    for a in range(180, -1, -1):
        rad = math.radians(a)
        inner_pts_r.append((hook_cx_right + inner_r_right * math.cos(rad), hook_cy_right + inner_r_right * math.sin(rad)))
    all_pts_r = outer_pts_r + inner_pts_r
    if len(all_pts_r) > 2:
        draw.polygon(all_pts_r, fill=fg)
    ball_cx_r = hook_cx_right - hook_r
    ball_cy_r = hook_cy_right
    draw.ellipse([ball_cx_r - ball_r, ball_cy_r - ball_r, ball_cx_r + ball_r, ball_cy_r + ball_r], fill=fg)

    # Beam
    draw.rectangle(
        [col_left_x + col_w, beam_y - beam_h // 2, right_col_left, beam_y + beam_h // 2],
        fill=fg,
    )

    # Letter e
    draw.ellipse([e_cx - letter_r, letter_cy - letter_r, e_cx + letter_r, letter_cy + letter_r], fill=fg)
    inner_r_e = letter_r - stroke
    draw.ellipse([e_cx - inner_r_e, letter_cy - inner_r_e, e_cx + inner_r_e, letter_cy + inner_r_e], fill=bg)
    draw.rectangle([e_cx - inner_r_e, letter_cy - stroke // 2, e_cx + int(inner_r_e * 0.4), letter_cy + stroke // 2], fill=fg)
    gap_w = int(s * 0.012)
    draw.rectangle([e_cx + letter_r - gap_w, letter_cy - int(inner_r_e * 0.5), e_cx + letter_r, letter_cy + int(inner_r_e * 0.5)], fill=bg)

    # Letter o
    draw.ellipse([o_cx - letter_r, letter_cy - letter_r, o_cx + letter_r, letter_cy + letter_r], fill=fg)
    inner_r_o = letter_r - stroke
    draw.ellipse([o_cx - inner_r_o, letter_cy - inner_r_o, o_cx + inner_r_o, letter_cy + inner_r_o], fill=bg)

    # Merge letters with beam
    draw.rectangle([e_cx - inner_r_e + 1, letter_cy, e_cx + inner_r_e - 1, beam_y + beam_h // 2], fill=bg)
    draw.rectangle([o_cx - inner_r_o + 1, letter_cy, o_cx + inner_r_o - 1, beam_y + beam_h // 2], fill=bg)

    return img


def generate_icon():
    source = create_jeo_logo(size=1024, bg_color=(255, 255, 255, 255), fg_color=(0, 0, 0, 255))
    source.save("icon.png", "PNG")
    print("icon.png generated (1024x1024)")

    sizes = [256, 128, 64, 48, 32, 24, 16]
    png_datas = []
    for sz in sizes:
        resized = source.resize((sz, sz), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="PNG")
        png_datas.append((sz, buf.getvalue()))

    with open("icon.ico", "wb") as f:
        f.write(struct.pack("<HHH", 0, 1, len(png_datas)))
        data_offset = 6 + 16 * len(png_datas)
        for sz, data in png_datas:
            w = sz if sz < 256 else 0
            h = sz if sz < 256 else 0
            f.write(struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), data_offset))
            data_offset += len(data)
        for sz, data in png_datas:
            f.write(data)

    print(f"icon.ico generated ({len(sizes)} sizes: {sizes})")
    print(f"icon.ico size: {os.path.getsize('icon.ico')} bytes")


if __name__ == "__main__":
    generate_icon()
