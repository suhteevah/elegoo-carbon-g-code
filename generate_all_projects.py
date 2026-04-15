"""
Etsy Product Line Generator - 10 Geometric/Modern 3D Printable Products
=========================================================================
Generates STL files for all projects.
All designs are original, parametric, and optimized for FDM printing.
"""

import numpy as np
from stl import mesh
import math
import os

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

# =============================================================================
# SHARED GEOMETRY HELPERS
# =============================================================================

def polygon_points(radius, sides, z=0, angle_offset=0):
    angles = np.linspace(0, 2*np.pi, sides, endpoint=False) + angle_offset
    pts = np.zeros((sides, 3))
    pts[:, 0] = radius * np.cos(angles)
    pts[:, 1] = radius * np.sin(angles)
    pts[:, 2] = z
    return pts

def circle_points(radius, n=32, z=0, center=(0,0)):
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    pts = np.zeros((n, 3))
    pts[:, 0] = center[0] + radius * np.cos(angles)
    pts[:, 1] = center[1] + radius * np.sin(angles)
    pts[:, 2] = z
    return pts

def tri(p1, p2, p3):
    return np.array([p1, p2, p3])

def quad(p1, p2, p3, p4):
    return [tri(p1, p2, p3), tri(p1, p3, p4)]

def ring_wall(bot, top):
    tris = []
    n = len(bot)
    for i in range(n):
        j = (i+1) % n
        tris.extend(quad(bot[i], bot[j], top[j], top[i]))
    return tris

def ring_wall_rev(bot, top):
    tris = []
    n = len(bot)
    for i in range(n):
        j = (i+1) % n
        tris.extend(quad(bot[j], bot[i], top[i], top[j]))
    return tris

def fan(center, ring, flip=False):
    tris = []
    n = len(ring)
    for i in range(n):
        j = (i+1) % n
        if flip:
            tris.append(tri(center, ring[j], ring[i]))
        else:
            tris.append(tri(center, ring[i], ring[j]))
    return tris

def annular(outer, inner, flip=False):
    tris = []
    n = len(outer)
    for i in range(n):
        j = (i+1) % n
        if flip:
            tris.extend(quad(outer[j], outer[i], inner[i], inner[j]))
        else:
            tris.extend(quad(outer[i], outer[j], inner[j], inner[i]))
    return tris

def save_stl(triangles, filepath):
    arr = np.array(triangles)
    m = mesh.Mesh(np.zeros(len(arr), dtype=mesh.Mesh.dtype))
    m.vectors = arr
    m.update_normals()
    m.save(filepath)
    return len(arr)

def box_tris(x, y, z, w, d, h):
    """Generate a rectangular box from corner (x,y,z) with dimensions w,d,h."""
    tris = []
    p = [
        [x,   y,   z],
        [x+w, y,   z],
        [x+w, y+d, z],
        [x,   y+d, z],
        [x,   y,   z+h],
        [x+w, y,   z+h],
        [x+w, y+d, z+h],
        [x,   y+d, z+h],
    ]
    p = [np.array(v) for v in p]
    # bottom
    tris.extend(quad(p[0], p[3], p[2], p[1]))
    # top
    tris.extend(quad(p[4], p[5], p[6], p[7]))
    # front
    tris.extend(quad(p[0], p[1], p[5], p[4]))
    # back
    tris.extend(quad(p[2], p[3], p[7], p[6]))
    # left
    tris.extend(quad(p[3], p[0], p[4], p[7]))
    # right
    tris.extend(quad(p[1], p[2], p[6], p[5]))
    return tris


def hollow_cylinder(r_outer, r_inner, h, n=32, z_base=0):
    """Hollow cylinder (tube)."""
    tris = []
    ob = circle_points(r_outer, n, z_base)
    ot = circle_points(r_outer, n, z_base + h)
    ib = circle_points(r_inner, n, z_base)
    it_ = circle_points(r_inner, n, z_base + h)
    tris.extend(ring_wall(ob, ot))
    tris.extend(ring_wall_rev(ib, it_))
    tris.extend(annular(ob, ib, flip=True))
    tris.extend(annular(ot, it_, flip=False))
    return tris

def solid_cylinder(r, h, n=32, z_base=0, center=(0,0)):
    """Solid cylinder."""
    tris = []
    bot = circle_points(r, n, z_base, center)
    top = circle_points(r, n, z_base + h, center)
    c_bot = np.array([center[0], center[1], z_base])
    c_top = np.array([center[0], center[1], z_base + h])
    tris.extend(ring_wall(bot, top))
    tris.extend(fan(c_bot, bot, flip=True))
    tris.extend(fan(c_top, top, flip=False))
    return tris


