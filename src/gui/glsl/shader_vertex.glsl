#version 460

uniform mat4 positionView;
uniform mat4 normalView;
uniform mat4 projectionView;

uniform vec3 in_light;
in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;

out vec4 ambient;
out float diffuse;

void main()
{
    vec4 position = positionView * vec4(in_position, 1);
    vec3 normal = (normalView * vec4(in_normal, 0)).xyz;
    vec3 lightDirection = in_light - position.xyz;

    ambient = in_color;
    diffuse = abs(dot(normalize(normal), normalize(lightDirection)));

    gl_Position = projectionView * position;
}
