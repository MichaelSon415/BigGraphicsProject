#version 330
in vec3 Normal;
in vec2 TexCoord;
in vec3 FragPos;

// This is the proper way to set the color of the fragment, NOT using gl_FragColor.
layout (location=0) out vec4 FragColor;

uniform sampler2D ourTexture;
// Lighting parameters for ambient light, and a single point light w/ no attenuation.
uniform vec3 ambientColor;
uniform vec3 pointPosition;
uniform vec3 pointColor;
uniform vec3 cameraPosition;

uniform float ambientCoefficient;
uniform float diffuseCoefficient;
uniform float specularCoefficient;
uniform float shiny;

uniform vec4 material;

void main() {
    
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(pointPosition - FragPos);  
    float cosineLight = max(dot(norm, lightDir), 0.0);
    

    // Compute the ambient and diffuse components.
    vec3 ambient = ambientColor * material[0];
    vec3 diffuse = pointColor * (cosineLight * material[1]);

    // Specular
    vec3 viewDir = cameraPosition - FragPos;
    vec3 reflectDir = reflect(-lightDir, norm);
    float cosine = dot(normalize(reflectDir), normalize(viewDir));
    vec3 specular = pow(max(cosine, 0), material[3]) * material[2] * pointColor;

    // Assemble the final fragment color.
    FragColor = vec4(diffuse + ambient + specular, 1) * texture(ourTexture, TexCoord);
}