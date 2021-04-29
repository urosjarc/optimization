#version 460

in vec2 in_position;
in vec4 in_color;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

out lowp vec4 v_color;

void main()
{
    gl_Position = projectionMatrix * modelViewMatrix * vec4(in_position, 0.0, 1.0);
//    gl_Position = vec4(in_position, 0.0, 1.0);
    v_color = in_color;
}