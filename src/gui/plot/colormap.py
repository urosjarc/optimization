import os
from typing import List
from src import utils

class Colormap:
    def __init__(self, id, name, src, preview):
        self.id = id
        self.name = name
        self.src = src
        self.parsedSrc = None
        self.preview = preview

        self.__init()

    def __init(self):
        self.name = self.name.replace('-', '_').replace('+', '_')
        self.parsedSrc: str = self.src.replace('colormap', self.name)

def colormaps() -> List[Colormap]:
    colormaps = []
    shadersPath = utils.getPath(__file__, '../../../libs/colormap_shaders/glsl')

    id = 0
    for filePath in os.listdir(shadersPath):
        if filePath.endswith('.frag'):
            name = filePath.replace('.frag', '')
            preview = str(shadersPath.parent.joinpath('previews', f'{name}.png'))
            with open(f'{shadersPath}/{filePath}') as f:
                colormap = Colormap(id, name, f.read(), preview)
                colormaps.append(colormap)
            id += 1

    return sorted(colormaps, key=lambda cm: cm.id)