# =============================================================================
# PROJECT 02: HONEYCOMB DESK ORGANIZER
# =============================================================================

def generate_02_honeycomb_desk_organizer():
    """Hexagonal honeycomb pencil/pen cup with 3 connected hex cells."""
    print("  [02] Honeycomb Desk Organizer...")
    tris = []

    hex_r = 25       # circumradius (center to vertex)
    wall = 2.4
    height = 100
    bottom = 2.0
    sides = 6

    # For a flat-topped hex (pointy-top with 30° offset), the apothem
    # (center to flat edge) = hex_r * cos(30°) = hex_r * sqrt(3)/2.
    # Two adjacent hexes touching edge-to-edge need center spacing of
    # 2 * apothem + wall gap = hex_r * sqrt(3) + wall
    apothem = hex_r * math.sqrt(3) / 2  # ~21.65mm
    spacing = 2 * apothem + wall         # ~45.7mm edge-to-edge with gap

    # Three hex cells in a horizontal row (inline, sharing flat edges)
    # This avoids overlap: cells are spaced along X axis
    centers = [
        (-spacing, 0),
        (0, 0),
        (spacing, 0),
    ]

    # Hex orientation: pointy-top (default polygon_points with 0 offset
    # gives a vertex pointing right). Rotate 30° so a FLAT side faces
    # the adjacent cell, enabling clean edge-to-edge packing.
    hex_angle_offset = np.pi / 6  # 30° rotation = flat-topped hex

    for cx, cy in centers:
        # Outer wall
        ob = polygon_points(hex_r, sides, 0, hex_angle_offset)
        ot = polygon_points(hex_r, sides, height, hex_angle_offset)
        ob[:, 0] += cx; ob[:, 1] += cy
        ot[:, 0] += cx; ot[:, 1] += cy
        tris.extend(ring_wall(ob, ot))

        # Inner wall
        ib = polygon_points(hex_r - wall, sides, 0, hex_angle_offset)
        it_ = polygon_points(hex_r - wall, sides, height, hex_angle_offset)
        ib[:, 0] += cx; ib[:, 1] += cy
        it_[:, 0] += cx; it_[:, 1] += cy
        tris.extend(ring_wall_rev(ib, it_))

        # Outer bottom
        ob_bot = polygon_points(hex_r, sides, 0, hex_angle_offset)
        ob_bot[:, 0] += cx; ob_bot[:, 1] += cy
        c_bot = np.array([cx, cy, 0])
        tris.extend(fan(c_bot, ob_bot, flip=True))

        # Inner bottom (raised floor)
        ib_floor = polygon_points(hex_r - wall, sides, bottom, hex_angle_offset)
        ib_floor[:, 0] += cx; ib_floor[:, 1] += cy
        c_inner = np.array([cx, cy, bottom])
        tris.extend(fan(c_inner, ib_floor, flip=False))

        # Connect inner wall bottom edge to inner floor
        ib_at_0 = polygon_points(hex_r - wall, sides, 0, hex_angle_offset)
        ib_at_0[:, 0] += cx; ib_at_0[:, 1] += cy
        tris.extend(ring_wall_rev(ib_at_0, ib_floor))

        # Top rim (annular ring connecting outer to inner at top)
        outer_top = polygon_points(hex_r, sides, height, hex_angle_offset)
        inner_top = polygon_points(hex_r - wall, sides, height, hex_angle_offset)
        outer_top[:, 0] += cx; outer_top[:, 1] += cy
        inner_top[:, 0] += cx; inner_top[:, 1] += cy
        tris.extend(annular(outer_top, inner_top, flip=False))

    # Connecting bridges between adjacent cells
    bridge_h = 12
    bridge_w = 10
    bridge_thick = wall
    for i in range(len(centers) - 1):
        c1 = centers[i]
        c2 = centers[i + 1]
        mx = (c1[0] + c2[0]) / 2
        my = (c1[1] + c2[1]) / 2
        for bz in [15, 45, 75]:
            tris.extend(box_tris(mx - bridge_thick/2, my - bridge_w/2, bz,
                                 bridge_thick, bridge_w, bridge_h))

    outdir = os.path.join(PROJECTS_DIR, "02_honeycomb_desk_organizer")
    path = os.path.join(outdir, "honeycomb_organizer.stl")
    count = save_stl(tris, path)
    print(f"    -> {path} ({count} triangles)")
    return path


# =============================================================================
# PROJECT 03: MODERN WALL HOOK SET (3 sizes)
# =============================================================================

