#version 460

in vec3 in_position;
in vec4 in_color;
in vec3 in_normal;

uniform mat4 viewMatrix;
uniform mat4 modelMatrix;
uniform mat4 projectionMatrix;

out lowp vec4 v_color;
out lowp vec3 v_normal;

void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(in_position, 1.0);
    v_color = in_color;
    v_normal = in_normal;
}