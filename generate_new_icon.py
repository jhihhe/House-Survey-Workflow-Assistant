import os
from PIL import Image, ImageDraw, ImageOps

def create_gradient_squircle(size, color1, color2):
    # Create base image with transparent background
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # macOS Squircle parameters (approximate)
    # Usually a superellipse, but rounded rect is close enough for script
    # macOS Big Sur icon shape: rounded rect with curvature ~22% of size
    width, height = size
    radius = int(width * 0.225)
    
    # Create mask for squircle
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
    
    # Create gradient
    gradient = Image.new('RGBA', size, color1)
    # Simple vertical gradient
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        # Draw line
        ImageDraw.Draw(gradient).line([(0, y), (width, y)], fill=(r, g, b, 255))
    
    # Apply mask
    output = Image.new('RGBA', size, (0, 0, 0, 0))
    output.paste(gradient, mask=mask)
    
    # Add a slight drop shadow (optional, but macOS adds it usually. 
    # Better to keep it flat for the icon file itself if the OS adds shadow)
    # We will stick to flat squircle as per AppIcon specs
    
    return output

def draw_cat_with_camera(base_image):
    width, height = base_image.size
    draw = ImageDraw.Draw(base_image)
    
    # Colors
    cat_color = (248, 248, 242) # Off-white
    cat_inner_ear = (255, 121, 198) # Pink
    camera_body_color = (40, 42, 54) # Dark Grey/Black
    camera_lens_color = (68, 71, 90) # Lighter Grey
    lens_glass_color = (98, 114, 164) # Blueish
    highlight_color = (255, 255, 255, 200)
    
    # Coordinates (Centered and Large)
    # Cat Head
    head_w = width * 0.65
    head_h = height * 0.55
    head_x = (width - head_w) / 2
    head_y = height * 0.15
    
    # Ears
    ear_w = head_w * 0.35
    ear_h = head_h * 0.5
    
    # Draw Ears
    # Left Ear
    draw.polygon([
        (head_x + head_w*0.1, head_y + head_h*0.3), # Bottom left
        (head_x - ear_w*0.2, head_y - ear_h*0.4), # Tip
        (head_x + head_w*0.4, head_y + head_h*0.1)  # Bottom right
    ], fill=cat_color)
    # Left Inner Ear
    draw.polygon([
        (head_x + head_w*0.15, head_y + head_h*0.25),
        (head_x - ear_w*0.2 + 20, head_y - ear_h*0.4 + 30),
        (head_x + head_w*0.35, head_y + head_h*0.15)
    ], fill=cat_inner_ear)
    
    # Right Ear
    draw.polygon([
        (head_x + head_w*0.6, head_y + head_h*0.1), # Bottom left
        (head_x + head_w + ear_w*0.2, head_y - ear_h*0.4), # Tip
        (head_x + head_w*0.9, head_y + head_h*0.3)  # Bottom right
    ], fill=cat_color)
    # Right Inner Ear
    draw.polygon([
        (head_x + head_w*0.65, head_y + head_h*0.15),
        (head_x + head_w + ear_w*0.2 - 20, head_y - ear_h*0.4 + 30),
        (head_x + head_w*0.85, head_y + head_h*0.25)
    ], fill=cat_inner_ear)
    
    # Draw Head
    draw.ellipse([head_x, head_y, head_x + head_w, head_y + head_h], fill=cat_color)
    
    # Draw Eyes
    eye_size = head_w * 0.12
    eye_y = head_y + head_h * 0.4
    eye_offset = head_w * 0.25
    # Left Eye
    draw.ellipse([head_x + eye_offset - eye_size, eye_y, head_x + eye_offset + eye_size, eye_y + eye_size*2], fill=camera_body_color)
    # Right Eye
    draw.ellipse([head_x + head_w - eye_offset - eye_size, eye_y, head_x + head_w - eye_offset + eye_size, eye_y + eye_size*2], fill=camera_body_color)
    
    # Camera (Held in front)
    cam_w = width * 0.7
    cam_h = height * 0.45
    cam_x = (width - cam_w) / 2
    cam_y = height * 0.55 # Overlapping bottom of face
    
    # Camera Body
    # Rounded rect for camera
    rect_r = 40
    draw.rounded_rectangle([cam_x, cam_y, cam_x + cam_w, cam_y + cam_h], radius=rect_r, fill=camera_body_color)
    
    # Top details (Shutter button, flash)
    draw.rectangle([cam_x + cam_w*0.15, cam_y - 20, cam_x + cam_w*0.35, cam_y], fill=camera_body_color) # Flash housing
    draw.rectangle([cam_x + cam_w*0.7, cam_y - 15, cam_x + cam_w*0.85, cam_y], fill=camera_lens_color) # Button housing
    draw.ellipse([cam_x + cam_w*0.75, cam_y - 25, cam_x + cam_w*0.85, cam_y - 5], fill=(255, 85, 85)) # Red Button
    
    # Lens (Big and central)
    lens_size = cam_h * 0.85
    lens_x = cam_x + (cam_w - lens_size) / 2
    lens_y = cam_y + (cam_h - lens_size) / 2
    
    # Outer ring
    draw.ellipse([lens_x, lens_y, lens_x + lens_size, lens_y + lens_size], fill=camera_lens_color)
    # Inner ring
    draw.ellipse([lens_x + 20, lens_y + 20, lens_x + lens_size - 20, lens_y + lens_size - 20], fill=camera_body_color)
    # Glass
    draw.ellipse([lens_x + 40, lens_y + 40, lens_x + lens_size - 40, lens_y + lens_size - 40], fill=lens_glass_color)
    # Reflection
    draw.ellipse([lens_x + lens_size*0.6, lens_y + lens_size*0.2, lens_x + lens_size*0.75, lens_y + lens_size*0.35], fill=highlight_color)
    
    # Paws (Holding the camera)
    paw_size = cam_h * 0.35
    # Left Paw
    draw.ellipse([cam_x - paw_size*0.3, cam_y + cam_h*0.3, cam_x + paw_size*0.7, cam_y + cam_h*0.3 + paw_size], fill=cat_color)
    # Right Paw
    draw.ellipse([cam_x + cam_w - paw_size*0.7, cam_y + cam_h*0.3, cam_x + cam_w + paw_size*0.3, cam_y + cam_h*0.3 + paw_size], fill=cat_color)

    return base_image

def main():
    # Dracula Colors
    purple = (189, 147, 249)
    pink = (255, 121, 198)
    
    # Create base icon (smaller size to allow padding)
    # macOS icons typically have some transparent padding
    # 1024x1024 canvas, we'll use about 88% of it for the shape (approx 900px)
    icon_size = 900
    icon_content = create_gradient_squircle((icon_size, icon_size), purple, pink)
    
    # Draw content on the smaller surface
    icon_content = draw_cat_with_camera(icon_content)
    
    # Create final 1024x1024 canvas and center the content
    final_icon = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    offset = (1024 - icon_size) // 2
    final_icon.paste(icon_content, (offset, offset))
    
    # Save
    output_dir = 'assets/icons'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'new_macos_icon.png')
    final_icon.save(output_path, 'PNG')
    print(f"Icon generated at {output_path}")

if __name__ == "__main__":
    main()
