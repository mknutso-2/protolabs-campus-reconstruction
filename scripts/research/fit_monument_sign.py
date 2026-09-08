"""Fit a vertical sign rectangle to manually interpreted official-image corners.

Requires NumPy/SciPy only for this optional research re-fit. The scene generator
consumes the committed JSON and needs neither package. Run from the repository:
    python3 scripts/research/fit_monument_sign.py
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
ANCHOR = np.array([94.39, -27.81])
CORNERS = np.array([[295, 680], [391, 652], [391, 715], [295, 740]], dtype=float)
ALTERNATE = np.array([[306, 677], [391, 653], [391, 715], [306, 739]], dtype=float)


def derive(root=ROOT):
    camera_path = root / 'research/reference_drone_camera_fit.json'
    terrain_path = root / 'research/terrain_grid.json'
    camera = json.loads(camera_path.read_text())
    terrain = json.loads(terrain_path.read_text())
    position = np.array(camera['position'])
    rotation = Rotation.from_euler('xyz', camera['rotation_euler_xyz_radians']).as_matrix()
    focal = camera['focal_length_pixels']

    def ground(x, y):
        tx, ty, tz = terrain['x'], terrain['y'], terrain['z']
        fx = max(0, min(len(tx)-1.001, (x-tx[0])/(tx[1]-tx[0])))
        fy = max(0, min(len(ty)-1.001, (y-ty[0])/(ty[1]-ty[0])))
        ix, iy = int(fx), int(fy)
        u, v = fx-ix, fy-iy
        return (tz[iy][ix]*(1-u)+tz[iy][ix+1]*u)*(1-v)+(tz[iy+1][ix]*(1-u)+tz[iy+1][ix+1]*u)*v

    def project(points):
        q = (np.array(points)-position) @ rotation
        return np.stack([600+focal*q[:, 0]/-q[:, 2], 400-focal*q[:, 1]/-q[:, 2]], axis=1)

    def corners(parameters):
        yaw, width, height, dx, dy, bottom = parameters
        x, y = ANCHOR + [dx, dy]
        center = [x, y, ground(x, y)+bottom+height/2]
        local = np.array([[-width/2, -.135, height/2], [width/2, -.135, height/2],
                          [width/2, -.135, -height/2], [-width/2, -.135, -height/2]])
        return local @ Rotation.from_euler('z', yaw).as_matrix().T + center

    def fit(pixels=CORNERS, free_xy=True, bottom=.10):
        def unpack(a):
            return [*a[:3], *(a[3:5] if free_xy else [0, 0]), bottom]
        def residual(a):
            p = unpack(a)
            # 2px fitting scale; left/bottom visual ambiguity is assessed below.
            image = ((project(corners(p))-pixels)/2).ravel()
            return np.r_[image, np.array(p[3:5])/.75] if free_xy else image
        initial = [math.pi/2, 4, 2.2] + ([0, 0] if free_xy else [])
        bounds = ([-.1, 2, .8] + ([-1.5, -1.5] if free_xy else []),
                  [math.pi, 9, 4] + ([1.5, 1.5] if free_xy else []))
        result = least_squares(residual, initial, bounds=bounds)
        p = unpack(result.x)
        predicted = project(corners(p))
        errors = np.linalg.norm(predicted-pixels, axis=1)
        x, y = ANCHOR + p[3:5]
        return {'yaw_degrees': math.degrees(p[0]), 'yaw_radians': p[0],
                'panel_width_m': p[1], 'panel_height_m': p[2], 'panel_depth_m': .27,
                'center_xy_m': [x, y], 'anchor_delta_xy_m': p[3:5],
                'anchor_displacement_m': float(np.linalg.norm(p[3:5])),
                'ground_z_m': ground(x, y), 'panel_bottom_above_ground_m': p[5],
                'panel_center_z_m': ground(x, y)+p[5]+p[2]/2,
                'corner_world_xyz_m': corners(p).tolist(),
                'projected_corners_px': predicted.tolist(),
                'corner_error_px': errors.tolist(),
                'corner_rms_px': float(np.sqrt(np.mean(errors**2)))}

    fitted = fit()
    rng = np.random.default_rng(20260907)
    trials = []
    for _ in range(128):
        jittered = CORNERS + rng.normal(size=(4, 2))*np.array([[3], [2], [5], [5]])
        trial = fit(jittered, bottom=float(rng.uniform(.05, .20)))
        trials.append([trial['yaw_degrees'], trial['panel_width_m'], trial['panel_height_m']])
    intervals = np.percentile(trials, [5, 95], axis=0)
    return {
        'schema_version': 1,
        'status': 'Bounded photo-based correction; not a surveyed sign specification',
        'reference': {
            'path': 'research/images/protolabs-official-hq-drone.jpg',
            'url': 'https://www.protolabs.com/media/s4dignhf/hq-drone.jpg',
            'attribution': 'Proto Labs, Inc.; undated public company photograph, acquired 2026-09-07',
            'sha256': hashlib.sha256((root/'research/images/protolabs-official-hq-drone.jpg').read_bytes()).hexdigest(),
            'size_px': [1200, 800], 'corner_order': ['top_left', 'top_right', 'bottom_right', 'bottom_left'],
            'annotated_panel_corners_px': CORNERS.tolist(),
            'annotation_uncertainty_px': [3, 2, 5, 5],
            'annotation_notes': [
                'Manual dark-panel interpretation, excluding gravel base. Lower corners are partly obscured by grass/shadow.',
                'The illuminated top edge begins near (295,680); continuous left dark boundary is near x295. The cyan logo begins around x307.',
                'An independent full-image reading placed the left front-plane edge near x306, possibly separating a side return. This unresolved interpretation is retained as an alternate fit.',
                'Numeric boundary support: median two-pixel RGB absolute change across y686..733 is 120 at x295 versus 15 at x306; this is an edge cue, not proof of front/side topology.'
            ]},
        'coordinate_system': 'Metres; X east, Y north, Z NAVD88 minus 303.6 m',
        'camera': {'path': 'research/reference_drone_camera_fit.json',
                   'sha256': hashlib.sha256(camera_path.read_bytes()).hexdigest(),
                   'position': camera['position'],
                   'rotation_euler_xyz_radians': camera['rotation_euler_xyz_radians'],
                   'lens_mm': camera['lens_mm'], 'sensor_width_mm': camera['sensor_width_mm'],
                   'focal_length_pixels': focal, 'held_fixed': True,
                   'original_landmark_rms_px_unweighted': camera['rmse_pixel_unweighted']},
        'terrain': {'path': 'research/terrain_grid.json', 'sha256': hashlib.sha256(terrain_path.read_bytes()).hexdigest(),
                    'method': 'Same bilinear sampling of the committed 5 m ground grid as build_scene.py'},
        'method': {'model': 'Vertical planar front rectangle; yaw only, width and height; depth retained at 0.27 m',
                   'objective': 'Eight image-coordinate residuals / 2 px, plus dx and dy / 0.75 m anchor prior',
                   'xy_anchor_m': ANCHOR.tolist(), 'xy_bounds_relative_to_anchor_m': [-1.5, 1.5],
                   'ground_constraint': 'Panel bottom 0.10 m above local ground; no independent camera-fit z=1.0 constraint',
                   'source_panel': {'width_m': 5.8, 'height_m': 2.75, 'depth_m': .27,
                                    'yaw_degrees': 0, 'center_xy_m': ANCHOR.tolist(),
                                    'center_z_above_ground_m': 1.5},
                   'reproduction': 'python3 scripts/research/fit_monument_sign.py (NumPy and SciPy required only for refitting)'},
        'fit': fitted,
        'fixed_xy_alternative': fit(free_xy=False),
        'alternate_left_edge': {'annotated_corners_px': ALTERNATE.tolist(), 'fit': fit(ALTERNATE)},
        'conditional_sensitivity': {'samples': 128, 'seed': 20260907,
             'method': 'Gaussian corner jitter at stated pixel scales and uniform 0.05..0.20 m panel-bottom clearance; camera and terrain grid held fixed',
             'percentiles': [5, 95], 'yaw_degrees': intervals[:, 0].tolist(),
             'panel_width_m': intervals[:, 1].tolist(), 'panel_height_m': intervals[:, 2].tolist(),
             'warning': 'These are conditional perturbation ranges, not confidence intervals for true dimensions; camera/datum and source-date errors are excluded'},
        'limitations': [
            'One photograph and an approximate fitted camera cannot uniquely establish physical dimensions, depth, or ground elevation.',
            'The 5 m ground grid does not resolve the monument foundation. Image edges are only a few pixels thick and lower corners blend into planting.',
            'Aerial XY is an approximate anchor; the nominal fit moves its center by less than half a metre.',
            'The old camera-fit monument center z=1.0 m was itself a manual approximation and is not an independent survey constraint.',
            'Yaw reverses the incorrect top-edge screen slope. Reduced foreshortening makes the sign wider in the image even though fitted physical width decreases.',
            'All existing lettering, logo parts and base share the same transform; no new text, logo topology, or measured sign-content claim is introduced.',
            'Full rendered visual acceptance and other-view checks remain required.'
        ]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.root/'research/monument-sign-fit.json'
    report = derive(args.root)
    output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'output': str(output), 'fit': report['fit'], 'conditional_sensitivity': report['conditional_sensitivity']}, indent=2))
