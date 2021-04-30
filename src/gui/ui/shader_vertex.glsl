#version 460

in vec3 in_position;
in vec4 in_color;

uniform mat4 viewMatrix;
uniform mat4 modelMatrix;
uniform mat4 projectionMatrix;

out lowp vec4 v_color;

void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(in_position, 1.0);
    v_color = in_color;
}