import os
from typing import List
from src import utils

class Colormap:
    @staticmethod
    def formatName(name):
        return name.replace('-', '_').replace('+', '_').replace('\n', '')

    def __init__(self, id, name, src, preview):
        self.id = id
        self.name = name
        self.src = src
        self.parsedSrc = None
        self.preview = preview

        self.__init()

    def __init(self):
        self.name = self.formatName(self.name)
        self.parsedSrc: str = self.src.replace('colormap', self.name)

def colormaps() -> List[Colormap]:
    shadersPath = utils.getPath(__file__, '../../../libs/colormap_shaders/glsl')

    with open(utils.getPath(__file__, '../../../data/colormap_shaders.txt')) as file:
        names = [Colormap.formatName(line) for line in file.readlines() if len(line) > 3]

    cmaps = []
    for i, name in enumerate(names):
        preview = str(shadersPath.parent.joinpath('previews', f'{name}.png'))
        with open(f'{shadersPath}/{name}.frag') as f:
            colormap = Colormap(i, name, f.read(), preview)
            cmaps.append(colormap)

    return cmaps
