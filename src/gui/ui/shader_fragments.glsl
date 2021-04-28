#version 100

varying lowp vec4 vColor;

void main(void) {
    gl_FragColor = vColor;
}