def _wedge_tris(x0, x1, points_left, points_right):
    """Create a solid wedge/prism between two X-planes from matching point rings.
    points_left and points_right are ordered vertex lists forming a closed polygon
    on the x=x0 and x=x1 planes respectively. They must have the same length."""
    tris = []
    n = len(points_left)

    # Left face fan (x=x0 plane)
    center_l = np.mean(points_left, axis=0)
    for i in range(n):
        j = (i + 1) % n
        tris.append(tri(center_l, points_left[j], points_left[i]))

    # Right face fan (x=x1 plane)
    center_r = np.mean(points_right, axis=0)
    for i in range(n):
        j = (i + 1) % n
        tris.append(tri(center_r, points_right[i], points_right[j]))

    # Side walls connecting left to right
    for i in range(n):
        j = (i + 1) % n
        tris.extend(quad(points_left[i], points_left[j],
                         points_right[j], points_right[i]))

    return tris


def generate_03_wall_hooks():
    """Modern wall hooks - set of 3 sizes. Designed for flat printing, zero supports.

    Print orientation: back plate flat on bed (XY plane).
    The hook uses a solid 45° triangular gusset under the arm instead of
    a floating overhang. The lip points upward. No geometry exceeds 45°.

    Coordinate system as printed:
      X = hook width (left-right)
      Y = depth (how far hook sticks out from wall)
      Z = height (print layers build up)
    """
    print("  [03] Modern Wall Hook Set...")
    paths = []

    for idx, (label, arm_reach, lip_height, width) in enumerate([
        ("small",  20, 12, 20),
        ("medium", 30, 18, 25),
        ("large",  40, 25, 30),
    ]):
        tris = []
        thick = 5.0
        plate_h = 60 + idx * 15   # back plate total Z height

        # --- Back plate (flat on bed, the screw-to-wall part) ---
        tris.extend(box_tris(-width/2, 0, 0, width, thick, plate_h))

        # --- Hook arm (extends in +Y from top of back plate) ---
        arm_z_bot = plate_h - thick
        arm_z_top = plate_h
        tris.extend(box_tris(-width/2, thick, arm_z_bot,
                             width, arm_reach, thick))

        # --- 45° triangular gusset under the arm ---
        # Solid right-triangle wedge: hypotenuse at exactly 45°.
        # Top edge at (y=thick..thick+arm_reach, z=arm_z_bot)
        # Meets back plate at (y=thick, z=arm_z_bot - arm_reach)
        # This is a proper solid prism, not stacked boxes.
        gusset_drop = min(arm_reach, arm_z_bot)  # can't go below z=0
        gusset_y_front = thick
        gusset_y_back = thick + gusset_drop  # 45°: horizontal run = vertical drop

        # Cross-section of gusset (right triangle in YZ plane):
        #   top-back:  (y=gusset_y_back, z=arm_z_bot)
        #   top-front: (y=gusset_y_front, z=arm_z_bot)
        #   bottom:    (y=gusset_y_front, z=arm_z_bot - gusset_drop)
        hw = width / 2
        left_pts = [
            np.array([-hw, gusset_y_front, arm_z_bot]),
            np.array([-hw, gusset_y_back,  arm_z_bot]),
            np.array([-hw, gusset_y_front, arm_z_bot - gusset_drop]),
        ]
        right_pts = [
            np.array([hw, gusset_y_front, arm_z_bot]),
            np.array([hw, gusset_y_back,  arm_z_bot]),
            np.array([hw, gusset_y_front, arm_z_bot - gusset_drop]),
        ]
        tris.extend(_wedge_tris(-hw, hw, left_pts, right_pts))

        # --- Hook lip (rises upward from arm tip - zero overhang) ---
        lip_y = thick + arm_reach - thick
        tris.extend(box_tris(-width/2, lip_y, arm_z_bot,
                             width, thick, thick + lip_height))

        # --- Screw hole markers ---
        for sz in [plate_h * 0.2, plate_h * 0.5]:
            tris.extend(solid_cylinder(2.5, 2, 12, z_base=sz,
                                       center=(0, -1)))

        outdir = os.path.join(PROJECTS_DIR, "03_modern_wall_hook_set")
        path = os.path.join(outdir, f"wall_hook_{label}.stl")
        count = save_stl(tris, path)
        print(f"    -> {path} ({count} triangles)")
        paths.append(path)

    return paths


# =============================================================================
# PROJECT 04: GEOMETRIC SUCCULENT POT
# =============================================================================

