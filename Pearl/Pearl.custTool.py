
import bpy # type: ignore
import bmesh # type: ignore
from mathutils import Vector, Matrix # type: ignore
import math
import random

class ForkCustomTools:
    """
    A class containing custom tools for the Fork 3D modeling software.
    """

    @staticmethod
    def create_spiral(context, segments=64, revolutions=2, radius=1, height=2):
        """
        Creates a spiral object in the 3D viewport.

        Args:
            context (bpy.context): The current context.
            segments (int): Number of segments in the spiral.
            revolutions (float): Number of revolutions in the spiral.
            radius (float): Radius of the spiral.
            height (float): Height of the spiral.

        Returns:
            bpy.types.Object: The created spiral object.
        """
        # Create a new mesh and a new object
        mesh = bpy.data.meshes.new(name="Spiral")
        obj = bpy.data.objects.new("Spiral", mesh)

        # Link the object to the scene
        bpy.context.collection.objects.link(obj)

        # Create a new BMesh
        bm = bmesh.new()

        # Calculate points along the spiral
        for i in range(segments + 1):
            t = i / segments
            angle = t * revolutions * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = height * t
            bm.verts.new((x, y, z))

        # Create edges between the vertices
        bm.verts.ensure_lookup_table()
        for i in range(len(bm.verts) - 1):
            bm.edges.new((bm.verts[i], bm.verts[i+1]))

        # Update the mesh with the new data
        bm.to_mesh(mesh)
        bm.free()

        # Update the mesh
        mesh.update()

        return obj

    @staticmethod
    def create_fractal_landscape(context, size=10, iterations=5, roughness=0.5):
        """
        Creates a fractal landscape using the Diamond-Square algorithm.

        Args:
            context (bpy.context): The current context.
            size (int): Size of the landscape (must be a power of 2 plus 1).
            iterations (int): Number of iterations for the fractal generation.
            roughness (float): Roughness factor for the landscape.

        Returns:
            bpy.types.Object: The created landscape object.
        """
        # Ensure size is a power of 2 plus 1
        size = 2**int(math.log2(size-1)) + 1

        # Create a new mesh and a new object
        mesh = bpy.data.meshes.new(name="FractalLandscape")
        obj = bpy.data.objects.new("FractalLandscape", mesh)

        # Link the object to the scene
        bpy.context.collection.objects.link(obj)

        # Create a heightmap
        heightmap = [[0 for _ in range(size)] for _ in range(size)]

        # Initialize the corners
        heightmap[0][0] = random.uniform(0, 1)
        heightmap[0][size-1] = random.uniform(0, 1)
        heightmap[size-1][0] = random.uniform(0, 1)
        heightmap[size-1][size-1] = random.uniform(0, 1)

        # Perform Diamond-Square algorithm
        step = size - 1
        for i in range(iterations):
            half_step = step // 2

            # Diamond step
            for x in range(half_step, size, step):
                for y in range(half_step, size, step):
                    avg = (heightmap[x-half_step][y-half_step] +
                           heightmap[x-half_step][y+half_step] +
                           heightmap[x+half_step][y-half_step] +
                           heightmap[x+half_step][y+half_step]) / 4
                    heightmap[x][y] = avg + random.uniform(-roughness, roughness)

            # Square step
            for x in range(0, size, half_step):
                for y in range((x + half_step) % step, size, step):
                    avg = (heightmap[(x-half_step)%size][y] +
                           heightmap[(x+half_step)%size][y] +
                           heightmap[x][(y-half_step)%size] +
                           heightmap[x][(y+half_step)%size]) / 4
                    heightmap[x][y] = avg + random.uniform(-roughness, roughness)

            step = half_step
            roughness *= 0.5

        # Create vertices and faces
        verts = []
        faces = []
        for x in range(size):
            for y in range(size):
                verts.append((x, y, heightmap[x][y]))

        for x in range(size - 1):
            for y in range(size - 1):
                i = x * size + y
                faces.append((i, i+1, i+size+1, i+size))

        # Create the mesh from vertices and faces
        mesh.from_pydata(verts, [], faces)

        # Update the mesh
        mesh.update()

        return obj

    @staticmethod
    def create_voronoi_sculpture(context, num_points=50, size=10, extrusion=1):
        """
        Creates a Voronoi diagram-based sculptural object.

        Args:
            context (bpy.context): The current context.
            num_points (int): Number of points to use for Voronoi diagram.
            size (float): Size of the base plane.
            extrusion (float): Maximum height of extrusion.

        Returns:
            bpy.types.Object: The created Voronoi sculpture object.
        """
        import scipy.spatial # type: ignore

        # Generate random points
        points = [(random.uniform(0, size), random.uniform(0, size)) for _ in range(num_points)]

        # Compute Voronoi diagram
        vor = scipy.spatial.Voronoi(points)

        # Create a new mesh and a new object
        mesh = bpy.data.meshes.new(name="VoronoiSculpture")
        obj = bpy.data.objects.new("VoronoiSculpture", mesh)

        # Link the object to the scene
        bpy.context.collection.objects.link(obj)

        # Create BMesh
        bm = bmesh.new()

        # Create vertices
        vert_lookup = {}
        for point in vor.vertices:
            vert = bm.verts.new((point[0], point[1], 0))
            vert_lookup[tuple(point)] = vert

        # Create faces
        for simplex in vor.ridge_vertices:
            if -1 not in simplex:
                face_verts = [vert_lookup[tuple(vor.vertices[i])] for i in simplex]
                bm.faces.new(face_verts)

        # Extrude faces
        for face in bm.faces:
            r = random.random()
            bmesh.ops.extrude_face_region(bm, geom=[face])
            bmesh.ops.translate(bm, vec=Vector((0, 0, r * extrusion)), verts=face.verts)

        # Update the mesh with the new data
        bm.to_mesh(mesh)
        bm.free()

        # Update the mesh
        mesh.update()

        return obj

    @staticmethod
    def create_l_system_tree(context, iterations=4, angle=25, length=1, scale=0.8):
        """
        Creates a tree-like structure using an L-system.

        Args:
            context (bpy.context): The current context.
            iterations (int): Number of iterations for the L-system.
            angle (float): Angle of branching in degrees.
            length (float): Initial length of branches.
            scale (float): Scale factor for branch length at each iteration.

        Returns:
            bpy.types.Object: The created L-system tree object.
        """
        def apply_rules(axiom):
            return axiom.replace("F", "FF+[+F-F-F]-[-F+F+F]")

        def create_tree_mesh(commands, angle, length):
            verts = [(0, 0, 0)]
            edges = []
            stack = []
            position = Vector((0, 0, 0))
            direction = Vector((0, 0, 1))
            
            for cmd in commands:
                if cmd == "F":
                    new_position = position + direction * length
                    verts.append(new_position[:])
                    edges.append((len(verts) - 2, len(verts) - 1))
                    position = new_position
                elif cmd == "+":
                    direction = Matrix.Rotation(math.radians(angle), 4, 'Y') @ direction
                elif cmd == "-":
                    direction = Matrix.Rotation(math.radians(-angle), 4, 'Y') @ direction
                elif cmd == "[":
                    stack.append((position.copy(), direction.copy(), length))
                elif cmd == "]":
                    position, direction, length = stack.pop()
                    verts.append(position[:])
            
            return verts, edges

        # Generate L-system string
        axiom = "F"
        for _ in range(iterations):
            axiom = apply_rules(axiom)

        # Create tree mesh
        verts, edges = create_tree_mesh(axiom, angle, length)

        # Create a new mesh and a new object
        mesh = bpy.data.meshes.new(name="LSystemTree")
        obj = bpy.data.objects.new("LSystemTree", mesh)

        # Link the object to the scene
        bpy.context.collection.objects.link(obj)

        # Create the mesh from verts and edges
        mesh.from_pydata(verts, edges, [])

        # Update the mesh
        mesh.update()

        return obj

    @staticmethod
    def create_geometric_pattern(context, rows=10, cols=10, size=0.1, gap=0.02, variation=0.5):
        """
        Creates a geometric pattern of various 3D shapes.

        Args:
            context (bpy.context): The current context.
            rows (int): Number of rows in the pattern.
            cols (int): Number of columns in the pattern.
            size (float): Base size of each shape.
            gap (float): Gap between shapes.
            variation (float): Variation in shape size and type.

        Returns:
            bpy.types.Object: The created geometric pattern object.
        """
        def create_cube(size):
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=size)
            return bm

        def create_sphere(size):
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=8, radius=size/2)
            return bm

        def create_cone(size):
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=size/2, radius2=0, depth=size)
            return bm

        # Create a new mesh and a new object
        mesh = bpy.data.meshes.new(name="GeometricPattern")
        obj = bpy.data.objects.new("GeometricPattern", mesh)

        # Link the object to the scene
        bpy.context.collection.objects.link(obj)

        # Create BMesh
        bm = bmesh.new()

        for row in range(rows):
            for col in range(cols):
                x = col * (size + gap)
                y = row * (size + gap)
                z = 0

                # Randomly choose shape and size
                shape_type = random.choice(['cube', 'sphere', 'cone'])
                shape_size = size * (1 + random.uniform(-variation, variation))

                if shape_type == 'cube':
                    shape_bm = create_cube(shape_size)
                elif shape_type == 'sphere':
                    shape_bm = create_sphere(shape_size)
                else:
                    shape_bm = create_cone(shape_size)

                # Move the shape to its position
                bmesh.ops.translate(shape_bm, verts=shape_bm.verts, vec=(x, y, z))

                # Join the shape to the main BMesh
                bmesh.ops.duplicate(shape_bm, geom=shape_bm.verts[:]+shape_bm.edges[:]+shape_bm.faces[:])
                bm.from_mesh(shape_bm.to_mesh())
                shape_bm.free()

        # Update the mesh with the new data
        bm.to_mesh(mesh)
        bm.free()

        # Update the mesh
        mesh.update()

        return obj

def register():
    """
    Register the custom tools with Fork.
    """
    bpy.utils.register_class(ForkCustomTools)

def unregister():
    """
    Unregister the custom tools from Fork.
    """
    bpy.utils.unregister_class(ForkCustomTools)

if __name__ == "__main__":
    register()
