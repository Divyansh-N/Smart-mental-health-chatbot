from PIL import Image, ImageDraw

S = 1024  # draw big, then shrink for smooth edges

# background gradient: deep blue (top) -> teal (bottom)
TOP, BOTTOM = (22, 42, 84), (18, 140, 150)
bg = Image.new("RGBA", (S, S))
bd = ImageDraw.Draw(bg)
for y in range(S):
    t = y / (S - 1)
    color = tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3)) + (255,)
    bd.line([(0, y), (S, y)], fill=color)

# rounded-square shape
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=220, fill=255)
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
img.paste(bg, (0, 0), mask)

d = ImageDraw.Draw(img)

# white chat bubble with a tail
d.rounded_rectangle((190, 220, 834, 700), radius=130, fill=(255, 255, 255, 255))
d.polygon([(320, 670), (290, 830), (520, 690)], fill=(255, 255, 255, 255))

# heartbeat line inside the bubble
pulse = [(270, 460), (400, 460), (455, 340), (530, 590), (600, 400), (640, 460), (754, 460)]
line_color = (18, 120, 135, 255)
d.line(pulse, fill=line_color, width=36, joint="curve")
for x, y in (pulse[0], pulse[-1]):
    d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=line_color)

img = img.resize((256, 256), Image.LANCZOS)
img.save("icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("icon.ico created")