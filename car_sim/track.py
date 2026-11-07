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

LOGIC_TRACK = DEFAULT_TRACK.logic
OB_MASK = DEFAULT_TRACK.ob_mask
FINISH_LINE_MASK = DEFAULT_TRACK.finish_mask
FINISH_CENTER = DEFAULT_TRACK.finish_center
CP_MASKS = DEFAULT_TRACK.cp_masks
cp_gate_points = DEFAULT_TRACK.cp_points
CP1_MASK, CP2_MASK, CP3_MASK, CP4_MASK, CP5_MASK = CP_MASKS
cp1_cord, cp2_cord, cp3_cord, cp4_cord, cp5_cord = cp_gate_points
