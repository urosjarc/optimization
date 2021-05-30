#version 460

uniform mat4 modelView;
uniform mat4 cameraView;
uniform mat4 normalView;
uniform mat4 screenView;

uniform vec3 in_light;
uniform float in_scaleRate;
uniform bool in_diffuse;

in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;

out vec4 ambient;
out float diffuse;

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
    vec4 light = vec4(in_light, 0);

    vec4 modelPosition = modelView * position;
    modelPosition.z = height_scalling(modelPosition.z, in_scaleRate);
    vec4 cameraModelPosition = cameraView * modelPosition;
    vec4 screenPosition = screenView * cameraModelPosition;

    vec4 cameraModelNormal = normalView * normal;
    vec4 lightDirection = light - cameraModelPosition;

    ambient = in_color;
    diffuse = in_diffuse ? 1 : abs(dot(normalize(cameraModelNormal.xyz), normalize(lightDirection.xyz)));

    gl_Position = screenPosition;
}