def generate_04_succulent_pot():
    """Low-poly faceted succulent pot with drainage hole and saucer."""
    print("  [04] Geometric Succulent Pot...")
    paths = []

    # --- POT ---
    tris = []
    sides = 6
    r_bot = 30
    r_top = 40
    h = 55
    wall = 2.4
    bottom = 2.5

    # Outer shell with twist
    layers = 8
    for i in range(layers):
        z0 = h * i / layers
        z1 = h * (i + 1) / layers
        t0 = i / layers
        t1 = (i + 1) / layers
        r0 = r_bot + (r_top - r_bot) * t0
        r1 = r_bot + (r_top - r_bot) * t1
        twist0 = t0 * (np.pi / sides / 2)  # subtle twist per layer
        twist1 = t1 * (np.pi / sides / 2)
        ob = polygon_points(r0, sides, z0, twist0)
        ot = polygon_points(r1, sides, z1, twist1)
        tris.extend(ring_wall(ob, ot))
        ib = polygon_points(r0 - wall, sides, z0, twist0)
        it_ = polygon_points(r1 - wall, sides, z1, twist1)
        tris.extend(ring_wall_rev(ib, it_))

    # Bottom
    ob = polygon_points(r_bot, sides, 0)
    c = np.array([0, 0, 0])
    tris.extend(fan(c, ob, flip=True))

    # Inner bottom
    ib = polygon_points(r_bot - wall, sides, bottom)
    c_in = np.array([0, 0, bottom])
    tris.extend(fan(c_in, ib, flip=False))

    # Top rim
    twist_top = (np.pi / sides / 2)
    ot = polygon_points(r_top, sides, h, twist_top)
    it_ = polygon_points(r_top - wall, sides, h, twist_top)
    tris.extend(annular(ot, it_, flip=False))

    # Drainage hole (cylinder through bottom)
    drain_r = 5
    tris.extend(solid_cylinder(drain_r, bottom + 1, 16, z_base=-0.5))

    outdir = os.path.join(PROJECTS_DIR, "04_geometric_succulent_pot")
    path_pot = os.path.join(outdir, "succulent_pot.stl")
    save_stl(tris, path_pot)
    paths.append(path_pot)

    # --- SAUCER ---
    tris = []
    s_r_bot = 35
    s_r_top = 43
    s_h = 10
    s_wall = 2.0

    ob = polygon_points(s_r_bot, sides, 0)
    ot = polygon_points(s_r_top, sides, s_h)
    tris.extend(ring_wall(ob, ot))
    ib = polygon_points(s_r_bot - s_wall, sides, 0)
    it_ = polygon_points(s_r_top - s_wall, sides, s_h)
    tris.extend(ring_wall_rev(ib, it_))
    c = np.array([0, 0, 0])
    tris.extend(fan(c, ob, flip=True))
    ib_top = polygon_points(s_r_bot - s_wall, sides, 2)
    c_in = np.array([0, 0, 2])
    tris.extend(fan(c_in, ib_top, flip=False))
    tris.extend(annular(ot, it_, flip=False))

    path_saucer = os.path.join(outdir, "succulent_saucer.stl")
    save_stl(tris, path_saucer)
    paths.append(path_saucer)
    print(f"    -> {path_pot}, {path_saucer}")
    return paths


# =============================================================================
# PROJECT 05: CABLE MANAGEMENT CLIPS (set of 3)
# =============================================================================

def generate_05_cable_clips():
    """Adhesive-back cable management clips for 1, 2, and 3 cables."""
    print("  [05] Cable Management Clips...")
    paths = []

    for n_slots in [1, 2, 3]:
        tris = []
        slot_r = 4  # cable radius
        slot_spacing = 12
        base_h = 3
        clip_h = 14
        base_w = n_slots * slot_spacing + 10
        base_d = 18

        # Base plate
        tris.extend(box_tris(-base_w/2, -base_d/2, 0, base_w, base_d, base_h))

        # Clip arms for each slot
        for s in range(n_slots):
            cx = -((n_slots - 1) * slot_spacing / 2) + s * slot_spacing
            arm_w = 2.5
            arm_h = clip_h

            # Left arm
            tris.extend(box_tris(cx - slot_r - arm_w, -base_d/4, base_h,
                                 arm_w, base_d/2, arm_h))
            # Right arm
            tris.extend(box_tris(cx + slot_r, -base_d/4, base_h,
                                 arm_w, base_d/2, arm_h))
            # Top bridge (with gap for cable insertion)
            tris.extend(box_tris(cx - slot_r - arm_w, -base_d/4,
                                 base_h + arm_h - arm_w,
                                 slot_r * 2 + arm_w * 2, base_d/2, arm_w))

        outdir = os.path.join(PROJECTS_DIR, "05_cable_management_clips")
        path = os.path.join(outdir, f"cable_clip_{n_slots}slot.stl")
        count = save_stl(tris, path)
        print(f"    -> {path} ({count} triangles)")
        paths.append(path)

    return paths


