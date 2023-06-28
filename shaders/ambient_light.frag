#version 330
in vec2 TexCoord;
layout (location=0) out vec4 FragColor;

uniform sampler2D ourTexture;
uniform vec3 ambientColor;
void main() {
    vec3 ambient = ambientColor;
    FragColor = vec4(ambient, 1) * texture(ourTexture, TexCoord);
}