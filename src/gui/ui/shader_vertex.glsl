#version 100

attribute vec2 aVertexPosition;
attribute vec4 aVertexColor;

uniform mat4 uModelViewMatrix;
uniform mat4 uProjectionMatrix;

varying lowp vec4 vColor;

void main()
{
//    gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(aVertexPosition, 0.0, 1.0);
    gl_Position = vec4(aVertexPosition, 0.0, 1.0);
    vColor = aVertexColor;
}