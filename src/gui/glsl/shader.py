from typing import List
from OpenGL.GL import *

import numpy as np

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
        'bool': (np.uint32, 'bool', glUniform1ui),
        'list': (lambda v: np.array(v, dtype=np.float32), 'vec3', lambda n, v: glUniform3fv(n, 1, v)),
        'float': (np.float32, 'float', glUniform1f),
        'int': (np.int32, 'int', glUniform1i)
    }

    configDict = {}
    for name, value in config.getAll().items():
        toRawValue, mappedType, uniform = mapping[type(value).__name__]
        configDict[f'ui_{name}'] = {
            'type': mappedType,
            'value': toRawValue(value),
            'unimapFun': uniform
        }
    return configDict

def modelTypes():
    from src.gui.plot.model import MODEL
    src = ""
    for name, val in MODEL.__dict__.items():
        if not name.startswith('_'):
            val = MODEL.__getattr__(name).value
            src += f'const uint {name}_MODEL = {val};\n'

    return src

def vertexSrc() -> str:
    shaders = ""
    function = 'vec4 colormap(int i, float z){\n'
    function += '    switch(i){\n'
    for i, cmap in enumerate(colormaps()):
        shaders += cmap.parsedSrc + "\n"
        function += f'        case {cmap.id}:\n'
        function += f'            return {cmap.name}(z);\n'
    function += '        default:\n'
    function += '            return vec4(1,0,0,1);\n'
    function += '    }\n'
    function += '}'

    config = ''
    for name, conf in uiConfig().items():
        config += f'uniform {conf["type"]} {name}; // {conf["value"]}\n'

    # Activate program and use it
    with open(utils.getPath(__file__, 'shader_vertex.glsl')) as f:
        src = f.read()
        src = src.replace("#include <colormap_shaders>", shaders)
        src = src.replace("#include <colormap_function>", function)
        src = src.replace("#include <ui_config>", config)
        src = src.replace("#include <model_types>", modelTypes())
        with open('shader_vertex_compiled.glsl', 'w') as f:
            f.write(src)
        return src

def fragmentSrc() -> str:
    with open(utils.getPath(__file__, 'shader_fragments.glsl')) as f:
        return f.read()
