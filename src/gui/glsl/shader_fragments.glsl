#version 460

in vec4 ambient;
in float diffuse;

void main(void) {
    gl_FragColor = ambient * diffuse;
}
