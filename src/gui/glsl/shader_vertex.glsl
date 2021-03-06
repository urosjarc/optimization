#version 460

#include <colormap_shaders>
#include <colormap_function>

float height_scalling(float x, float s){
    float b=0.5;
    float x0=1.5;
    float scale=2/(1+exp(-10*s))-1;
    float p=1-scale;
    return (2-2*p+b*(x+x0)*(3*p-4))/(2-3*p+4*b*(x+x0)*(p-1)) * 2 - 1.5;
}

uniform uint type_model;
uniform mat4 view_model;
uniform mat4 view_camera;
uniform mat4 view_normal;
uniform mat4 view_screen;
in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;
out vec4 out_color;

#include <ui_config>
#include <model_types>

void main() {

    //Prepare variables
    vec4 position = vec4(in_position, 1);
    vec4 normal = vec4(in_normal, 1);
    vec4 light = vec4(ui_lightPosition, 0);
    vec4 ambientColor = vec4(vec3(ui_ambientRate), 1.0);
    vec4 lightColor = vec4(vec3(ui_lightRate), 1.0);

    //Fix initial model position
    vec4 model = view_model * position;

    /* HEIGHT SCALLING FOR EVAL POINTS AND LINES */
    if (ui_dimensionality < 3){
        switch (type_model){
            case FUNCTION_MODEL:
            model.z = height_scalling(model.z, ui_scaleRate);
            break;
            case EVAL_POINT_MODEL:
            model.z = height_scalling(model.z, ui_scaleRate);
            break;
            case EVAL_LINE_MODEL:
            model.z = height_scalling(model.z, ui_scaleRate);
            if (length(in_normal) != 0){ //If current point is end point **HACK**
                normal = view_model * normal;
                normal.z = height_scalling(normal.z, ui_scaleRate);
                model.z += ui_linesSize;
            }
            break;
        }
    }

    //Compute position and normal
    vec4 cameraModelPosition = view_camera * model;
    vec4 screenPosition = view_screen * cameraModelPosition;

    //Compute diffuse rate
    float diffuseRate = 1;
    if (type_model == FUNCTION_MODEL && ui_dimensionality == 2){// Shading if function
        vec4 cameraModelNormal = view_normal * normal;
        vec4 lightDirection = light - cameraModelPosition;
        diffuseRate = abs(dot(normalize(cameraModelNormal.xyz), normalize(lightDirection.xyz)));
    }

    //Compute colormap value
    float value = model.z + 0.5;
    if(ui_dimensionality == 3)
        value = normal.x;


    //Compute colormap
    vec4 surfaceColor = colormap(ui_colormap, value);
    switch (type_model){
        case EVAL_POINT_MODEL:
            surfaceColor = 1 - surfaceColor;
            surfaceColor.w = 1;
            break;
        case EVAL_LINE_MODEL:
            surfaceColor = 1 - surfaceColor;
            if (length(in_normal) != 0){
                value = normal.z+0.5;
                surfaceColor = 1-colormap(ui_colormap, value);
            }
            surfaceColor.w = 1;
            break;
        case FUNCTION_MODEL:
            if(ui_dimensionality == 3) surfaceColor.w = 1-smoothstep(0, ui_scaleRate, value);
            break;
        default :
            surfaceColor = in_color;
    }

    //Push values to fragment
    if (ui_dimensionality <= 2)
        out_color = (ambientColor + diffuseRate * lightColor) * surfaceColor;
    else{
        out_color = surfaceColor;
    }


    gl_Position = screenPosition;
}
