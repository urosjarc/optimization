#version 460

uniform mat4 modelTranslationMatrix;
uniform mat4 modelScaleMatrix;
uniform mat4 modelRotationMatrix;

uniform mat4 worldScaleMatrix;
uniform mat4 worldRotationMatrix;
uniform mat4 worldTranslationMatrix;

uniform mat4 projectionMatrix;
uniform vec3 in_light;

in vec3 in_position;
in vec3 in_normal;
in vec4 in_color;

out vec4 ambient;
out float diffuse;

void main()
{
    vec3 normal = (worldRotationMatrix * modelRotationMatrix * vec4(in_normal, 0)).xyz;
    vec4 scaledPosition = worldScaleMatrix * modelRotationMatrix * modelScaleMatrix * modelTranslationMatrix * vec4(in_position, 1);
    vec4 world_position =  worldTranslationMatrix * worldRotationMatrix * scaledPosition;
    vec3 light_direction = normalize(in_light - world_position.xyz);


//    ambient = in_color;
//    ambient.z = scaledPosition.z;
//    ambient.y = 0;
//    ambient.x = 1-scaledPosition.z;

    ambient = in_color;
    diffuse = abs(dot(normal, light_direction));

    gl_Position = projectionMatrix * world_position;
}
