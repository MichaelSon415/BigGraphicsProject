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
    # For Mac people.
    # pygame.display.gl_set_attribute(GL_CONTEXT_MAJOR_VERSION, 3)
    # pygame.display.gl_set_attribute(GL_CONTEXT_MINOR_VERSION, 3)
    # pygame.display.gl_set_attribute(GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
    # pygame.display.gl_set_attribute(GL_CONTEXT_PROFILE_COMPATIBILITY, GL_CONTEXT_PROFILE_CORE)

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        DOUBLEBUF | OPENGL,
    )

    print(glGetString(GL_VERSION))

    pygame.display.set_caption("Solar System Sim")

    # earth = load_textured_obj("models/bunny_textured.obj")

    # Sun
    sun = assimp_load_object("models/sun/Sun_1_1391000.obj", "models/sun/texture.png")
    sun.set_material(glm.vec4(1, 1, 0.1, 1))
    sun.move(glm.vec3(-1.5, 0, -5))
    sun.grow(glm.vec3(1/800, 1/800, 1/800))

    # Mercury
    mercury = assimp_load_object("models/mercury/Mercury_1_4878.obj", "models/mercury/texture.png")
    mercury.set_material(glm.vec4(1, 1, 0.1, 1))
    mercury.move(glm.vec3(-1, 1.25, -5))
    mercury.grow(glm.vec3(1/800, 1/800, 1/800))

    # Venus
    venus = assimp_load_object("models/venus/Venus_1_12103.obj", "models/venus/texture.png")
    venus.set_material(glm.vec4(1, 1, 0.1, 1))
    venus.move(glm.vec3(0, 0, -5))
    venus.grow(glm.vec3(1/800, 1/800, 1/800))

    # Earth
    earth = assimp_load_object("models/earth/Earth_1_12756.obj", "models/earth/texture.png")
    earth.set_material(glm.vec4(1, 1, 0.1, 1))
    earth.move(glm.vec3(1, 1.25, -5))
    earth.grow(glm.vec3(1/800, 1/800, 1/800))

    # Mars
    mars = assimp_load_object("models/mars/Mars_1_6792.obj", "models/mars/texture.png")
    mars.set_material(glm.vec4(1, 1, 0.1, 1))
    mars.move(glm.vec3(1.5, 0, -5))
    mars.grow(glm.vec3(1/800, 1/800, 1/800))

    # UFO
    ufo = assimp_load_object("models/ufo/UFO.obj", "models/ufo/UFO.png")
    ufo.set_material(glm.vec4(1, 1, 0.1, 1))
    ufo.move(glm.vec3(0, -1.5, -5))
    ufo.grow(glm.vec3(1/100, 1/100, 1/100))
    '''
    boat = assimp_load_object("models/boat/boat.fbx")
    #boat = assimp_load_object("models/backpack/backpack.obj", None, 
    #                          assimp_py.Process_Triangulate | assimp_py.Process_FlipUVs)
    boat.move(glm.vec3(-1, 0, -5))
    boat.grow(glm.vec3(0.5, 0.5, 0.5))
    boat.rotate(glm.vec3(math.pi/4, math.pi/2, math.pi/2))
    boat.set_material(glm.vec4(1, 1, 0.3, 1))
    '''

    light = Object3D(None)
    light.position = glm.vec3(0, 0, 1)

    

    # Load the vertex and fragment shaders for this program.
    shader_lighting = get_program(
        "shaders/normal_perspective.vert", "shaders/specular_light.frag"
    )
    shader_nolighting = get_program(
        "shaders/normal_perspective.vert", "shaders/texture_mapped.frag"
    )
    renderer = RenderProgram()

    # Define the scene.
    camera = glm.lookAt(glm.vec3(0, 0, 3), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    perspective = glm.perspective(
        math.radians(30), screen_width / screen_height, 0.1, 100
    )

    ambient_color = glm.vec3(1, 1, 1)
    ambient_intensity = 0.1
    renderer.set_uniform("ambientColor", ambient_color * ambient_intensity, glm.vec3)
    renderer.set_uniform("pointPosition", light.position, glm.vec3)
    renderer.set_uniform("pointColor", glm.vec3(1, 1, 1), glm.vec3)
    renderer.set_uniform("viewPos", glm.vec3(0, 0, 0), glm.vec3)

    # Loop
    done = False
    frames = 0
    start = time.perf_counter()

    # Only draw wireframes.
    glEnable(GL_DEPTH_TEST)
    keys_down = set()
    spin = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys_down.add(event.dict["key"])
            elif event.type == pygame.KEYUP:
                keys_down.remove(event.dict["key"])

        if pygame.K_UP in keys_down:
            earth.rotate(glm.vec3(-0.001, 0, 0))
        elif pygame.K_DOWN in keys_down:
            earth.rotate(glm.vec3(0.001, 0, 0))
        if pygame.K_RIGHT in keys_down:
            earth.rotate(glm.vec3(0, 0.001, 0))
        elif pygame.K_LEFT in keys_down:
            earth.rotate(glm.vec3(0, -0.001, 0))
        if pygame.K_a in keys_down:
            light.move(glm.vec3(-0.003, 0, 0))
            renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_d in keys_down:
            light.move(glm.vec3(0.003, 0, 0))
            renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_w in keys_down:
            light.move(glm.vec3(0, 0, -0.003))
            renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_s in keys_down:
            light.move(glm.vec3(0, 0, 0.003))
            renderer.set_uniform("pointPosition", light.position, glm.vec3)
        

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        renderer.use_program(shader_lighting)
        renderer.render(perspective, camera, [sun, mercury, venus, earth, mars, ufo])
        pygame.display.flip()
        end = time.perf_counter()
        frames += 1

    pygame.quit()
