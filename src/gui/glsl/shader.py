from typing import List

from src import utils
from src.gui.ui import config


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

def uiConfig():
    mapping = {
        'bool': 'bool',
        'list': 'vec3',
        'float': 'float',
        'int': 'int'
    }
    src = []
    for name, value in config.getAll().items():
        mapedType = mapping[type(value).__name__]
        src.append(f'uniform {mapedType} ui_{name};')
    return '\n'.join(src)


def vertexSrc() -> str:
    shaders = ""
    function = 'vec4 colormap(int i, z){\n'
    function += '    switch(i){\n'
    for i, cmap in enumerate(colormaps()):
        shaders += cmap.parsedSrc + "\n"
        function += f'''        case {cmap.id}:
            return {cmap.name}(z);
'''
    function += '        default:\n'
    function += '            return vec4(0,0,0,1);\n'
    function += '    }\n'
    function += '}'


    # Activate program and use it
    with open(utils.getPath(__file__, 'shader_vertex.glsl')) as f:
        src = f.read()
        src = src.replace("#include <colormap_shaders>", shaders)
        src = src.replace("#include <colormap_function>", function)
        src = src.replace("#include <ui_config>", uiConfig())
        with open('test.glsl', 'w') as f:
            f.write(src)
        return src

def fragmentSrc() -> str:
    with open(utils.getPath(__file__, 'shader_fragments.glsl')) as f:
        return f.read()