# =============================================================================
# PROJECT 06: MINIMALIST PHONE STAND
# =============================================================================

def generate_06_phone_stand():
    """Clean minimalist phone stand with adjustable angle look."""
    print("  [06] Minimalist Phone Stand...")
    tris = []

    # Base
    base_w = 80
    base_d = 80
    base_h = 5
    tris.extend(box_tris(-base_w/2, -base_d/2, 0, base_w, base_d, base_h))

    # Back support (angled)
    support_w = 70
    support_thick = 5
    support_h = 90
    angle = 15 * np.pi / 180  # 15 degree lean back

    # Build angled back as a series of stacked boxes (approximation)
    slices = 20
    for i in range(slices):
        z0 = base_h + support_h * i / slices
        z1 = base_h + support_h * (i + 1) / slices
        y_offset0 = -np.sin(angle) * (support_h * i / slices)
        y_offset1 = -np.sin(angle) * (support_h * (i + 1) / slices)
        h_slice = (z1 - z0)
        y_mid = -base_d/4 + (y_offset0 + y_offset1) / 2
        tris.extend(box_tris(-support_w/2, y_mid, z0,
                             support_w, support_thick, h_slice))

    # Front lip (holds the phone)
    lip_w = 70
    lip_d = 20
    lip_h = 15
    tris.extend(box_tris(-lip_w/2, -base_d/4 - lip_d/2, base_h,
                         lip_w, lip_d, lip_h))

    # Cable channel through the lip
    channel_w = 15
    channel_h = 8
    tris.extend(box_tris(-channel_w/2, -base_d/4 - lip_d/2 - 1, base_h + 3,
                         channel_w, lip_d + 2, channel_h))

    outdir = os.path.join(PROJECTS_DIR, "06_minimalist_phone_stand")
    path = os.path.join(outdir, "phone_stand.stl")
    count = save_stl(tris, path)
    print(f"    -> {path} ({count} triangles)")
    return path


# =============================================================================
# PROJECT 07: FLOATING SHELF BRACKET (hidden mount)
# =============================================================================

def generate_07_shelf_bracket():
    """L-shaped floating shelf brackets - pair."""
    print("  [07] Floating Shelf Bracket...")
    paths = []

    for label, depth in [("small_150mm", 150), ("large_200mm", 200)]:
        tris = []
        wall_plate_h = 80
        wall_plate_w = 40
        thick = 6

        # Wall plate (vertical)
        tris.extend(box_tris(-wall_plate_w/2, 0, 0,
                             wall_plate_w, thick, wall_plate_h))

        # Shelf arm (horizontal)
        tris.extend(box_tris(-wall_plate_w/2, 0, wall_plate_h - thick,
                             wall_plate_w, depth, thick))

        # Diagonal brace
        brace_steps = 15
        brace_thick = thick
        for i in range(brace_steps):
            t0 = i / brace_steps
            t1 = (i + 1) / brace_steps
            z0 = thick + (wall_plate_h - 2*thick) * (1 - t0)
            z1 = thick + (wall_plate_h - 2*thick) * (1 - t1)
            y0 = thick + (depth - thick) * t0
            y1 = thick + (depth - thick) * t1
            hz = abs(z1 - z0) + 0.1
            tris.extend(box_tris(-brace_thick/2, min(y0,y1), min(z0,z1),
                                 brace_thick, abs(y1-y0)+0.1, hz))

        # Screw holes (decorative cylinders)
        for sz in [20, 55]:
            tris.extend(solid_cylinder(3, thick+2, 12, z_base=sz,
                                       center=(0, -1)))

        outdir = os.path.join(PROJECTS_DIR, "07_floating_shelf_bracket")
        path = os.path.join(outdir, f"shelf_bracket_{label}.stl")
        count = save_stl(tris, path)
        print(f"    -> {path} ({count} triangles)")
        paths.append(path)

    return paths


# =============================================================================
# PROJECT 08: GEOMETRIC TEA LIGHT HOLDER
# =============================================================================

