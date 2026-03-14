import re

def _parse_shoot_line(line):
    raw = (line or "").strip()
    if not raw:
        return None
    raw = raw.replace("　", " ")
    raw = raw.strip()
    # Debug print
    print(f"Original: '{line}'")
    print(f"Pre-regex: '{raw}'")
    
    raw = re.sub(r'^\s*\d+\s*[\.、]?\s*', '', raw)
    print(f"Post-regex: '{raw}'")
    
    parts = [p for p in raw.split() if p]
    print(f"Parts: {parts}")
    
    if len(parts) < 2:
        print("Failed: len(parts) < 2")
        return None
    
    name = parts[0]
    hs = None
    hs_idx = None
    for idx, p in enumerate(parts):
        if p.startswith("HS") and len(p) >= 4:
            hs = p
            hs_idx = idx
            break
            
    if hs and hs_idx is not None and hs_idx + 1 < len(parts):
        direction = parts[-1] if len(parts) >= 2 else ""
        room = parts[-2] if len(parts) >= 3 else ""
        store = parts[hs_idx + 1] if hs_idx + 1 < len(parts) else ""
        addr_parts = parts[hs_idx + 2:-2] if len(parts) >= 3 else []
        address = " ".join(addr_parts).strip()
    else:
        hs = ""
        direction = parts[-1] if len(parts) >= 2 else ""
        room = parts[-2] if len(parts) >= 3 else ""
        mid = parts[1:-2] if len(parts) >= 4 else parts[1:-1]
        
        # Debug logic here
        print(f"Mid parts: {mid}")
        
        if len(mid) >= 2:
            store = mid[0]
            address = " ".join(mid[1:]).strip()
        elif len(mid) == 1:
            store = ""
            address = mid[0]
        else:
            store = ""
            address = ""
            
    return {
        "name": name,
        "hs": hs,
        "store": store,
        "address": address,
        "room": room,
        "direction": direction,
    }

test_lines = [
    "5.李军 芭茅洲 602 西",
    "1.杨红美 HS260311741003 四方小区店 万科半岛国际 8-707 北",
    "6.江浩 HS260302138553 湘江中路店 望江公寓 5-2-603 南"
]

for l in test_lines:
    print("-" * 20)
    res = _parse_shoot_line(l)
    print(f"Result: {res}")
