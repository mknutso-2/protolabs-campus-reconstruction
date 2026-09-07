"""Fit aerial-traced tree widths to supported lidar heights; disclose fallbacks."""
import hashlib
import json
import math
import random
import statistics


def add_campus_trees(root, collection, assets, ground, pixel, north_rows):
    import bpy
    layout_path = root / 'research/site-layout.json'
    constraints_path = root / 'research/campus-tree-constraints.json'
    layout = json.loads(layout_path.read_text())
    constraints = json.loads(constraints_path.read_text())
    if hashlib.sha256(layout_path.read_bytes()).hexdigest() != constraints['layout_sha256']:
        raise RuntimeError('Campus tree constraints do not match the aerial trace')
    rows = constraints['rows']
    if len(rows) != len(layout['trees']):
        raise RuntimeError('Campus tree constraint count differs from trace')
    eligible = [r for r in rows if r['scene_eligible']]
    bounds = [([min(v.co[k] for v in src.data.vertices) for k in range(3)],
               [max(v.co[k] for v in src.data.vertices) for k in range(3)]) for src in assets]
    rng = random.Random(554007)
    report = {'constraint_sha256': hashlib.sha256(constraints_path.read_bytes()).hexdigest(),
              'placement': 'Bottom at rendered 5 m terrain; lidar height retained. Absolute top shifts by disclosed ground adjustment.',
              'width': '2026 aerial-traced diameter, uncertain; not lidar full-crown measurement',
              'rows': []}
    for index, (trace, row) in enumerate(zip(layout['trees'], rows)):
        if (row['tree_array_index'] != index or row['tree_id'] != trace['id']
                or row['center_px'] != trace['center_px']):
            raise RuntimeError(f'Unmatched campus tree constraint at index {index}')
        x, y = pixel(trace['center_px'])
        if math.hypot(x-row['position'][0], y-row['position'][1]) > .001:
            raise RuntimeError('Campus tree coordinate mismatch')
        item = {'id': trace['id'], 'index': index, 'position': [x, y]}
        report['rows'].append(item)
        if y >= 70 and any((x-r['position'][0])**2+(y-r['position'][1])**2 < 36 for r in north_rows):
            item['status'] = 'omitted_overlap_with_north_envelope'
            continue
        height = row['canopy_height_m'] if row['scene_eligible'] else None
        if height is not None:
            item.update(status='lidar_supported_height', confidence=row['confidence'])
        else:
            # Same approximate planting strip, nearby, similar ground and away
            # from building margins. This is an inference, not a new measurement.
            candidates = [r for r in eligible if math.dist([x,y], r['position']) <= 30
                          and min(abs(x-r['position'][0]), abs(y-r['position'][1])) <= 8
                          and row['ground_z'] is not None and abs(r['ground_z']-row['ground_z']) <= 2
                          and r['support']['distance_to_cached_building_plan_m'] >= 8]
            if (row['support']['distance_to_cached_building_plan_m'] >= 8 and len(candidates) >= 2
                    and any(r['confidence'] == 'higher_relative_confidence' for r in candidates)
                    and max(r['canopy_height_m'] for r in candidates)-min(r['canopy_height_m'] for r in candidates) <= 4):
                preferred = [r for r in candidates if r['confidence'] == 'higher_relative_confidence']
                used = preferred if len(preferred) >= 2 else candidates
                height = statistics.median(r['canopy_height_m'] for r in used)
                item.update(status='inferred_neighborhood_height', neighbors=[r['tree_id'] for r in used])
            else:
                item.update(status='omitted_insufficient_height_evidence', reasons=row['ineligibility_reasons'])
                continue
        width = 2*trace['crown_radius_px']*(layout['extent']['xmax']-layout['extent']['xmin'])/3000
        src = assets[index % len(assets)]
        low, high = bounds[index % len(assets)]
        vertical = height/(high[2]-low[2])
        horizontal = width/max(high[0]-low[0], high[1]-low[1])
        scene_ground = ground(x,y)
        ob = bpy.data.objects.new('Campus tree '+trace['id'], src.data)
        collection.objects.link(ob)
        ob.location = (x, y, scene_ground-low[2]*vertical)
        ob.scale = (horizontal, horizontal, vertical)
        ob.rotation_euler.z = rng.random()*math.tau
        ob['evidence'] = item['status']+'; aerial width and position, species and crown shape inferred'
        ob['tree_id'] = trace['id']
        ob['canopy_height_m'] = height
        ob['source_ground_z'] = row['ground_z']
        ob['scene_ground_z'] = scene_ground
        item.update(height_m=height, traced_width_m=width, source_ground_z=row['ground_z'],
                    scene_ground_z=scene_ground, ground_adjustment_m=scene_ground-row['ground_z'])
    report['counts'] = {status: sum(r['status'] == status for r in report['rows'])
                        for status in sorted({r['status'] for r in report['rows']})}
    return report
