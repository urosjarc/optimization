#version 460

float MATLAB_jet_red(float x) {
    if (x < 0.7) {
        return 4.0 * x - 1.5;
    } else {
        return -4.0 * x + 4.5;
    }
}

float MATLAB_jet_green(float x) {
    if (x < 0.5) {
        return 4.0 * x - 0.5;
    } else {
        return -4.0 * x + 3.5;
    }
}

float MATLAB_jet_blue(float x) {
    if (x < 0.3) {
       return 4.0 * x + 0.5;
    } else {
       return -4.0 * x + 2.5;
    }
}

vec4 MATLAB_jet(float x) {
    float r = clamp(MATLAB_jet_red(x), 0.0, 1.0);
    float g = clamp(MATLAB_jet_green(x), 0.0, 1.0);
    float b = clamp(MATLAB_jet_blue(x), 0.0, 1.0);
    return vec4(r, g, b, 1.0);
}

vec4 MATLAB_hot(float x) {
    float r = clamp(8.0 / 3.0 * x, 0.0, 1.0);
    float g = clamp(8.0 / 3.0 * x - 1.0, 0.0, 1.0);
    float b = clamp(4.0 * x - 3.0, 0.0, 1.0);
    return vec4(r, g, b, 1.0);
}

float MATLAB_bone_red(float x) {
    if (x < 0.75) {
        return 8.0 / 9.0 * x - (13.0 + 8.0 / 9.0) / 1000.0;
    } else {
        return (13.0 + 8.0 / 9.0) / 10.0 * x - (3.0 + 8.0 / 9.0) / 10.0;
    }
}

float MATLAB_bone_green(float x) {
    if (x <= 0.375) {
        return 8.0 / 9.0 * x - (13.0 + 8.0 / 9.0) / 1000.0;
    } else if (x <= 0.75) {
        return (1.0 + 2.0 / 9.0) * x - (13.0 + 8.0 / 9.0) / 100.0;
    } else {
        return 8.0 / 9.0 * x + 1.0 / 9.0;
    }
}

float MATLAB_bone_blue(float x) {
    if (x <= 0.375) {
        return (1.0 + 2.0 / 9.0) * x - (13.0 + 8.0 / 9.0) / 1000.0;
    } else {
        return 8.0 / 9.0 * x + 1.0 / 9.0;
    }
}

vec4 MATLAB_bone(float x) {
    float r = clamp(MATLAB_bone_red(x), 0.0, 1.0);
    float g = clamp(MATLAB_bone_green(x), 0.0, 1.0);
    float b = clamp(MATLAB_bone_blue(x), 0.0, 1.0);
    return vec4(r, g, b, 1.0);
}

vec4 transform_grayscale_banded(float x) {
    float v = cos(133.0 * x) * 28.0 + 230.0 * x + 27.0;
    if (v > 255.0) {
        v = 510.0 - v;
    }
    v = v / 255.0;
    return vec4(v, v, v, 1.0);
}

float transform_seismic_f(float x) {
    return ((-2010.0 * x + 2502.5950459) * x - 481.763180924) / 255.0;
}

float transform_seismic_red(float x) {
    if (x < 0.0) {
        return 3.0 / 255.0;
    } else if (x < 0.238) {
        return ((-1810.0 * x + 414.49) * x + 3.87702) / 255.0;
    } else if (x < 51611.0 / 108060.0) {
        return (344441250.0 / 323659.0 * x - 23422005.0 / 92474.0) / 255.0;
    } else if (x < 25851.0 / 34402.0) {
        return 1.0;
    } else if (x <= 1.0) {
        return (-688.04 * x + 772.02) / 255.0;
    } else {
        return 83.0 / 255.0;
    }
}

float transform_seismic_green(float x) {
    if (x < 0.0) {
        return 0.0;
    } else if (x < 0.238) {
        return 0.0;
    } else if (x < 51611.0 / 108060.0) {
        return transform_seismic_f(x);
    } else if (x < 0.739376978894039) {
        float xx = x - 51611.0 / 108060.0;
        return ((-914.74 * xx - 734.72) * xx + 255.) / 255.0;
    } else {
        return 0.0;
    }
}

float transform_seismic_blue(float x) {
    if (x < 0.0) {
        return 19.0 / 255.0;
    } else if (x < 0.238) {
        float xx = x - 0.238;
        return (((1624.6 * xx + 1191.4) * xx + 1180.2) * xx + 255.0) / 255.0;
    } else if (x < 51611.0 / 108060.0) {
        return 1.0;
    } else if (x < 174.5 / 256.0) {
        return (-951.67322673866 * x + 709.532730938451) / 255.0;
    } else if (x < 0.745745353439206) {
        return (-705.250074130877 * x + 559.620050530617) / 255.0;
    } else if (x <= 1.0) {
        return ((-399.29 * x + 655.71) * x - 233.25) / 255.0;
    } else {
        return 23.0 / 255.0;
    }
}

vec4 transform_seismic(float x) {
    return vec4(transform_seismic_red(x), transform_seismic_green(x), transform_seismic_blue(x), 1.0);
}

vec4 MATLAB_autumn(float x) {
    float g = clamp(x, 0.0, 1.0);
    return vec4(1.0, g, 0.0, 1.0);
}

vec4 MATLAB_summer(float x) {
    return vec4(clamp(x, 0.0, 1.0), clamp(0.5 * x + 0.5, 0.0, 1.0), 0.4, 1.0);
}

vec4 MATLAB_winter(float x) {
    return vec4(0.0, clamp(x, 0.0, 1.0), clamp(-0.5 * x + 1.0, 0.0, 1.0), 1.0);
}


vec4 colormap(int i, float z){
    switch(i){
        case 0:
            return MATLAB_jet(z);
        case 1:
            return MATLAB_hot(z);
        case 2:
            return MATLAB_bone(z);
        case 3:
            return transform_grayscale_banded(z);
        case 4:
            return transform_seismic(z);
        case 5:
            return MATLAB_autumn(z);
        case 6:
            return MATLAB_summer(z);
        case 7:
            return MATLAB_winter(z);
        default:
            return vec4(1,0,0,1);
    }
}

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

uniform bool ui_transperency; // 1
uniform bool ui_ortogonalView; // 0
uniform vec3 ui_lightPosition; // [ 10.  10. 100.]
uniform int ui_birdsEye; // 0
uniform float ui_scaleRate; // 0.0
uniform float ui_pointsSize; // 10.0
uniform float ui_ambientRate; // 0.5600000023841858
uniform float ui_lightRate; // 0.5
uniform float ui_linesSize; // 0.10000000149011612
uniform int ui_colormap; // 0
uniform bool ui_light; // 0
uniform int ui_dimensionality; // 2

const uint GENERIC_MODEL = 0;
const uint FUNCTION_MODEL = 1;
const uint AXIS_MODEL = 2;
const uint EVAL_POINT_MODEL = 3;
const uint EVAL_LINE_MODEL = 4;


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
            break;
        default :
            surfaceColor = in_color;
    }

    //Push values to fragment
    out_color = (ambientColor + diffuseRate * lightColor) * surfaceColor;
    gl_Position = screenPosition;
}
