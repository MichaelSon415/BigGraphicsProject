from OpenGL.GL import *
import numpy as np
import pygame
import ctypes


class Mesh3D:
    """
    Represents a 3D mesh using an OpenGL vertex buffer + attrib array to
    store the vertices and faces.
    """

    def __init__(self, vertices, faces, texture=None):
        self.vao = Mesh3D.get_vao(vertices, faces, texture)
        self.fcount = len(faces)
        if texture is not None:
            self.texture = Mesh3D.get_texture(texture)

    def draw(self, mode=GL_TRIANGLES):
        """
        Draws the mesh by binding its VAO and then triggering glDrawElements.
        """
        glBindVertexArray(self.vao)
        if self.texture is not None:
            glBindTexture(GL_TEXTURE_2D, self.texture)

        glDrawElements(mode, self.fcount, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    @staticmethod
    def get_texture(texture):
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image_data = pygame.image.tostring(texture, "RGB", True)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            texture.get_width(),
            texture.get_height(),
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            image_data,
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex

    @staticmethod
    def get_vao(vertices, faces, texture, usage="GL_STATIC_DRAW"):
        """
        Gets a Vertex Array Object for this mesh -- an encapsulation of the mesh's vertices
        and the indexes forming its triangle faces.
        """

        # Generate and bind a VAO for this mesh, so that all future calls are associated with this VAO.
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        # Generate and bind a buffer to hold the positions of the vertices.
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        
        # Each vertex has 12 bytes of data if there is no texture; otherwise it has 20.
        stride = 24 if texture is None else 32
        
        position_location = 0  
        glEnableVertexAttribArray(position_location)
        glVertexAttribPointer(
            position_location, 3, GL_FLOAT, False, stride, ctypes.c_void_p(0)
        )

        normal_location = 1
        glEnableVertexAttribArray(normal_location)
        glVertexAttribPointer(
            normal_location, 3, GL_FLOAT, False, stride, ctypes.c_void_p(12)
        )

        if texture is not None:
            texture_location = 2
            glEnableVertexAttribArray(texture_location)
            # Tell OpenGL that the texCorod of each vertex is 2 floats in size,
            # and is found by skipping 12 bytes at the start of the vertex.
            glVertexAttribPointer(
                texture_location, 2, GL_FLOAT, False, stride, ctypes.c_void_p(24)
            )

        # Specify the numpy array to use as the source of the vertex data.
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL_STATIC_DRAW)

        # Unbind this buffer so no one else messes with it.
        #glBindVertexArray(0)
        #glDisableVertexAttribArray(position_location)
        #glBindBuffer(GL_ARRAY_BUFFER, 0)
        #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        return vao

    @staticmethod
    def square():
        return Mesh3D(
            np.array(
                [
                    0.5,
                    -0.5,
                    0.5,
                    -0.5,
                    -0.5,
                    0.5,
                    0.5,
                    0.5,
                    0.5,
                    -0.5,
                    0.5,
                    0.5,
                    0.5,
                    0.5,
                    -0.5,
                    -0.5,
                    0.5,
                    -0.5,
                ],
                dtype="float32",
            ),
            np.array([[0, 2, 3], [0, 3, 1]], dtype="uint32"),
        )

    @staticmethod
    def cube():
        verts = [
            0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
        ]
        tris = [
            0,
            1,
            2,
            0,
            2,
            3,
            4,
            0,
            3,
            4,
            3,
            7,
            5,
            4,
            7,
            5,
            7,
            6,
            1,
            5,
            6,
            1,
            6,
            2,
            4,
            5,
            1,
            4,
            1,
            0,
            2,
            6,
            7,
            2,
            7,
            3,
        ]

        return Mesh3D(np.array(verts, "float32"), np.array(tris, "uint32"))

    @staticmethod
    def textured_triangle(texture):
        # fmt: off
        verts = [-0.5, -0.5, 0, 0, 0, 1, 0, 0, # x, y, z, nx, ny, nz, u, v
                 0, 0.5, 0, 0, 0, 1, 0.5, 1,
                 0.5, -0.5, 0, 0, 0, 1, 1, 0]
        tris = [0, 1, 2]
        return Mesh3D(np.array(verts, "float32"), 
                      np.array(tris, "uint32"), texture)
        # fmt: on

    @staticmethod
    # DEPRECATED.
    def load_obj(file) -> "Mesh3D":
        verts = []
        faces = []
        for line in file:
            if line[0] == "#":
                continue
            sp = line.split(" ")
            if line[0] == "v":
                verts.append(float(sp[1]))
                verts.append(float(sp[2]))
                verts.append(float(sp[3]))
            elif line[0] == "f":
                faces.append(int(sp[1]) - 1)
                faces.append(int(sp[2]) - 1)
                faces.append(int(sp[3]) - 1)
        return Mesh3D(np.array(verts, "float32"), 
                      np.array(faces, "uint32"))

    @staticmethod
    # DEPRECATED.
    def load_textured_obj(obj_file, texture) -> "Mesh3D":
        verts = []
        faces = []
        texcoords = []
        normals = []
        for line in obj_file:
            if line[0] == "#":
                continue

            sp = [x for x in line.split(" ") if x]
            if line.startswith("v "):
                verts.append(float(sp[1]))
                verts.append(float(sp[2]))
                verts.append(float(sp[3]))
            elif line.startswith("vt"):
                texcoords.append(float(sp[1]))
                texcoords.append(float(sp[2]))
            elif line.startswith("vn"):
                normals.append(float(sp[1]))
                normals.append(float(sp[2]))
                normals.append(float(sp[3]))
            elif line.startswith("f"):
                va, ta, na = sp[1].split("/")
                faces.append(int(va) - 1)
                faces.append(int(ta) - 1)
                faces.append(int(na) - 1)

                vb, tb, nb = sp[2].split("/")
                faces.append(int(vb) - 1)
                faces.append(int(tb) - 1)
                faces.append(int(nb) - 1)

                vc, tc, nc = sp[3].split("/")
                faces.append(int(vc) - 1)
                faces.append(int(tc) - 1)
                faces.append(int(nc) - 1)

        vertex_buffer = []
        # vertex_buffer will contain 5 values per vertex: x, y, z, nx, ny, nz, u, v
        # We are not using face normals for now.
        for i in range(0, len(verts), 3):
            vertex_buffer.append(verts[i])
            vertex_buffer.append(verts[i + 1])
            vertex_buffer.append(verts[i + 2])
            vertex_buffer.append(0)
            vertex_buffer.append(0)
            vertex_buffer.append(0)
            vertex_buffer.append(0)  # temporary u, v
            vertex_buffer.append(0)

        face_buffer = []
        # map from OBJ Vertex Index -> (map from OBJ Texture Index -> vertex_buffer index) 
        vertex_textures : dict[int, dict[tuple[int, int], int]] = {}
        
        for i in range(0, len(faces), 9):
            v1_index = faces[i]
            v2_index = faces[i + 3]
            v3_index = faces[i + 6]

            # Check to see if u, v don't match what we're already recorded for the vertices of
            # this face.
            # If they don't, we need to duplicate them.
            texindex_v1 = faces[i + 1]
            texindex_v2 = faces[i + 4]
            texindex_v3 = faces[i + 7]

            nrmindex_v1 = faces[i + 2]
            nrmindex_v2 = faces[i + 5]
            nrmindex_v3 = faces[i + 8]

            v1_texindexes = vertex_textures.setdefault(v1_index, {(texindex_v1, nrmindex_v1) : v1_index})
            v2_texindexes = vertex_textures.setdefault(v2_index, {(texindex_v2, nrmindex_v2) : v2_index})
            v3_texindexes = vertex_textures.setdefault(v3_index, {(texindex_v3, nrmindex_v3) : v3_index})

            # If we haven't seen this texindex for vertex 1 before, add a duplicate 
            # of vertex 1 to the vertex buffer, then record the new vertex buffer index
            # for vertex 1.
            if (texindex_v1, nrmindex_v1) not in v1_texindexes:
                vertex_buffer.append(vertex_buffer[v1_index * 8])
                vertex_buffer.append(vertex_buffer[v1_index * 8+1])
                vertex_buffer.append(vertex_buffer[v1_index * 8+2])
                vertex_buffer.append(normals[nrmindex_v1])
                vertex_buffer.append(normals[nrmindex_v1+1])
                vertex_buffer.append(normals[nrmindex_v1+2])
                vertex_buffer.append(texcoords[2 * texindex_v1])
                vertex_buffer.append(texcoords[2 * texindex_v1+1])
                v1_index = len(vertex_buffer)//8-1
                v1_texindexes[(texindex_v1, nrmindex_v1)] = v1_index
            else:
                v1_index = v1_texindexes[(texindex_v1, nrmindex_v1)]
                vertex_buffer[v1_index * 8 + 3] = normals[3 * nrmindex_v1]
                vertex_buffer[v1_index * 8 + 4] = normals[3 * nrmindex_v1 + 1]
                vertex_buffer[v1_index * 8 + 5] = normals[3 * nrmindex_v1 + 2]
                vertex_buffer[v1_index * 8 + 6] = texcoords[2 * texindex_v1]
                vertex_buffer[v1_index * 8 + 7] = texcoords[2 * texindex_v1 + 1]

            if (texindex_v2, nrmindex_v2) not in v2_texindexes:
                vertex_buffer.append(vertex_buffer[v2_index * 8])
                vertex_buffer.append(vertex_buffer[v2_index * 8+1])
                vertex_buffer.append(vertex_buffer[v2_index * 8+2])
                vertex_buffer.append(normals[nrmindex_v2])
                vertex_buffer.append(normals[nrmindex_v2+1])
                vertex_buffer.append(normals[nrmindex_v2+2])
                vertex_buffer.append(texcoords[2 * texindex_v2])
                vertex_buffer.append(texcoords[2 * texindex_v2+1])
                v2_index = len(vertex_buffer)//8-1
                v2_texindexes[(texindex_v2, nrmindex_v2)] = v2_index
            else:
                v2_index = v2_texindexes[(texindex_v2, nrmindex_v2)]
                vertex_buffer[v2_index * 8 + 3] = normals[3 * nrmindex_v2]
                vertex_buffer[v2_index * 8 + 4] = normals[3 * nrmindex_v2 + 1]
                vertex_buffer[v2_index * 8 + 5] = normals[3 * nrmindex_v2 + 2]
                vertex_buffer[v2_index * 8 + 6] = texcoords[2 * texindex_v2]
                vertex_buffer[v2_index * 8 + 7] = texcoords[2 * texindex_v2 + 1]
            
            if (texindex_v3, nrmindex_v3) not in v3_texindexes:
                vertex_buffer.append(vertex_buffer[v3_index * 8])
                vertex_buffer.append(vertex_buffer[v3_index * 8+1])
                vertex_buffer.append(vertex_buffer[v3_index * 8+2])
                vertex_buffer.append(normals[nrmindex_v3])
                vertex_buffer.append(normals[nrmindex_v3+1])
                vertex_buffer.append(normals[nrmindex_v3+2])
                vertex_buffer.append(texcoords[2 * texindex_v3])
                vertex_buffer.append(texcoords[2 * texindex_v3+1])
                v3_index = len(vertex_buffer)//8-1
                v3_texindexes[(texindex_v3, nrmindex_v3)] = v3_index
            else:
                v3_index = v3_texindexes[(texindex_v3, nrmindex_v3)]
                vertex_buffer[v3_index * 8 + 3] = normals[3 * nrmindex_v3]
                vertex_buffer[v3_index * 8 + 4] = normals[3 * nrmindex_v3 + 1]
                vertex_buffer[v3_index * 8 + 5] = normals[3 * nrmindex_v3 + 2]
                vertex_buffer[v3_index * 8 + 6] = texcoords[2 * texindex_v3]
                vertex_buffer[v3_index * 8 + 7] = texcoords[2 * texindex_v3 + 1]

            face_buffer.append(v1_index)
            face_buffer.append(v2_index)
            face_buffer.append(v3_index)

        return Mesh3D(
            np.array(vertex_buffer, "float32"), 
            np.array(face_buffer, "uint32"), texture
        )

    # Loads a Mesh object from assimp into a Mesh3D format compatible with our code.
    # The loaded Mesh must have normals and texture coordinates.
    @staticmethod
    def load_assimp_mesh(mesh_obj, texture):
        verts = mesh_obj.vertices
        norms = mesh_obj.normals
        texes = mesh_obj.texcoords[0]
        faces = mesh_obj.indices

        vertexbuffer = np.empty(mesh_obj.num_vertices * 8, dtype="float32")
        vnum = 0
        for i in range(0, len(vertexbuffer), 8):
            vertexbuffer[i] = verts[vnum][0]
            vertexbuffer[i+1] = verts[vnum][1]
            vertexbuffer[i+2] = verts[vnum][2]
            vertexbuffer[i+3] = norms[vnum][0]
            vertexbuffer[i+4] = norms[vnum][1]
            vertexbuffer[i+5] = norms[vnum][2]
            vertexbuffer[i+6] = texes[vnum][0]
            vertexbuffer[i+7] = texes[vnum][1]
            vnum += 1
            
        facebuffer = np.empty(len(faces) * 3, dtype="uint32")
        fnum = 0
        for i in range(0, len(facebuffer), 3):
            facebuffer[i] = faces[fnum][0]
            facebuffer[i+1] = faces[fnum][1]
            facebuffer[i+2] = faces[fnum][2]
            fnum += 1

        return Mesh3D(vertexbuffer, facebuffer, texture)