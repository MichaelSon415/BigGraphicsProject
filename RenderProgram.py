from OpenGL.GL import *
from Object3D_animated import Object3D
import glm


class RenderProgram:
    """
    Encapsulates a shader program (vertex + fragment shaders) and its bound
    uniform values. Can render a list of objects with a given projection and view matrix.
    """

    def __init__(self):
        self.uniforms = {}

    def use_program(self, program):
        self.shader_program = program
        glUseProgram(self.shader_program)

    def set_uniform(self, name:str, value, value_type):
        """
        Saves a value to assign to the given uniform name when the program runs.
        """
        self.uniforms[name] = (value, value_type)

    def start_program(self):
        glUseProgram(self.shader_program)
        for name in self.uniforms:
            value, value_type = self.uniforms[name]
            if value_type == glm.mat4:
                glUniformMatrix4fv(
                    glGetUniformLocation(self.shader_program, name),
                    1,
                    GL_FALSE,
                    value,
                )
            elif value_type == glm.vec4:
                glUniform4f(
                    glGetUniformLocation(self.shader_program, name),
                    value[0], value[1], value[2], value[3]
                )
            elif value_type == glm.vec3:
                glUniform3f(
                    glGetUniformLocation(self.shader_program, name),
                    value[0], value[1], value[2]
                )
            elif value_type == float:
                glUniform1f(
                    glGetUniformLocation(self.shader_program, name),
                    value
                )
            elif value_type == int:
                glUniform1i(
                    glGetUniformLocation(self.shader_program, name),
                    value
                )

    def render(
        self,
        projection_matrix: glm.mat4,
        view_matrix: glm.mat4,
        objects: list[Object3D],
    ):
        """
        Renders each of the given objects using the given projection and view matrices.
        """

        # Set uniform values for the projection and view matrices.
        self.set_uniform("projection", glm.value_ptr(projection_matrix), glm.mat4)
        self.set_uniform("view", glm.value_ptr(view_matrix), glm.mat4)

        # Iterate the list to draw.
        for o in objects:
            # Set uniform for this object's model matrix.
            self.set_uniform("model", glm.value_ptr(o.get_model_matrix()), glm.mat4)
            self.set_uniform("material", o.material, glm.vec4)
            #print(o.material[0],o.material[1], o.material[2], o.material[3])

            # Initialize the shader programs with the bound uniform values.
            self.start_program()
            # Draw the object.
            o.draw(self)
