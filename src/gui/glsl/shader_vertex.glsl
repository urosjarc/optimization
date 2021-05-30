#version 460

uniform mat4 modelView;
uniform mat4 cameraView;
uniform mat4 normalView;
uniform mat4 screenView;

uniform float in_scaleRate;

uniform vec3 in_lightPosition;
uniform vec4 in_lightColor;

uniform bool in_shading;
uniform bool in_colormap;

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

float colormap_red(float x) {
    if (x < 0.7) {
        return 4.0 * x - 1.5;
    } else {
        return -4.0 * x + 4.5;
    }
}

float colormap_green(float x) {
    if (x < 0.5) {
        return 4.0 * x - 0.5;
    } else {
        return -4.0 * x + 3.5;
    }
}

float colormap_blue(float x) {
    if (x < 0.3) {
        return 4.0 * x + 0.5;
    } else {
        return -4.0 * x + 2.5;
    }
}

vec4 colormap(float x) {
    float r = clamp(colormap_red(x), 0.0, 1.0);
    float g = clamp(colormap_green(x), 0.0, 1.0);
    float b = clamp(colormap_blue(x), 0.0, 1.0);
    return vec4(r, g, b, 1.0);
}

void main() {
    vec4 position = vec4(in_position, 1);
    vec4 normal = vec4(in_normal, 0);
    vec4 light = vec4(in_lightPosition, 0);

    vec4 modelPosition = modelView * position;
    if(in_scaleRate > 0)
        modelPosition.z = height_scalling(modelPosition.z, in_scaleRate);
    vec4 cameraModelPosition = cameraView * modelPosition;
    vec4 screenPosition = screenView * cameraModelPosition;

    vec4 cameraModelNormal = normalView * normal;
    vec4 lightDirection = light - cameraModelPosition;

    vec4 lightColor = vec4(0.7,0.7,0.7,1);
    vec4 ambientColor = vec4(0.5, 0.5, 0.5, 1.0);

    vec4 surfaceColor = in_colormap ? colormap(modelPosition.z+0.5) : in_color;
    float diffuseRate = !in_shading ? 1: abs(dot(normalize(cameraModelNormal.xyz), normalize(lightDirection.xyz)));
    vec4 diffuseColor = diffuseRate * lightColor;

    color = (ambientColor + diffuseColor) * surfaceColor;
    gl_Position = screenPosition;
}
