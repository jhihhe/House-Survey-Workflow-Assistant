// Port of _parse_shoot_line from Python
export interface ShootInfo {
  name: string;
  hs: string;
  store: string;
  address: string;
  room: string;
  direction: string;
  seq?: number;
}

export function parseShootLine(line: string): ShootInfo | null {
  let raw = (line || "").trim();
  if (!raw) return null;
  
  // Replace full-width space
  raw = raw.replace(/\u3000/g, " ").trim();

  // Parse sequence number
  let seq: number | undefined;
  const seqMatch = raw.match(/^\s*(\d+)\s*[\.、．。]?\s*/);
  if (seqMatch) {
    seq = parseInt(seqMatch[1], 10);
    raw = raw.substring(seqMatch[0].length);
  } else {
    // Fallback stripping
    raw = raw.replace(/^\s*\d+\s*[\.、．。]?\s*/, '');
  }

  const parts = raw.split(/\s+/).filter(p => p);
  if (parts.length === 0) return null;

  // Sometimes the name is missing and it starts directly with HS code.
  // Python logic: name = parts[0] unconditionally at first.
  let name = parts[0];

  let hs = "";
  let hsIdx = -1;

  // Find HS code
  for (let i = 0; i < parts.length; i++) {
    if (parts[i].startsWith("HS") && parts[i].length >= 4) {
      hs = parts[i];
      hsIdx = i;
      break;
    }
  }

  let store = "";
  let address = "";
  let room = "";
  let direction = "";

  if (hs && hsIdx !== -1 && hsIdx + 1 < parts.length) {
    // Standard format: Name HS... Store Address... Room Direction
    // Assume standard: Name [0] HS [1] Store [2] Address [3..N-2] Room [N-2] Direction [N-1]
    
    // Direction is always last?
    direction = parts.length >= 2 ? parts[parts.length - 1] : "";
    // Room is always second to last?
    room = parts.length >= 3 ? parts[parts.length - 2] : "";
    
    // Store is after HS
    if (hsIdx + 1 < parts.length) {
        store = parts[hsIdx + 1];
    }
    
    // Address is between Store and Room
    // Indices: Store is at hsIdx + 1
    // Room is at parts.length - 2
    // So address parts are from hsIdx + 2 to parts.length - 2
    const startAddr = hsIdx + 2;
    const endAddr = parts.length - 2;
    
    if (startAddr < endAddr) {
       const addrParts = parts.slice(startAddr, endAddr);
       address = addrParts.join(" ").trim();
    } else {
        // Fallback: if no room/direction, maybe structure is simpler
        address = "";
    }
  } else {
    // Fallback logic if no HS code found or structure is weird
    hs = "";
    direction = parts.length >= 2 ? parts[parts.length - 1] : "";
    room = parts.length >= 3 ? parts[parts.length - 2] : "";
    
    // Middle parts
    let mid: string[] = [];
    if (parts.length >= 4) {
        mid = parts.slice(1, parts.length - 2);
    } else if (parts.length >= 2) {
        mid = parts.slice(1, parts.length - 1); // If only Name Address Direction
    }

    if (mid.length >= 2) {
      store = mid[0];
      address = mid.slice(1).join(" ").trim();
    } else if (mid.length === 1) {
      store = "";
      address = mid[0];
    }
  }

  return {
    name,
    hs,
    store,
    address,
    room,
    direction,
    seq
  };
}
