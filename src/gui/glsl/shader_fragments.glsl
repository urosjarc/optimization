#version 460

in vec4 ambient;
in float diffuse;

void main(void) {
    gl_FragColor = ambient - vec4(1,1,1,1) * diffuse * 0.7;
}
