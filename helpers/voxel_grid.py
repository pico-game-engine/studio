"""Voxel grid data structure with greedy-meshed triangle export."""

from triangle3d import Triangle3D


_FACE_DEFS = {
    0: ('x', 'ix', 'iy', 'iz'),   # +x
    1: ('x', 'ix', 'iy', 'iz'),   # -x
    2: ('y', 'iy', 'ix', 'iz'),   # +y
    3: ('y', 'iy', 'ix', 'iz'),   # -y
    4: ('z', 'iz', 'ix', 'iy'),   # +z
    5: ('z', 'iz', 'ix', 'iy'),   # -z
}

class VoxelGrid:
    """3D voxel grid with paint operations and greedy-meshed triangle export."""

    def __init__(self, nx=24, ny=24, nz=24, voxel_size=0.1):
        """Create a grid of nx*ny*nz voxels with given world-space size."""
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.voxel_size = voxel_size
        self.grid = {}  # (x, y, z) -> int color
    
    def _greedy_merge_quads(self, quads, nx, ny, nz):
        """Merge adjacent same-axis quads into larger rectangles."""
        groups = {}
        for axis, ix, iy, iz in quads:
            _, fixed_axis, u_axis, v_axis = _FACE_DEFS[axis]
            fixed = {'ix': ix, 'iy': iy, 'iz': iz}[fixed_axis]
            u = {'ix': ix, 'iy': iy, 'iz': iz}[u_axis]
            v = {'ix': ix, 'iy': iy, 'iz': iz}[v_axis]
            key = (axis, fixed)
            groups.setdefault(key, set()).add((u, v))

        merged = []
        for (axis, fixed), cells in groups.items():
            _, _, u_axis, v_axis = _FACE_DEFS[axis]
            max_u = {'ix': nx, 'iy': ny, 'iz': nz}[u_axis]
            max_v = {'ix': nx, 'iy': ny, 'iz': nz}[v_axis]
            occupied = [[False] * max_v for _ in range(max_u)]
            for u, v in cells:
                occupied[u][v] = True

            for u in range(max_u):
                for v in range(max_v):
                    if not occupied[u][v]:
                        continue
                    v_end = v
                    while v_end + 1 < max_v and occupied[u][v_end + 1]:
                        v_end += 1
                    u_end = u
                    can_expand = True
                    while can_expand and u_end + 1 < max_u:
                        for vv in range(v, v_end + 1):
                            if not occupied[u_end + 1][vv]:
                                can_expand = False
                                break
                        if can_expand:
                            u_end += 1
                    for uu in range(u, u_end + 1):
                        for vv in range(v, v_end + 1):
                            occupied[uu][vv] = False
                    merged.append((axis, u, u_end, v, v_end, fixed))

        return merged
    
    def _quad_to_tris(self, axis, u0, u1, v0, v1, fixed, min_x, min_y, min_z, vx, vy, vz, color):
        """Convert a merged quad into two world-space triangles."""
        def world(ax, fv, uv, vv):
            if ax == 0:
                return (min_x + (fv + 1) * vx, min_y + uv * vy, min_z + vv * vz)
            elif ax == 1:
                return (min_x + fv * vx, min_y + uv * vy, min_z + vv * vz)
            elif ax == 2:
                return (min_x + uv * vx, min_y + (fv + 1) * vy, min_z + vv * vz)
            elif ax == 3:
                return (min_x + uv * vx, min_y + fv * vy, min_z + vv * vz)
            elif ax == 4:
                return (min_x + uv * vx, min_y + vv * vy, min_z + (fv + 1) * vz)
            else:
                return (min_x + uv * vx, min_y + vv * vy, min_z + fv * vz)

        p00 = world(axis, fixed, u0, v0)
        p10 = world(axis, fixed, u1 + 1, v0)
        p01 = world(axis, fixed, u0, v1 + 1)
        p11 = world(axis, fixed, u1 + 1, v1 + 1)

        tris = []
        if axis in (0, 2, 4):
            tris.append(Triangle3D(*p00, *p10, *p11, color))
            tris.append(Triangle3D(*p00, *p11, *p01, color))
        else:
            tris.append(Triangle3D(*p10, *p00, *p01, color))
            tris.append(Triangle3D(*p10, *p01, *p11, color))
        return tris

    def set(self, x, y, z, color):
        """Place a voxel at grid position with given color."""
        if 0 <= x < self.nx and 0 <= y < self.ny and 0 <= z < self.nz:
            self.grid[(x, y, z)] = color

    def get(self, x, y, z):
        """Return voxel color or None if empty."""
        return self.grid.get((x, y, z))

    def erase(self, x, y, z):
        """Remove voxel at position."""
        self.grid.pop((x, y, z), None)

    def clear(self):
        """Remove all voxels."""
        self.grid.clear()

    def voxel_count(self):
        """Return number of placed voxels."""
        return len(self.grid)

    def to_triangles(self, center_xz=True):
        """Convert voxels to a list of Triangle3D using greedy meshing per color.
        If center_xz is True, offset so the sprite is centered at X=0, Z=0."""
        if not self.grid:
            return []

        # Compute centering offset
        off_x = 0.0
        off_z = 0.0
        if center_xz and self.grid:
            xs = [p[0] for p in self.grid]
            zs = [p[2] for p in self.grid]
            cx = (min(xs) + max(xs) + 1) * self.voxel_size * 0.5
            cz = (min(zs) + max(zs) + 1) * self.voxel_size * 0.5
            off_x = -cx
            off_z = -cz

        # Group voxels by color
        color_sets = {}
        for (x, y, z), c in self.grid.items():
            color_sets.setdefault(c, set()).add((x, y, z))

        vx = vy = vz = self.voxel_size
        all_tris = []

        for color, voxels in color_sets.items():
            quads = []
            for (ix, iy, iz) in voxels:
                if (ix + 1, iy, iz) not in voxels:
                    quads.append((0, ix, iy, iz))
                if (ix - 1, iy, iz) not in voxels:
                    quads.append((1, ix, iy, iz))
                if (ix, iy + 1, iz) not in voxels:
                    quads.append((2, ix, iy, iz))
                if (ix, iy - 1, iz) not in voxels:
                    quads.append((3, ix, iy, iz))
                if (ix, iy, iz + 1) not in voxels:
                    quads.append((4, ix, iy, iz))
                if (ix, iy, iz - 1) not in voxels:
                    quads.append((5, ix, iy, iz))

            if not quads:
                continue

            merged = self._greedy_merge_quads(quads, self.nx, self.ny, self.nz)
            for axis, u0, u1, v0, v1, fixed in merged:
                tris = self._quad_to_tris(axis, u0, u1, v0, v1, fixed,
                                     off_x, 0.0, off_z, vx, vy, vz, color)
                all_tris.extend(tris)

        return all_tris

    def to_sprite3d(self, name='voxel_sprite'):
        """Export voxels to a Sprite3D object."""
        from sprite3d import Sprite3D
        sprite = Sprite3D()
        sprite.name = name
        sprite.type_str = 'VOXEL'
        for t in self.to_triangles():
            sprite.triangles.append(t)
        return sprite

    def get_bounds(self):
        """Return world-space AABB of the voxel grid."""
        if not self.grid:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        xs = [p[0] for p in self.grid]
        ys = [p[1] for p in self.grid]
        zs = [p[2] for p in self.grid]
        vs = self.voxel_size
        return (min(xs) * vs, min(ys) * vs, min(zs) * vs,
                (max(xs) + 1) * vs, (max(ys) + 1) * vs, (max(zs) + 1) * vs)
