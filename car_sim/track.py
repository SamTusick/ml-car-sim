import pygame
from .helper_functs import scale_image

LOGIC_TRACK = scale_image(pygame.image.load("assets/tracks/logic_track1.png"), 1)

# Out of Bounds Mask
# OB in logic image is RED(255,0,0)
ob_color = pygame.Color(255,0,0)
threshold_target = (15,15,15,50)

OB_MASK = pygame.mask.from_threshold(LOGIC_TRACK, ob_color, threshold_target)

# Start/Finish Mask
# line in logic image is BLACK(0,0,0)
finish_line_color = pygame.Color(0,0,0)
threshold_line_target = (2,2,2,255)

FINISH_LINE_MASK = pygame.mask.from_threshold(LOGIC_TRACK, finish_line_color, threshold_line_target)

# Checkpoints 
cp_threshold_target = (15,15,15,50)

cp1 = pygame.Color(0, 0, 255)
CP1_MASK = pygame.mask.from_threshold(LOGIC_TRACK, cp1, cp_threshold_target)

cp2 = pygame.Color(255, 255, 0)
CP2_MASK = pygame.mask.from_threshold(LOGIC_TRACK, cp2, cp_threshold_target)

cp3 = pygame.Color(0, 255, 255)
CP3_MASK = pygame.mask.from_threshold(LOGIC_TRACK, cp3, cp_threshold_target)

cp4 = pygame.Color(255, 255, 255)
CP4_MASK = pygame.mask.from_threshold(LOGIC_TRACK, cp4, cp_threshold_target)

cp5 = pygame.Color(255, 127, 39)
CP5_MASK = pygame.mask.from_threshold(LOGIC_TRACK, cp5, cp_threshold_target)

CP_MASKS = [CP1_MASK, CP2_MASK, CP3_MASK, CP4_MASK, CP5_MASK]

