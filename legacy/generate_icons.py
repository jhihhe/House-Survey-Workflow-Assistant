from PIL import Image, ImageDraw, ImageFont
import os
import math

# Colors (Dracula Theme)
BG = '#282a36'
FG = '#f8f8f2'
PURPLE = '#bd93f9'
PINK = '#ff79c6'
CYAN = '#8be9fd'
GREEN = '#50fa7b'
ORANGE = '#ffb86c'
YELLOW = '#f1fa8c'

SIZE = (1024, 1024)
CENTER = (512, 512)

def create_base_image():
    return Image.new('RGBA', SIZE, (0, 0, 0, 0))

def draw_rounded_rect(draw, xy, corner_radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=corner_radius, fill=fill, outline=outline, width=width)

# Option 1: Neon Folder (House Focus)
def create_option_1():
    img = create_base_image()
    draw = ImageDraw.Draw(img)
    
    # Circular Background
    draw.ellipse([(50, 50), (974, 974)], fill=BG, outline=PURPLE, width=20)
    
    # Folder Icon (Abstract)
    folder_pts = [
        (200, 300), (400, 300), (450, 350), (824, 350),
        (824, 800), (200, 800)
    ]
    draw.polygon(folder_pts, fill=None, outline=PINK, width=30)
    
    # House Icon inside
    house_pts = [
        (350, 600), (512, 450), (674, 600), # Roof
        (624, 600), (624, 750), (400, 750), (400, 600) # Body
    ]
    draw.polygon(house_pts, fill=CYAN, outline=FG, width=10)
    
    # Text
    # draw.text((512, 850), "FC", fill=FG, anchor="mm", font_size=100) # Requires recent Pillow
    
    return img

# Option 2: Shutter Speed (Lens Focus)
def create_option_2():
    img = create_base_image()
    draw = ImageDraw.Draw(img)
    
    # Circular Background
    draw.ellipse([(50, 50), (974, 974)], fill=BG, outline=CYAN, width=20)
    
    # Shutter Blades
    center_x, center_y = 512, 512
    radius = 350
    num_blades = 6
    for i in range(num_blades):
        angle = (360 / num_blades) * i
        start_angle = math.radians(angle)
        end_angle = math.radians(angle + 120)
        
        # Simple blade approximation
        x1 = center_x + math.cos(start_angle) * radius
        y1 = center_y + math.sin(start_angle) * radius
        
        draw.arc([(162, 162), (862, 862)], start=angle, end=angle+90, fill=PURPLE, width=40)

    # Center Lens
    draw.ellipse([(400, 400), (624, 624)], fill=None, outline=GREEN, width=20)
    draw.ellipse([(450, 450), (574, 574)], fill=GREEN)
    
    return img

def create_option_3_v2():
    # Create base
    img = Image.new('RGBA', SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # macOS Style Rounded Square Background (Squircle)
    # Standard macOS icon shape approximation
    bg_color = BG # Dracula Background
    rect_coords = [(100, 100), (924, 924)]
    draw.rounded_rectangle(rect_coords, radius=180, fill=bg_color, outline=None)
    
    # Add a subtle gradient effect (simulated with concentric rounded rects) for depth
    for i in range(20):
        color_val = int(40 + i * 2) # Slightly lighter towards center
        c = f"#{color_val:02x}{color_val:02x}{color_val+10:02x}"
        margin = 100 + i * 2
        draw.rounded_rectangle([(margin, margin), (1024-margin, 1024-margin)], radius=180-i, outline=c, width=2)

    # Pixel Cat Logic (Centered and larger)
    # Cat Body Color: White (Dracula FG)
    cat_color = FG
    
    # Head
    draw.rectangle([(400, 300), (624, 500)], fill=cat_color)
    # Ears (Triangular pixels)
    draw.polygon([(400, 300), (400, 220), (480, 300)], fill=cat_color)
    draw.polygon([(624, 300), (624, 220), (544, 300)], fill=cat_color)
    # Eyes
    draw.rectangle([(440, 380), (480, 420)], fill=BG)
    draw.rectangle([(544, 380), (584, 420)], fill=BG)
    # Nose/Mouth area
    draw.rectangle([(492, 440), (532, 460)], fill=PINK)

    # Body
    draw.rectangle([(450, 500), (574, 750)], fill=cat_color)
    
    # Tail (Upright and curled)
    draw.rectangle([(574, 680), (700, 720)], fill=cat_color)
    draw.rectangle([(660, 580), (700, 680)], fill=cat_color)

    # Camera (Held by cat)
    # Camera Body: Cyan
    cam_x, cam_y = 300, 550
    draw.rectangle([(cam_x, cam_y), (cam_x+180, cam_y+120)], fill=CYAN)
    # Lens: Purple
    draw.ellipse([(cam_x+50, cam_y+20), (cam_x+130, cam_y+100)], fill=PURPLE, outline=FG, width=5)
    # Flash/Button
    draw.rectangle([(cam_x+20, cam_y-20), (cam_x+60, cam_y)], fill=ORANGE)
    
    # Arm holding camera
    draw.rectangle([(450, 580), (480, 620)], fill=cat_color) # Shoulder connection
    
    return img

def save_icons():
    # ... (previous options)
    
    opt3_v2 = create_option_3_v2()
    opt3_v2.save("assets/icons/final_icon.png")
    
    # Create icns (Requires iconutil on macOS, usually works on folder of pngs)
    # For now, we just save the high-res PNG which can be used by py2app (it converts it)
    
    print("Final icon generated: assets/icons/final_icon.png")

if __name__ == "__main__":
    save_icons()
