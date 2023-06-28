#version 330
layout (location=0) in vec4 vPosition;
void main() {
    // Don't move the vertex at all; assume its local space == clip space.
    gl_Position = vec4(vPosition.x * 5, vPosition.y * 5, vPosition.z *5, 1) ;
}