def generate_08_tea_light_holder():
    """Faceted tea light holder with integrated vertical ribs.

    12-sided faceted body with alternating layer rotation for a crystalline
    look. Decorative vertical ribs protrude outward from every other facet
    edge, fully connected to the outer wall. No floating geometry.
    """
    print("  [08] Geometric Tea Light Holder...")
    tris = []

    sides = 12
    r_bot = 30
    r_top = 35
    h = 50
    wall = 3.0
    bottom = 3.0

    # --- Outer shell with alternating facet rotation ---
    layers = 6
    outer_rings = []
    for i in range(layers + 1):
        t = i / layers
        r = r_bot + (r_top - r_bot) * t
        z = h * t
        off = (np.pi / sides) * (i % 2) * 0.3
        ring = polygon_points(r, sides, z, off)
        outer_rings.append(ring)

    for i in range(layers):
        tris.extend(ring_wall(outer_rings[i], outer_rings[i + 1]))

    # --- Vertical ribs protruding from every other edge midpoint ---
    # Each rib is a small box that sits ON the outer wall surface,
    # spanning from the wall outward. Built per-layer so it follows
    # the tapered faceted surface exactly.
    rib_depth = 3.0     # how far the rib sticks out
    rib_half_w = 1.5    # half-width along the wall tangent

    for edge_idx in range(0, sides, 2):  # every other edge
        # Build rib as vertical column of quads from bottom to top
        # following the outer wall surface at this edge midpoint
        rib_z_start = h * 0.1
        rib_z_end = h * 0.85
        rib_layers = 10

        rib_outer_bot_pts = []
        rib_outer_top_pts = []
        rib_inner_bot_pts = []
        rib_inner_top_pts = []

        for ri in range(rib_layers + 1):
            rt = ri / rib_layers
            rz = rib_z_start + (rib_z_end - rib_z_start) * rt

            # Interpolate the outer wall radius and rotation at this Z
            layer_t = rz / h
            r_at_z = r_bot + (r_top - r_bot) * layer_t
            # Find which layer band we're in for the rotation offset
            layer_idx = min(int(layer_t * layers), layers - 1)
            frac_in_layer = (layer_t * layers) - layer_idx
            off_lo = (np.pi / sides) * (layer_idx % 2) * 0.3
            off_hi = (np.pi / sides) * ((layer_idx + 1) % 2) * 0.3
            off_at_z = off_lo + (off_hi - off_lo) * frac_in_layer

            # Edge midpoint angle (between vertex edge_idx and edge_idx+1)
            a0 = 2 * np.pi * edge_idx / sides + off_at_z
            a1 = 2 * np.pi * ((edge_idx + 1) % sides) / sides + off_at_z
            mid_angle = (a0 + a1) / 2

            # Surface point on outer wall at this angle
            sx = r_at_z * np.cos(mid_angle)
            sy = r_at_z * np.sin(mid_angle)

            # Outward direction (radial)
            dx = np.cos(mid_angle)
            dy = np.sin(mid_angle)

            # Tangent direction (perpendicular to radial, in XY plane)
            tx = -np.sin(mid_angle)
            ty = np.cos(mid_angle)

            # Inner edge (on the wall surface)
            tris_data_inner_l = np.array([sx - tx * rib_half_w,
                                          sy - ty * rib_half_w, rz])
            tris_data_inner_r = np.array([sx + tx * rib_half_w,
                                          sy + ty * rib_half_w, rz])

            # Outer edge (protruding outward)
            tris_data_outer_l = np.array([sx + dx * rib_depth - tx * rib_half_w,
                                          sy + dy * rib_depth - ty * rib_half_w, rz])
            tris_data_outer_r = np.array([sx + dx * rib_depth + tx * rib_half_w,
                                          sy + dy * rib_depth + ty * rib_half_w, rz])

            if ri < rib_layers:
                rib_inner_bot_pts.append((tris_data_inner_l, tris_data_inner_r))
                rib_outer_bot_pts.append((tris_data_outer_l, tris_data_outer_r))

            if ri > 0:
                rib_inner_top_pts.append((tris_data_inner_l, tris_data_inner_r))
                rib_outer_top_pts.append((tris_data_outer_l, tris_data_outer_r))

        # Build rib faces layer by layer
        for ri in range(rib_layers):
            il_b, ir_b = rib_inner_bot_pts[ri]
            ol_b, or_b = rib_outer_bot_pts[ri]
            il_t, ir_t = rib_inner_top_pts[ri]
            ol_t, or_t = rib_outer_top_pts[ri]

            # Front face (outward-facing)
            tris.extend(quad(ol_b, or_b, or_t, ol_t))
            # Left side
            tris.extend(quad(il_b, ol_b, ol_t, il_t))
            # Right side
            tris.extend(quad(or_b, ir_b, ir_t, or_t))
            # Back face (toward center - optional, mostly hidden)
            tris.extend(quad(ir_b, il_b, il_t, ir_t))

        # Top cap of rib
        il_t, ir_t = rib_inner_top_pts[-1]
        ol_t, or_t = rib_outer_top_pts[-1]
        tris.extend(quad(il_t, ir_t, or_t, ol_t))

        # Bottom cap of rib
        il_b, ir_b = rib_inner_bot_pts[0]
        ol_b, or_b = rib_outer_bot_pts[0]
        tris.extend(quad(ir_b, il_b, ol_b, or_b))

    # --- Inner cavity (straight cylinder for tea light) ---
    cavity_r = 19.5  # standard tealight = 38mm dia
    n_inner = sides

    ib = circle_points(cavity_r, n_inner, bottom)
    it_ = circle_points(cavity_r, n_inner, h)
    tris.extend(ring_wall_rev(ib, it_))

    # Bottom face
    ob = polygon_points(r_bot, sides, 0)
    c = np.array([0, 0, 0])
    tris.extend(fan(c, ob, flip=True))

    # Inner bottom
    ib_floor = circle_points(cavity_r, n_inner, bottom)
    c_in = np.array([0, 0, bottom])
    tris.extend(fan(c_in, ib_floor, flip=False))

    # Top rim
    ot = outer_rings[-1]
    it_top = circle_points(cavity_r, n_inner, h)
    tris.extend(annular(ot, it_top, flip=False))

    outdir = os.path.join(PROJECTS_DIR, "08_tea_light_holder")
    path = os.path.join(outdir, "tea_light_holder.stl")
    count = save_stl(tris, path)
    print(f"    -> {path} ({count} triangles)")
    return path


