#version 460

in lowp vec4 v_color;
in lowp vec3 v_normal;

void main(void) {
    gl_FragColor = v_color;
}