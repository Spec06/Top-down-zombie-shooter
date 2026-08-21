# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: python main_game.py
"""
3D Top-Down Zombie Looter Shooter
"""

import sys, math, random, ctypes
import numpy as np
import pygame
from pygame import mixer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

SCREEN_W, SCREEN_H = 1200, 800
FPS = 120
WORLD_HALF = 50.0

