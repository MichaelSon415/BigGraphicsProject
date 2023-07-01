from OpenGL.GL import *
import glm
import math

# An object in 3D space, with a mesh, position, orientation (yaw/pitch/roll),
# and scale.
class Object3D:
    def __init__(
        self,
        mesh,
        position: glm.vec3 = None,
        orientation: glm.vec3 = None,
        scale: glm.vec3 = None,
        center: glm.vec3 = None,
        material: glm.vec4 = None
    ):
        self.mesh = mesh
        self.position = position or glm.vec3(0)
        self.orientation = orientation or glm.vec3(0)
        self.scale = scale or glm.vec3(1)
        self.center = center or glm.vec3(0)
        self.children : list[Object3D] = []
        self.velocity = glm.vec3(0)
        self.acceleration = glm.vec3(0)
        self.angular_velocity = glm.vec3(0)
        self.material = material or glm.vec4(1, 1, 1, 1)
        self.radius = 0
        self.mass = 0
        self.distance_to_sun = 0
        self._refresh_model_matrix()

   


    def set_position(self, position:glm.vec3):
        self.position = position
        self._refresh_model_matrix()

    def move(self, offset: glm.vec3):
        """
        Moves the object along the given vector.
        """
        self.position = self.position + offset
        self._refresh_model_matrix()

    def rotate(self, rot: glm.vec3):
        """
        Adds the given yaw,pitch,roll values to the object's current orientation.
        """
        self.orientation = self.orientation + rot
        self._refresh_model_matrix()

    def grow(self, sc: glm.vec3):
        """
        Multiplies the object's current scale by the given x,y,z scale values.
        """
        self.scale = self.scale * sc
        self._refresh_model_matrix()

    def center_point(self, center: glm.vec3):
        self.center = center
        self._refresh_model_matrix()

    def set_velocity(self, velocity: glm.vec3):
        self.velocity = glm.vec3(velocity)

    def set_acceleration(self, acceleration: glm.vec3):
        self.acceleration = glm.vec3(acceleration)

    def set_angular_velocity(self, angular_velocity: glm.vec3):
        self.angular_velocity = glm.vec3(angular_velocity)

    def get_position(self):
        return self.position
    
    def set_material(self, material: glm.vec4):
        self.material = material

    def get_model_matrix(self):
        """
        Retrieve the object's current Model transformation matrix.
        """
        return self.model_matrix

    def _refresh_model_matrix(self):
        m = glm.translate(glm.mat4(1), self.position)
        m = glm.translate(m, self.center * self.scale)
        m = glm.rotate(m, self.orientation[2], glm.vec3(0, 0, 1))
        m = glm.rotate(m, self.orientation[0], glm.vec3(1, 0, 0))
        m = glm.rotate(m, self.orientation[1], glm.vec3(0, 1, 0))
        m = glm.scale(m, self.scale)
        m = glm.translate(m, -self.center)

        self.model_matrix = m

    def tick(self, time_delta):
        self.velocity += self.acceleration * time_delta
        self.position += self.velocity * time_delta
        self.orientation += self.angular_velocity * time_delta
        self._refresh_model_matrix()

        for c in self.children:
            c.tick(time_delta)

    def add_child(self, child :"Object3D"):
        self.children.append(child)

    def draw(self, renderer):
        self.draw_recursive(glm.mat4(1), renderer)

    def draw_recursive(self, parent_matrix, renderer):
        combined = parent_matrix * self.model_matrix
        renderer.set_uniform("model", glm.value_ptr(combined), glm.mat4)
        renderer.start_program()
        if self.mesh is not None:
            self.mesh.draw()

        for c in self.children:
            c.draw_recursive(combined, renderer)
