import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Mesh3D_normals import *
from Object3D_animated import *
from OpenGL.arrays import vbo
from numpy import array, empty
from OpenGL.GL import shaders
import os
import assimp_py

from RenderProgram import *
import time
import math


def load_obj(filename) -> Object3D:
    with open(filename) as f:
        return Object3D(Mesh3D.load_obj(f))

def mesh_to_object3d(mesh, scene, filename, texture_path):
    material = scene.materials[mesh.material_index]
    
    if texture_path is None:
        if mesh.material_index > 0 and len(material["TEXTURES"]) == 0:
            material = scene.materials[0]
            
        if mesh.material_index < 0 or len(material["TEXTURES"]) == 0:
            raise Exception("You must provide a texture_path because the OBJ file has no .mtl file, or there is no texture set in the .mtl file")
        
        # Load the texture information from the obj file's material file.
        textures = material["TEXTURES"][1]
        objpath = os.path.dirname(filename)
        texture_path = os.path.join(objpath, textures[0])

    obj = Object3D(
        Mesh3D.load_assimp_mesh(
            mesh, pygame.image.load(texture_path)
        )
    )

    return obj

def assimp_load_object(filename, texture_path=None, assimp_options = assimp_py.Process_Triangulate) -> Object3D:
    scene = assimp_py.ImportFile(filename, assimp_options)

    if len(scene.meshes) == 1:
        return mesh_to_object3d(scene.meshes[0], scene, filename, texture_path)
    
    root = Object3D(None)
    for mesh in scene.meshes:
        obj = mesh_to_object3d(mesh, scene, filename, texture_path)
        root.add_child(obj)
    return root
    


def load_shader_source(filename):
    with open(filename) as f:
        return f.read()
    
    
def get_program(vertex_source_filename, fragment_source_filename):
    vertex_shader = shaders.compileShader(
        load_shader_source(vertex_source_filename), GL_VERTEX_SHADER
    )
    fragment_shader = shaders.compileShader(
        load_shader_source(fragment_source_filename), GL_FRAGMENT_SHADER
    )
    return shaders.compileProgram(vertex_shader, fragment_shader)



