#version 330
// Vertex attributes: position, normal, texture coordinates.
layout (location=0) in vec3 vPosition;
layout (location=1) in vec3 vNormal;
layout (location=2) in vec2 vTexCoord;

// Matrices for model (local->world), view (world->view), 
// and projection (view->clip).
uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

// The outputs of the this shader: 
//   the world-space coordinate of this vertex, which will be interpolated as a fragment position.
//   the world-space normal vector of the vertex, which will also be interpolated.
//   the texture coordinates (u, v) of the vertex, ALSO will be interpolated.
out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

void main() {
    // Project the position to clip space.
    gl_Position = projection * view * model * vec4(vPosition, 1.0);

    // Compute FragPos and Normal in world space.
    FragPos = vec3(model * vec4(vPosition, 1.0));
    Normal = mat3(transpose(inverse(model))) * vNormal;  
    
    TexCoord = vTexCoord;
}