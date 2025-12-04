# tests/test_entity_collision.py

import os
import sys

# Add the project root (the directory containing pyaquarium.py) to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pyaquarium import Entity  # this is your pyaquarium.py


def test_entity_collision_and_non_collision():
    # Two entities at the same position should collide
    e1 = Entity(x=0, y=0, art=["fish"], direction=1, color=0)
    e2 = Entity(x=0, y=0, art=["fish"], direction=1, color=0)

    assert e1.collides_with(e2)

    # An entity far to the right should NOT collide
    e3 = Entity(x=e1.width + 10, y=0, art=["fish"], direction=1, color=0)

    assert not e1.collides_with(e3)
