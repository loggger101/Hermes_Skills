---
description: "Open3D 0.20.0 for point clouds and meshes from Python: install size, headless geometry/ICP/IO checks run live, and the silent-failure traps (missing file returns an empty cloud)"
source_repo: isl-org/Open3D (MIT)
tested_version: open3d 0.20.0 cp314 win_amd64 wheel, numpy 2.5.3, Windows, Python 3.14.6; geometry, registration and I/O only (no window, no GPU)
verified_date: "2026-10-05"
---

# Open3D (3D data processing)

Library for point clouds, triangle meshes, registration (ICP, global), KD-trees, TSDF/volumetric fusion, and a GUI/visualiser. Latest release v0.20.0 (2026-09-16).
`pip install open3d` has wheels for CPython 3.10-3.14 on Windows, Linux (x86_64, aarch64) and macOS arm64; the CUDA build is separate.

**Footprint:** the install is large. `pip install --target` of open3d plus dependencies took **488 MB** on disk; plan for it in venvs and CI caches. Import took 0.7 s.

## What was run (headless, CPU)

```python
import numpy as np, open3d as o3d
pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points_Nx3))     # numpy float64 in, float64 out
small = pcd.voxel_down_sample(0.1)
pcd.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=0.2, max_nn=30))
res = o3d.pipelines.registration.registration_icp(src, tgt, 0.5, np.eye(4),
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100))
res.transformation, res.fitness, res.inlier_rmse
```

| Check (4,000-point bumpy surface) | Result |
|---|---|
| `voxel_down_sample(0.1)` | 4,000 to 635 points |
| `estimate_normals` (hybrid radius 0.2, 30 neighbours) | `(4000, 3)` array; mean `abs(nz)` 0.855 (a mostly horizontal surface) |
| ICP point-to-point, target rotated 10 degrees about z plus a small translation, identity initial guess, max distance 0.5 | `fitness 1.000`, `rmse 2e-15`, max abs error of the recovered 4x4 vs the true transform `2.4e-15` |
| ICP with a 60 degree rotation from the identity | max abs transform error 0.09: it landed near but not exactly on the answer for this near-planar, symmetric-ish cloud. ICP is a **local** method: give it a good initial guess or run a global registration (FPFH + RANSAC) first |
| `KDTreeFlann.search_knn_vector_3d(p, 5)` | first neighbour is the query point itself (index 0, distance 0) |
| PLY write then read | 4,000 points back, max coordinate difference `0.0` |
| `TriangleMesh.create_sphere(1.0, resolution=20)` | 762 vertices, 1,520 triangles, watertight; `get_volume()` = 4.146 vs the true 4.189 (tessellation underestimates by about 1%) |
| `o3d.t.geometry.PointCloud` (tensor API) | `Float32` positions on `CPU:0`; `o3d.core.cuda.is_available()` was `False` (CPU wheel) |

## Traps

- **A missing file does not raise.** `o3d.io.read_point_cloud("nope.ply")` printed `RPly: Unable to open file` and `[Open3D WARNING] Read PLY failed` and returned an **empty cloud** (0 points). Check `len(pcd.points) > 0` (or `pcd.is_empty()`) after every read, and treat empty as an error in pipelines.
- The legacy API (`o3d.geometry.*`) holds float64; the tensor API (`o3d.t.geometry.*`, `o3d.core.Tensor`) is float32 by default and device-aware. Convert explicitly at the boundary and do not assume bit-identical results between them.
- Distances and radii are in the cloud's own units: voxel size, ICP max-correspondence distance and normal-search radius must be scaled to the data (an asteroid shape model in km needs different values than a scan in metres).
- `volume` and watertightness come from the mesh you give; a decimated or open mesh gives a wrong `get_volume()` (check `is_watertight()`).
- Visualisation (`o3d.visualization.draw_geometries`) needs a display and a GPU/OpenGL context; it was present as an API but not run here. For headless figures use offscreen rendering or export to PLY/OBJ and plot elsewhere.

## Where it fits

Use for scan or shape-model processing (downsample, denoise, normals, registration, meshing), e.g. aligning asteroid shape models or comparing a mesh to a point cloud.
Use `numpy`/`scipy.spatial.cKDTree` when you only need nearest neighbours, and avoid the 488 MB dependency for that.
