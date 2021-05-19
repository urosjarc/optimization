#version 460

uniform mat4 positionView;
uniform mat4 normalView;
uniform mat4 projectionView;

uniform vec3 in_light;
uniform uint in_logHeight;

in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;

out vec4 ambient;
out float diffuse;

void main()
{
    vec3 position = in_position;
    if(in_logHeight == 1)
        position = vec3(in_position.xy, log2(in_position.z));

    vec4 worldPosition = positionView * vec4(position, 1);
    vec3 normal = (normalView * vec4(in_normal, 0)).xyz;
    vec3 lightDirection = in_light - worldPosition.xyz;

    ambient = in_color;
    diffuse = abs(dot(normalize(normal), normalize(lightDirection)));

    gl_Position = projectionView * worldPosition;
}