if __name__ == "__main__":
    pygame.init()
    screen_width = 800
    screen_height = 800

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        DOUBLEBUF | OPENGL,
    )

    print(glGetString(GL_VERSION))

    pygame.display.set_caption("Solar System Sim")

    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 1 / AU

    def attraction(planet, other):
        other_x, other_z = (other.position[0] / SCALE), (other.position[2] / SCALE)
        distance_x = other_x - (planet.position[0] / SCALE)
        distance_z = other_z - (planet.position[2] / SCALE)
        distance = math.sqrt(distance_x ** 2 + distance_z ** 2)
        planet.distance_to_sun = distance
        force = G * planet.mass * other.mass / distance**2
        theta = math.atan2(distance_z, distance_x)
        force_x = math.cos(theta) * force
        force_z = math.sin(theta) * force
        return force_x, force_z

    # Sun
    sun = assimp_load_object("models/sun/Sun_1_1391000.obj", "models/sun/texture.png")
    sun.set_material(glm.vec4(10, 1, 0.1, 1))
    sun.move(glm.vec3(0, 0, -5))
    sun.grow(glm.vec3(1/3000, 1/3000, 1/3000))
    sun.radius = 30
    sun.mass = 1.98892 * 10**30

    # Mercury
    mercury = assimp_load_object("models/mercury/Mercury_1_4878.obj", "models/mercury/texture.png")
    mercury.set_material(glm.vec4(1, 1, 0.1, 1))
    mercury.move(glm.vec3(.387, 0, -5))
    mercury.grow(glm.vec3(1/6000, 1/6000, 1/6000))
    mercury.radius = 8
    mercury.mass = 3.30 * 10**23
    mercury.velocity[2] = -47.4 * 1000

    # Venus
    venus = assimp_load_object("models/venus/Venus_1_12103.obj", "models/venus/texture.png")
    venus.set_material(glm.vec4(1, 1, 0.1, 1))
    venus.move(glm.vec3(.723, 0, -5))
    venus.grow(glm.vec3(1/6000, 1/6000, 1/6000))
    venus.radius = 14
    venus.mass = 4.8686 * 10**24
    venus.velocity[2] = -35.02 * 1000

    # Earth
    earth = assimp_load_object("models/earth/Earth_1_12756.obj", "models/earth/texture.png")
    earth.set_material(glm.vec4(1, 1, 0.1, 1))
    earth.move(glm.vec3(1, 0, -5))
    #print(earth.position)
    earth.grow(glm.vec3(1/6000, 1/6000, 1/6000))
    earth.radius = 16
    earth.mass = 5.9742 * 10**24
    earth.velocity[2] = -29.783 * 1000

    # Mars
    mars = assimp_load_object("models/mars/Mars_1_6792.obj", "models/mars/texture.png")
    mars.set_material(glm.vec4(1, 1, 0.1, 1))
    mars.move(glm.vec3(1.524, 0, -5))
    mars.grow(glm.vec3(1/6000, 1/6000, 1/6000))
    mars.radius = 12
    mars.mass = 6.39 * 10**23
    mars.velocity[2] = -24.077 * 1000

    # UFO
    ufo = assimp_load_object("models/ufo/ufo.obj", "models/ufo/ufo.png") 
    ufo.set_material(glm.vec4(1, 1, 0.1, 1))
    ufo.move(glm.vec3(0, .25, -5))
    ufo.grow(glm.vec3(1/800, 1/800, 1/800))
    ufo_x_offset = 0
    ufo_z_offset = 0

    #light = Object3D(None)
    #light.position = glm.vec3(0, 0, 1)

    

    # Load the vertex and fragment shaders for this program.
    shader_lighting = get_program(
        "shaders/normal_perspective.vert", "shaders/specular_light.frag"
    )
    shader_nolighting = get_program(
        "shaders/normal_perspective.vert", "shaders/texture_mapped.frag"
    )
    renderer = RenderProgram()

    # Define the scene.
    cameraRotation = 0
    camera = glm.lookAt(glm.vec3(0, 1, 1), glm.vec3(0, 0, -5), glm.vec3(0, 1, 0))
    print(camera)
    perspective = glm.perspective(
        math.radians(30), screen_width / screen_height, 0.1, 100
    )

    ambient_color = glm.vec3(1, 1, 1)
    ambient_intensity = 0.1
    renderer.set_uniform("ambientColor", ambient_color * ambient_intensity, glm.vec3)
    renderer.set_uniform("pointPosition", sun.position, glm.vec3)
    renderer.set_uniform("pointColor", glm.vec3(1, 1, 1), glm.vec3)
    renderer.set_uniform("viewPos", glm.vec3(0, 0, 0), glm.vec3)
    renderer.set_uniform("ufoPosition", ufo.position, glm.vec3)
    
    # Point Lighting Constants
    renderer.set_uniform("pointLight.constant", 1.0, float)
    renderer.set_uniform("pointLight.linear", 0.35, float)
    renderer.set_uniform("pointLight.quadratic", 0.44, float)
    renderer.set_uniform("pointLight.position", sun.position, glm.vec3)

    # Spot Light Constants
    cos = math.cos(math.radians(12.5))
    outer = math.cos(math.radians(15))
    renderer.set_uniform("spotLight.position", ufo.position, glm.vec3)
    renderer.set_uniform("spotLight.direction", glm.vec3(0, -1, 0), glm.vec3)
    renderer.set_uniform("spotLight.constant", 1.0, float)
    renderer.set_uniform("spotLight.linear", 0.12, float)
    renderer.set_uniform("spotLight.quadratic", 0.05, float)
    renderer.set_uniform("spotLight.cutOff", cos, float)
    renderer.set_uniform("spotLight.outercutOff", outer, float)

    # Loop
    done = False
    frames = 0
    start = time.perf_counter()
    clock = pygame.time.Clock()
    tick_rate = 60

    # Only draw wireframes.
    glEnable(GL_DEPTH_TEST)
    keys_down = set()
    spin = False
    mercury_orbit_angle, venus_orbit_angle, earth_orbit_angle, mars_orbit_angle, ufo_orbit_angle = 0, 0, 0, 0, 0
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys_down.add(event.dict["key"])
            elif event.type == pygame.KEYUP:
                keys_down.remove(event.dict["key"])

        if pygame.K_UP in keys_down:
            #earth.rotate(glm.vec3(-0.001, 0, 0))
            #ufo.move(glm.vec3(0, 0.03, 0))
            ufo_z_offset -= .01
            renderer.set_uniform("spotLight.position", ufo.position, glm.vec3)
        elif pygame.K_DOWN in keys_down:
            #earth.rotate(glm.vec3(0.001, 0, 0))
            #ufo.move(glm.vec3(0, -0.03, 0))
            ufo_z_offset += .01
            renderer.set_uniform("spotLight.position", ufo.position, glm.vec3)
        if pygame.K_RIGHT in keys_down:
            #earth.rotate(glm.vec3(0, 0.001, 0))
            #ufo.move(glm.vec3(0.03, 0, 0))
            ufo_x_offset += .03
            renderer.set_uniform("spotLight.position", ufo.position, glm.vec3)
        elif pygame.K_LEFT in keys_down:
            #earth.rotate(glm.vec3(0, -0.001, 0))
            #ufo.move(glm.vec3(-0.03, 0, 0))
            ufo_x_offset -= .03
            renderer.set_uniform("spotLight.position", ufo.position, glm.vec3)
        if pygame.K_a in keys_down:
            sun.move(glm.vec3(-0.01, 0, 0))
            renderer.set_uniform("pointLight.position", sun.position, glm.vec3)
        elif pygame.K_d in keys_down:
            sun.move(glm.vec3(0.01, 0, 0))
            renderer.set_uniform("pointLight.position", sun.position, glm.vec3)
        if pygame.K_w in keys_down:
            sun.move(glm.vec3(0, 0, -0.01))
            renderer.set_uniform("pointLight.position", sun.position, glm.vec3)
        elif pygame.K_s in keys_down:
            sun.move(glm.vec3(0, 0, 0.01))
            renderer.set_uniform("pointLight.position", sun.position, glm.vec3)
        if pygame.K_z in keys_down:
            cameraRotation -= .02
        elif pygame.K_x in keys_down:
            cameraRotation -= .01
        elif pygame.K_c in keys_down:
            cameraRotation += .01
        elif pygame.K_v in keys_down:
            cameraRotation += .02
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        cameraLocationX = 6 * math.cos((3/3.14159) * cameraRotation)
        cameraLocationZ = 6 * math.sin((3/3.14159) * cameraRotation) - 5
        camera = glm.lookAt(glm.vec3(cameraLocationX, 1, cameraLocationZ), glm.vec3(0, 0, -5), glm.vec3(0, 1, 0))

        fx, fz = attraction(mercury, sun)
        mercury.velocity[0] += fx / mercury.mass * 86400
        mercury.velocity[2] += fz / mercury.mass * 86400
        mercury.position[0] += mercury.velocity[0] * 86400 * SCALE
        mercury.position[2] += mercury.velocity[2] * 86400 * SCALE
        #print(mercury.position)
        mercury.rotate(glm.vec3(0, .001, 0))

        fx, fz = attraction(venus, sun)
        venus.velocity[0] += fx / venus.mass * 86400
        venus.velocity[2] += fz / venus.mass * 86400
        venus.position[0] += venus.velocity[0] * 86400 * SCALE
        venus.position[2] += venus.velocity[2] * 86400 * SCALE
        #print(venus.position)
        venus.rotate(glm.vec3(0, .001, 0))

        fx, fz = attraction(earth, sun)
        earth.velocity[0] += fx / earth.mass * 86400
        earth.velocity[2] += fz / earth.mass * 86400
        earth.position[0] += earth.velocity[0] * 86400 * SCALE
        earth.position[2] += earth.velocity[2] * 86400 * SCALE
        #print(earth.position)
        earth.rotate(glm.vec3(0, .001, 0))

        ufo_orbit_angle += .1
        ufo_x = .05 * math.cos(ufo_orbit_angle)
        ufo_z = .05 * math.sin(ufo_orbit_angle)
        ufo.set_position(glm.vec3(earth.position[0] + ufo_x, .25, earth.position[2] + ufo_z))
        renderer.set_uniform("spotLight.position", ufo.position, glm.vec3)

        fx, fz = attraction(mars, sun)
        mars.velocity[0] += fx / mars.mass * 86400
        mars.velocity[2] += fz / mars.mass * 86400
        mars.position[0] += mars.velocity[0] * 86400 * SCALE
        mars.position[2] += mars.velocity[2] * 86400 * SCALE
        #print(mars.position)
        mars.rotate(glm.vec3(0, .001, 0))

        renderer.use_program(shader_lighting)
        renderer.render(perspective, camera, [sun, mercury, venus, earth, mars, ufo])
        renderer.use_program(shader_nolighting)
        renderer.render(perspective, camera, [sun])
        pygame.display.flip()
        end = time.perf_counter()
        frames += 1
        clock.tick(tick_rate)
        #print(frames / (end - start))

    pygame.quit()
