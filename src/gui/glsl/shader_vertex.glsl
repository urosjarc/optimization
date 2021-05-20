#version 460

uniform mat4 modelView;
uniform mat4 cameraView;
uniform mat4 normalView;
uniform mat4 screenView;

uniform vec3 in_light;
uniform uint in_scaleHeight;

in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;

out vec4 ambient;
out float diffuse;

float logistic_scalling(float x, float k){
    float y0 = -1;
    float x0 = 0;
    float L = 2;
    return L/(1+exp(-k * (x-x0))) + y0;
}

void main() {
    vec4 position = vec4(in_position, 1);
    vec4 normal = vec4(in_normal, 0);
    vec4 light = vec4(in_light, 0);


    vec4 modelPosition = modelView * position;
    if(in_scaleHeight == 1){
        modelPosition.z = logistic_scalling(modelPosition.z, 10);
    }
    vec4 cameraModelPosition = cameraView * modelPosition;
    vec4 screenPosition = screenView * cameraModelPosition;

    vec4 cameraModelNormal = normalView * normal;
    vec4 lightDirection = light - cameraModelPosition;

    ambient = in_color;
    diffuse = abs(dot(normalize(cameraModelNormal.xyz), normalize(lightDirection.xyz)));
    gl_Position = screenPosition;
}
