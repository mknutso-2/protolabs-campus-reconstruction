"""Reproduce the lower entrance fascia fit with the saved camera held fixed.

NumPy and SciPy are required only for this optional research refit. The scene
module uses the recorded nominal dimensions and needs neither dependency.
    python3 scripts/research/fit_frontage_fascia.py
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
CORNERS = np.array([[436, 430], [644, 441], [644, 468], [436, 453]], dtype=float)
INITIAL = np.array([61, 0, 77, 8, 5.1, 1.8], dtype=float)
PHOTO_SHA256 = 'd63946a04d11b20ae3cc026b06cf07e0a58deb7d46b8ece8bd305912a60f47a9'


def derive(root=ROOT):
    camera_path = root / 'research/reference_drone_camera_fit.json'
    photo_path = root / 'research/images/protolabs-official-hq-drone.jpg'
    camera = json.loads(camera_path.read_text())
    photo_hash = hashlib.sha256(photo_path.read_bytes()).hexdigest()
    if photo_hash != PHOTO_SHA256:
        raise ValueError('The annotated photograph differs from the recorded source')
    position = np.array(camera['position'])
    rotation = Rotation.from_euler('xyz', camera['rotation_euler_xyz_radians']).as_matrix()
    focal = camera['focal_length_pixels']
    image_width, image_height = camera['reference_size']
    if (image_width, image_height) != (1200, 800):
        raise ValueError('Corner annotations require the original 1200 x 800 photograph')

    def world_corners(p):
        x1, y1, x2, y2, top, height = p
        return np.array([[x1, y1, top], [x2, y2, top],
                         [x2, y2, top-height], [x1, y1, top-height]])

    def project(points):
        q = (points-position) @ rotation
        return np.stack([image_width/2+focal*q[:, 0]/-q[:, 2],
                         image_height/2-focal*q[:, 1]/-q[:, 2]], axis=1)

    def fit(pixels=CORNERS, corner_weights=(1, 1, 1, 1), prior_weight=1):
        weights = np.array(corner_weights)[:, None]

        def residual(p):
            image = ((project(world_corners(p))-pixels)*weights).ravel()
            prior = np.array([p[0]-61, p[2]-77, p[3]-8])*prior_weight
            return np.r_[image, prior]

        result = least_squares(residual, INITIAL)
        if not result.success or not np.all(np.isfinite(result.x)) or result.x[5] <= 0:
            raise ValueError('Fascia fit did not converge to a valid positive-height solution')
        p = result.x
        predicted = project(world_corners(p))
        error = predicted-pixels
        edge = p[2:4]-p[:2]
        return {'a_xy': p[:2].tolist(), 'b_xy': p[2:4].tolist(),
                'top_z': p[4], 'height': p[5], 'bottom_z': p[4]-p[5],
                'front_edge_length_m': float(np.linalg.norm(edge)),
                'yaw_degrees': math.degrees(math.atan2(edge[1], edge[0])),
                'inferred_depth_m': 3.0,
                'coordinate_rms_px': float(np.sqrt(np.mean(error**2))),
                'corner_rms_px': float(np.sqrt(np.mean(np.sum(error**2, axis=1)))),
                'projected_corners_px': predicted.tolist(),
                'corner_error_px': np.linalg.norm(error, axis=1).tolist(),
                'world_corners_xyz_m': world_corners(p).tolist(),
                'image_coordinate_weights_by_corner': list(corner_weights),
                'prior_weight_px_per_m': prior_weight}

    nominal = fit()
    weighted = fit(corner_weights=(1, .5, .5, 1))
    # Sensitivity is conditional on the approximate fixed camera and endpoint priors.
    rng = np.random.default_rng(20260907)
    trials = []
    for _ in range(128):
        jittered = CORNERS + rng.normal(size=(4, 2))*np.array([[2], [5], [5], [2]])
        trial = fit(jittered)
        trials.append([*trial['a_xy'], *trial['b_xy'], trial['top_z'], trial['height'],
                       trial['front_edge_length_m'], trial['yaw_degrees']])
    intervals = np.percentile(trials, [5, 95], axis=0)
    labels = ('a_x_m', 'a_y_m', 'b_x_m', 'b_y_m', 'top_z_m', 'height_m',
              'front_edge_length_m', 'yaw_degrees')
    return {
        'schema_version': 1,
        'status': 'Proposed photo-inferred lower fascia; four-view acceptance remains pending',
        'source': {'path': 'research/images/protolabs-official-hq-drone.jpg',
                   'url': 'https://www.protolabs.com/media/s4dignhf/hq-drone.jpg',
                   'sha256': photo_hash, 'attribution': 'Proto Labs, Inc.; undated official image',
                   'size_px': [1200, 800]},
        'camera': 'research/reference_drone_camera_fit.json',
        'camera_constraints': {
            'sha256': hashlib.sha256(camera_path.read_bytes()).hexdigest(),
            'held_fixed': True, 'position': camera['position'],
            'rotation_euler_xyz_radians': camera['rotation_euler_xyz_radians'],
            'focal_length_pixels': focal,
            'original_landmark_rms_px_unweighted': camera['rmse_pixel_unweighted'],
            'projection': 'q = (point - camera_position) @ Rotation.from_euler(xyz).as_matrix(); pixel = [600 + f*q.x/-q.z, 400 - f*q.y/-q.z]'},
        'coordinate_system': 'Metres; X east, Y north, Z NAVD88 minus 303.6 m',
        'manual_corners_px': CORNERS.tolist(),
        'corners_order': ['top_left', 'top_right', 'bottom_right', 'bottom_left'],
        'annotation_uncertainty_px_for_sensitivity': [2, 5, 5, 2],
        'annotation_review': [
            'The left vertical silhouette near x436 and y430..453 is directly visible; an independent image review supports these picks to a few pixels.',
            'The front-panel upper/lower edges slope slightly downward toward image right. Top-right and bottom-right are inferred continuations through truss/entrance-awnings occlusion, not confidently observed physical endpoints.',
            'The four points describe a single vertical front plane and do not measure the top surface, depth, hidden returns, lettering or exact panel topology.'
        ],
        'method': {
            'model': 'Vertical front rectangle with endpoint XY, common top Z and height; no camera or lidar-roof changes',
            'parameter_order': ['x1', 'y1', 'x2', 'y2', 'top', 'height'],
            'initial': INITIAL.tolist(),
            'solver': 'scipy.optimize.least_squares with default settings and no bounds',
            'nominal_residual': 'Concatenate 8 unweighted projected-minus-annotated image coordinates in pixels with [(x1-61)*1, (x2-77)*1, (y2-8)*1]',
            'endpoint_priors': 'Weak interpreted connector-plan priors x1=61 m, x2=77 m, y2=8 m; not new measured constraints',
            'rms_definition': 'coordinate_rms_px averages eight squared scalar coordinates; corner_rms_px averages four squared Euclidean corner distances and equals sqrt(2) times coordinate RMS',
            'reproduction': 'python3 scripts/research/fit_frontage_fascia.py (optional NumPy/SciPy research dependencies)'
        },
        'fit': nominal,
        'right_occlusion_weighted_alternative': {
            'method': 'Multiply each image-coordinate residual at both right corners by 0.5, leave left residuals and the original endpoint priors unchanged',
            'adopted': False, 'fit': weighted,
            'reason': 'Tests reduced confidence in occluded endpoints; does not establish a superior physical reconstruction from this one image'},
        'prior_sensitivity': {
            'warning': 'Holding the same pixels and camera, change all endpoint prior weights together; these alternatives expose depth/scale dependence on inferred priors',
            'weaker_prior': fit(prior_weight=.25), 'stronger_prior': fit(prior_weight=4)},
        'conditional_sensitivity': {
            'samples': 128, 'seed': 20260907, 'percentiles': [5, 95],
            'method': 'Independent Gaussian corner-coordinate jitter with 2 px left and 5 px occluded-right scales; original nominal objective, fixed camera and endpoint priors',
            'ranges': {label: intervals[:, i].tolist() for i, label in enumerate(labels)},
            'warning': 'Conditional perturbation ranges, not confidence intervals for true building dimensions; approximate camera calibration, photo date and endpoint-prior errors are excluded'},
        'limits': [
            'Right corners are occluded by truss/entrance elements. A subpixel fit residual measures consistency with these approximate picks, not physical accuracy.',
            'Weak endpoint priors reduce single-view depth and scale ambiguity. Camera landmark residuals are several pixels and are not refitted here.',
            'The 3 m depth, lettering, roof surface and hidden return are interpretations. Main lidar-constrained roof planes, massing and saved cameras remain unchanged.',
            'The 2022 lidar camera correspondences and the undated company photo are not contemporaneous measured fascia geometry.',
            'Nominal geometry is retained because isolated visual inspection confirms a better left extent and apparent height; uncertain right-edge weighting provides no compelling visual replacement.',
            'Other-view intersection, soffit and entrance checks remain required before accepting the integrated assembly.'
        ]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = derive(args.root)
    output = args.output or args.root/'research/frontage-fascia-fit.json'
    output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'output': str(output), 'fit': report['fit'],
                      'conditional_sensitivity': report['conditional_sensitivity']}, indent=2))
