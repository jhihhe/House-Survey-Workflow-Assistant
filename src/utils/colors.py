def hex_to_rgb(hex_val):
    hex_val = hex_val.lstrip('#')
    if len(hex_val) == 3:
        hex_val = ''.join([c*2 for c in hex_val])
    return tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*map(int, rgb))

def interpolate_color(start_hex, end_hex, t):
    t = max(0.0, min(1.0, t))
    s = hex_to_rgb(start_hex)
    e = hex_to_rgb(end_hex)
    curr = tuple(s[i] + (e[i] - s[i]) * t for i in range(3))
    return rgb_to_hex(curr)
