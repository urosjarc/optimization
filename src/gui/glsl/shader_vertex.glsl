#version 460

#include <colormap_shaders>
#include <colormap_function>
#include <ui_config>

float height_scalling(float x, float s){
    float b=0.5;
    float x0=1.5;
    float scale=2/(1+exp(-10*s))-1;
    float p=1-scale;
    return (2-2*p+b*(x+x0)*(3*p-4))/(2-3*p+4*b*(x+x0)*(p-1)) * 2 - 1.5;
}

uniform mat4 view_model;
uniform mat4 view_camera;
uniform mat4 view_normal;
uniform mat4 view_screen;
in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;
out vec4 color;

void main() {

    //Prepare variables
    vec4 position = vec4(in_position, 1);
    vec4 normal = vec4(in_normal, 0);
    vec4 light = vec4(ui_lightPosition, 0);
    vec4 ambientColor = vec4(ui_ambientRate, ui_ambientRate, ui_ambientRate, 1.0);
    vec4 lightColor = vec4(ui_lightRate, ui_lightRate, ui_lightRate, 1.0);

    //Fix initial model position
    vec4 modelPosition = modelView * position;

    //Scale model axis
    if(in_modelScale != 0)
        modelPosition.z = height_scalling(modelPosition.z, in_scaleRate);
    if(in_modelScale == 2 && length(normal) != 0) //Increase line after chosing color for point.
        modelPosition.z += in_linesSize;

    //Compute position and normal
    vec4 cameraModelPosition = cameraView * modelPosition;
    vec4 screenPosition = screenView * cameraModelPosition;
    vec4 cameraModelNormal = normalView * normal;
    vec4 lightDirection = light - cameraModelPosition;

    //Compute diffuse rate
    float diffuseRate = 1;
    if(in_modelShading)
        diffuseRate = abs(dot(normalize(cameraModelNormal.xyz), normalize(lightDirection.xyz)));
    vec4 diffuseColor = diffuseRate * lightColor;

    //Compute colormap
    vec4 surfaceColor;
    switch (in_modelColormap){
        case 0:
            surfaceColor = in_color;
            break;
        case 1:
            surfaceColor = colormap;
            break;
        case 2:
            surfaceColor = 1 - colormap;
            break;
    }

    //Push values to fragment
    color = (ambientColor + diffuseColor) * surfaceColor;
    gl_Position = screenPosition;
}
