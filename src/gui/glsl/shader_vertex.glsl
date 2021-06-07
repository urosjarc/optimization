#version 460

#include <colormap_shaders>

vec4 ambientColor = vec4(0.5, 0.5, 0.5, 1.0);
vec4 lightColor = vec4(0.7,0.7,0.7,1);

uniform mat4 modelView;
uniform mat4 cameraView;
uniform mat4 normalView;
uniform mat4 screenView;

uniform float in_scaleRate;
uniform vec3 in_lightPosition;
uniform uint in_colormap;
uniform bool in_inverseColormap;

uniform bool in_modelShading;
uniform uint in_modelColormap;
uniform bool in_modelScale;

in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;

out vec4 color;

float height_scalling(float x, float s){
    float b=0.5;
    float x0=1.5;
    float scale=2/(1+exp(-10*s))-1;
    float p=1-scale;
    return (2-2*p+b*(x+x0)*(3*p-4))/(2-3*p+4*b*(x+x0)*(p-1)) * 2 - 1.5;
}

void main() {
    vec4 position = vec4(in_position, 1);
    vec4 normal = vec4(in_normal, 0);
    vec4 light = vec4(in_lightPosition, 0);

    vec4 modelPosition = modelView * position;
    if(in_modelScale)
        modelPosition.z = height_scalling(modelPosition.z, in_scaleRate);

    vec4 cameraModelPosition = cameraView * modelPosition;
    vec4 screenPosition = screenView * cameraModelPosition;

    vec4 cameraModelNormal = normalView * normal;
    vec4 lightDirection = light - cameraModelPosition;

    vec4 colormap;
    vec4 colormap_inverse;
    #include <colormap_shaders_switch>

    float diffuseRate = 1;
    if(in_modelShading)
        diffuseRate = abs(dot(normalize(cameraModelNormal.xyz), normalize(lightDirection.xyz)));

    vec4 diffuseColor = diffuseRate * lightColor;

    vec4 surfaceColor;
    switch(in_modelColormap){
        case 0:
            surfaceColor = in_color;
            break;
        case 1:
            surfaceColor = colormap;
            break;
        case 2:
            surfaceColor = colormap_inverse;
            break;
    }

    color = (ambientColor + diffuseColor) * surfaceColor;
    gl_Position = screenPosition;
}
