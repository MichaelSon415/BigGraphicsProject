#version 330
in vec3 Normal;
in vec2 TexCoord;
in vec3 FragPos;

// This is the proper way to set the color of the fragment, NOT using gl_FragColor.
layout (location=0) out vec4 FragColor;

uniform sampler2D ourTexture;
// Lighting parameters for ambient light, and a single point light w/ no attenuation.

struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec4 specular;
};

struct SpotLight {
    vec3 position;
    vec3 direction;

    float cutOff;
    float outercutOff;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

uniform PointLight pointLight;
uniform SpotLight spotLight;
uniform vec3 ambientColor;
uniform vec3 pointPosition;
uniform vec3 pointColor;
uniform vec3 cameraPosition;
//uniform vec3 ufoPosition;

//uniform float constant;
//uniform float linear;
//uniform float quadratic;

//uniform vec3 position;
//uniform vec3 direction;
//uniform float cutOff;
//uniform float outercutOff;

uniform vec4 material;
vec3 CalcPointLight(float constant, float linear, float quadratic, vec3 lightDir, float cosineLight, vec3 reflectDir, float spec, vec3 ambientColor, vec3 pointColor, vec4 material, vec3 pointPosition);
vec3 CalcSpotLight (vec3 position, vec3 direction, float cutOff, vec3 lightDir, float cosineLight, vec3 reflectDir, float spec, vec3 ambientColor, vec3 pointColor, vec4 material, float constant, float linear, float quadratic, float outercutOff);

vec3 CalcPointLight(PointLight light, vec3 norm, vec3 FragPos, vec3 viewDir, vec3 ambientColor, vec3 pointColor) {
    vec3 lightDir = normalize(light.position - FragPos);
    float cosineLight = max(dot(norm, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(normalize(viewDir), normalize(reflectDir)), 0.0), material[3]);
    float distance = length(light.position - FragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    vec3 ambient = ambientColor * material[0];
    vec3 diffuse = pointColor * (cosineLight * material[1]);
    vec3 specular = spec * material[2] * pointColor;
    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
}

vec3 CalcSpotLight (SpotLight light, vec3 norm, vec3 FragPos, vec3 viewDir, vec3 ambientColor, vec3 pointColor) {

    vec3 lightDir = normalize(light.position - FragPos);
    float cosineLight = max(dot(norm, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(normalize(viewDir), normalize(reflectDir)), 0.0), material[3]);
    float distance = length(light.position - FragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = light.cutOff - light.outercutOff;
    float intensity = clamp((theta - light.outercutOff) / epsilon, 0.0, 1.0);
    vec3 ambient = ambientColor * material[0];
    vec3 diffuse = pointColor * (cosineLight * material[1]);
    vec3 specular = spec * material[2] * pointColor; 

    ambient *= attenuation * intensity;
    diffuse *= attenuation * intensity;
    specular *= attenuation * intensity;
    return (ambient + diffuse + specular);
} 

void main() {
    
    vec3 norm = normalize(Normal);
    //vec3 lightDir = normalize(pointPosition - FragPos);  
    //float cosineLight = max(dot(norm, lightDir), 0.0);
    

    // Compute the ambient and diffuse components.
    //vec3 ambient = ambientColor * material[0];
    //vec3 diffuse = pointColor * (cosineLight * material[1]);

    // Specular
    vec3 viewDir = cameraPosition - FragPos;
    //vec3 reflectDir = reflect(-lightDir, norm);
    //float cosine = dot(normalize(reflectDir), normalize(viewDir));
    //float spec = pow(max(cosine, 0), material[3]);
    //vec3 specular = spec * material[2] * pointColor;
    //vec3 result = CalcPointLight(constant, linear, quadratic, lightDir, cosineLight, reflectDir, spec, ambientColor, pointColor, material, pointPosition);
    //result += CalcSpotLight(position, direction, cutOff, lightDir, cosineLight, reflectDir, spec, ambientColor, pointColor, material, pointPosition, constant, linear, quadratic, outercutOff);
    //vec3 result = CalcSpotLight(spotLight, norm, FragPos, viewDir, ambientColor, pointColor);
    vec3 result = CalcPointLight(pointLight, norm, FragPos, viewDir, ambientColor, pointColor);
    result += CalcSpotLight(spotLight, norm, FragPos, viewDir, ambientColor, pointColor);
    //result += CalcSpotLight(position, direction, cutOff, lightDir, cosineLight, reflectDir, spec, ambientColor, pointColor, material);
    // Point Lighting
    //float distance = length(pointPosition - FragPos);
    //float attenuation = 1.0 / (constant + linear * distance + quadratic *(distance * distance));

    //ambient *= attenuation;
    //diffuse *= attenuation;
    //specular *= attenuation;
    // Assemble the final fragment color.
    FragColor = vec4(result, 1) * texture(ourTexture, TexCoord);
}