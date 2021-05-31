import os
from src import utils

class Colormap:
    def __init__(self, name, src):
        self.name = name
        self.src = src
        self.parsedSrc = None

    def __init(self):
        for line in self.src:
            print(line)

def colormaps():
    previews = {}
    shaders = {}

    shadersPath = utils.getPath(__file__, '../../../libs/colormap_shaders/glsl')

    for filePath in os.listdir(shadersPath):
        if filePath.endswith('.frag'):
            name = filePath.replace('.frag', '')
            previews[name] = shadersPath.parent.joinpath('previews', f'{name}.png')
            with open(shadersPath.joinpath(filePath)) as f:
                shaders[name] = f.read()
    pass



if __name__ == '__main__':
    colormaps()
