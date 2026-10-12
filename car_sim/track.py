import pygame
from env import scale_image

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