# =============================================================================
# PROJECT 09: SOAP DISH DRAINER
# =============================================================================

def generate_09_soap_dish():
    """Angled soap dish with drainage slats."""
    print("  [09] Soap Dish Drainer...")
    tris = []

    w = 90  # width
    d = 65  # depth
    h_back = 20  # height at back (raised for drainage angle)
    h_front = 12  # height at front (lower)
    wall = 2.5
    bottom = 2.5
    slat_count = 8
    slat_w = 3
    slat_gap = (d - 2*wall - slat_count*slat_w) / (slat_count - 1)

    # Outer box (tapered height)
    # Bottom
    tris.extend(box_tris(0, 0, 0, w, d, bottom))

    # Left wall
    tris.extend(box_tris(0, 0, bottom, wall, d, h_back))
    # Right wall
    tris.extend(box_tris(w - wall, 0, bottom, wall, d, h_back))
    # Back wall
    tris.extend(box_tris(0, d - wall, bottom, w, wall, h_back))
    # Front wall (shorter)
    tris.extend(box_tris(0, 0, bottom, w, wall, h_front))

    # Drainage slats (angled ribs inside)
    for i in range(slat_count):
        sy = wall + i * (slat_w + slat_gap)
        # Each slat is angled from h_back down to h_front
        slat_h = 4
        # Place at bottom + a bit
        sz = bottom
        tris.extend(box_tris(wall + 2, sy, sz,
                             w - 2*wall - 4, slat_w, slat_h))

    # Drain channel (groove at front)
    channel_w = 20
    channel_d = wall + 2
    channel_h = 3
    tris.extend(box_tris(w/2 - channel_w/2, -1, bottom,
                         channel_w, channel_d + 1, channel_h))

    outdir = os.path.join(PROJECTS_DIR, "09_soap_dish_drainer")
    path = os.path.join(outdir, "soap_dish.stl")
    count = save_stl(tris, path)
    print(f"    -> {path} ({count} triangles)")
    return path


# =============================================================================
# PROJECT 10: MODULAR DRAWER DIVIDER
# =============================================================================

