import pygame
from types import SimpleNamespace
from .helper_functs import scale_image

# Colour thresholds, shared by every track
# OB in logic image is RED(255,0,0)
ob_color = pygame.Color(255,0,0)
threshold_target = (15,15,15,50)

# line in logic image is BLACK(0,0,0)
finish_line_color = pygame.Color(0,0,0)
threshold_line_target = (2,2,2,255)

cp_threshold_target = (15,15,15,50)

# Gate colours, in the order the car must pass them
CP_COLORS = [
    pygame.Color(0, 0, 255),
    pygame.Color(255, 255, 0),
    pygame.Color(0, 255, 255),
    pygame.Color(255, 255, 255),
    pygame.Color(255, 127, 39),
]

def load_track(logic_path, start_pos=(30, 630), start_angle=0):
    # build every mask for one logic image and bundle them together
    logic = scale_image(pygame.image.load(logic_path), 1)

    # Out of Bounds Mask
    ob_mask = pygame.mask.from_threshold(logic, ob_color, threshold_target)

    # Start/Finish Mask
    finish_mask = pygame.mask.from_threshold(logic, finish_line_color, threshold_line_target)

    # Checkpoints
    cp_masks = [pygame.mask.from_threshold(logic, c, cp_threshold_target) for c in CP_COLORS]
    cp_points = [m.centroid() for m in cp_masks]

    return SimpleNamespace(
        logic=logic,
        ob_mask=ob_mask,
        finish_mask=finish_mask,
        finish_center=finish_mask.centroid(),
        cp_masks=cp_masks,
        cp_points=cp_points,
        start_pos=start_pos,
        start_angle=start_angle,
    )

# Original (training) track. The old module-level names stay so other scripts keep working.
DEFAULT_TRACK = load_track("assets/tracks/logic_track1.png")
VISUAL_TRACK = scale_image(pygame.image.load("assets/tracks/visual_track1.png"), 1)

# Track 2 starting cord (98,554)

# Logic image path for each track id. Each logic image has a pixel-aligned visual_trackN.png.
# Tracks 3 and 4 are held out for testing; their files must exist before they are loaded.
TRACK_PATHS = {
    1: "assets/tracks/logic_track1.png",
    2: "assets/tracks/logic_track2.png",
    3: "assets/tracks/logic_track3.png",
    4: "assets/tracks/logic_track4.png",
}


# Fixed start pose per track: (start_pos, start_angle in degrees, 0 = up).
# No randomness, so every genome and every run sees the identical start.
START_POSES = {
    1: ((30, 630), 0),
    2: ((98, 554), 0),
    3: ((132, 542), 0),
    4: ((122, 511), 10),
}


def get_start_pose(track_id):
    if track_id not in START_POSES:
        raise ValueError(f"no start pose for track {track_id}; add it to START_POSES in track.py")
    return START_POSES[track_id]


def load_tracks(track_ids):
    # build one track object per id, in the order given
    tracks = []
    for track_id in track_ids:
        if track_id not in TRACK_PATHS:
            raise ValueError(f"unknown track id {track_id}; known ids: {sorted(TRACK_PATHS)}")
        start_pos, start_angle = get_start_pose(track_id)
        tracks.append(load_track(TRACK_PATHS[track_id], start_pos, start_angle))
    return tracks

LOGIC_TRACK = DEFAULT_TRACK.logic
OB_MASK = DEFAULT_TRACK.ob_mask
FINISH_LINE_MASK = DEFAULT_TRACK.finish_mask
FINISH_CENTER = DEFAULT_TRACK.finish_center
CP_MASKS = DEFAULT_TRACK.cp_masks
cp_gate_points = DEFAULT_TRACK.cp_points
CP1_MASK, CP2_MASK, CP3_MASK, CP4_MASK, CP5_MASK = CP_MASKS
cp1_cord, cp2_cord, cp3_cord, cp4_cord, cp5_cord = cp_gate_points
