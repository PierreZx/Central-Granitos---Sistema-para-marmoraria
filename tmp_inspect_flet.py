import flet as ft
import flet.canvas as cv
print('ft has Paint:', hasattr(ft,'Paint'))
print('cv has Paint:', hasattr(cv,'Paint'))
print('ft attrs:', [a for a in dir(ft) if 'Paint' in a or 'Painting' in a or 'Canvas' in a])
print('cv attrs filtered:', [a for a in dir(cv) if 'Paint' in a or 'Path' in a or 'Rect' in a or 'Text' in a])