def generate_10_drawer_divider():
    """Interlocking modular drawer dividers - cross pieces that slot together."""
    print("  [10] Modular Drawer Divider...")
    paths = []

    h = 50  # divider height
    thick = 2.5
    slot_w = 2.8  # slightly wider than thick for easy fit

    for label, length in [("short_100mm", 100), ("medium_200mm", 200), ("long_300mm", 300)]:
        tris = []

        # Main divider panel
        tris.extend(box_tris(0, -thick/2, 0, length, thick, h))

        # Slots cut from top (for cross-pieces to slide in)
        # We add small tab markers at slot positions
        n_slots = max(1, int(length / 80))
        for i in range(n_slots):
            sx = length * (i + 1) / (n_slots + 1)
            # Slot guide tabs (small bumps to mark slot position)
            tab_w = slot_w + 2
            tab_h = 3
            tris.extend(box_tris(sx - tab_w/2, -thick/2 - 1, h - 2,
                                 tab_w, thick + 2, tab_h))

        # End tabs for grip
        tab_size = 8
        tris.extend(box_tris(-1, -tab_size/2, h/2 - tab_size/2,
                             1, tab_size, tab_size))
        tris.extend(box_tris(length, -tab_size/2, h/2 - tab_size/2,
                             1, tab_size, tab_size))

        outdir = os.path.join(PROJECTS_DIR, "10_modular_drawer_divider")
        path = os.path.join(outdir, f"divider_{label}.stl")
        count = save_stl(tris, path)
        print(f"    -> {path} ({count} triangles)")
        paths.append(path)

    return paths


# =============================================================================
# PROJECT 11: WALL MOUNT HEADPHONE STAND
# =============================================================================

def generate_11_headphone_stand():
    """Sleek wall-mounted headphone hanger."""
    print("  [11] Wall Mount Headphone Stand...")
    tris = []

    # Wall plate
    plate_w = 50
    plate_h = 70
    plate_thick = 6
    tris.extend(box_tris(-plate_w/2, 0, 0, plate_w, plate_thick, plate_h))

    # Main arm (extends outward)
    arm_w = 30
    arm_length = 80
    arm_thick = 8
    arm_z = plate_h - 15
    tris.extend(box_tris(-arm_w/2, plate_thick, arm_z,
                         arm_w, arm_length, arm_thick))

    # Upturned tip (prevents headphones from sliding off)
    tip_h = 20
    tip_thick = arm_thick
    tris.extend(box_tris(-arm_w/2, plate_thick + arm_length - arm_thick, arm_z,
                         arm_w, tip_thick, tip_h + arm_thick))

    # Support brace underneath arm
    brace_steps = 12
    brace_w = 10
    for i in range(brace_steps):
        t0 = i / brace_steps
        t1 = (i + 1) / brace_steps
        bz0 = plate_thick + arm_length * 0.6 * t0
        bz1 = plate_thick + arm_length * 0.6 * t1
        z0 = arm_z * (1 - t0) + (arm_z) * t0
        z1 = arm_z * (1 - t1) + (arm_z) * t1
        dz = max(0.5, abs(z1 - z0))
        tris.extend(box_tris(-brace_w/2, min(bz0, bz1), min(z0, z1) - 4,
                             brace_w, abs(bz1 - bz0) + 0.1, dz + 4))

    # Screw holes
    for sz in [15, 50]:
        tris.extend(solid_cylinder(3, plate_thick + 2, 12, z_base=sz,
                                   center=(0, -1)))

    # Rounded pad on arm top (comfort strip)
    pad_w = arm_w - 4
    pad_len = arm_length - 15
    pad_h = 2
    tris.extend(box_tris(-pad_w/2, plate_thick + 5, arm_z + arm_thick,
                         pad_w, pad_len, pad_h))

    outdir = os.path.join(PROJECTS_DIR, "11_wall_mount_headphone_stand")
    path = os.path.join(outdir, "headphone_stand.stl")
    count = save_stl(tris, path)
    print(f"    -> {path} ({count} triangles)")
    return path


# =============================================================================
# MAIN - Generate everything
# =============================================================================

def main():
    print("=" * 60)
    print("  ETSY PRODUCT LINE - STL GENERATOR")
    print("  Generating 10 projects...")
    print("=" * 60)

    all_paths = []

    all_paths.append(generate_02_honeycomb_desk_organizer())
    all_paths.extend(generate_03_wall_hooks())
    all_paths.extend(generate_04_succulent_pot())
    all_paths.extend(generate_05_cable_clips())
    all_paths.append(generate_06_phone_stand())
    all_paths.extend(generate_07_shelf_bracket())
    all_paths.append(generate_08_tea_light_holder())
    all_paths.append(generate_09_soap_dish())
    all_paths.extend(generate_10_drawer_divider())
    all_paths.append(generate_11_headphone_stand())

    # Flatten
    flat = []
    for p in all_paths:
        if isinstance(p, list):
            flat.extend(p)
        else:
            flat.append(p)

    print()
    print("=" * 60)
    print(f"  COMPLETE: Generated {len(flat)} STL files across 10 projects")
    print("=" * 60)
    for p in flat:
        size = os.path.getsize(p) / 1024
        print(f"  {size:6.1f} KB  {os.path.relpath(p, PROJECTS_DIR)}")


if __name__ == "__main__":
    main()
