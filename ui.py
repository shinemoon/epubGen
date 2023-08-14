# Work around for console-menu for remove bordres
from consolemenu.format import *

class EmptyBorderStyle(MenuBorderStyle):
    @property
    def bottom_left_corner(self): return ''
    @property
    def bottom_right_corner(self): return ''
    @property
    def inner_horizontal(self): return ''
    @property
    def inner_vertical(self): return ''
    @property
    def intersection(self): return ''
    @property
    def outer_horizontal(self): return ''
    @property
    def outer_horizontal_inner_down(self): return ''
    @property
    def outer_horizontal_inner_up(self): return ''
    @property
    def outer_vertical(self): return ''
    @property
    def outer_vertical_inner_left(self): return ''
    @property
    def outer_vertical_inner_right(self): return ''
    @property
    def top_left_corner(self): return ''
    @property
    def top_right_corner(self): return ''
