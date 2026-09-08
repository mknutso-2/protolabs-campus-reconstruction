// Exterior collision plan derived from the Blender generator, in local metres.
// It represents solid footprints, with a small pedestrian clearance at walls.
type Point = readonly [number, number];
const footprints: readonly (readonly Point[])[] = [
  [
    [3.5, 1.1],
    [61, 1.1],
    [61, 49.8],
    [3.5, 49.8],
  ],
  [
    [-1, 0.7],
    [3.5, 0.7],
    [3.5, 8],
    [-1, 8],
  ],
  [
    [10, 47],
    [34, 47],
    [34, 58],
    [10, 58],
  ],
  [
    [55.9, 0],
    [72.5, 8.5],
    [76.5, 11.3],
    [76.5, 24.15],
    [65.65, 50.03],
    [56, 47],
  ],
  [
    [76.66, 24.16],
    [104.65, 38.86],
    [92.16, 63.5],
    [65.65, 50.03],
  ],
  [
    [71.75, 2],
    [76.25, 2],
    [76.25, 7],
    [71.75, 7],
  ],
];

function insideOrNear(
  x: number,
  y: number,
  polygon: readonly Point[],
  radius: number,
) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [ax, ay] = polygon[j],
      [bx, by] = polygon[i];
    if (ay > y !== by > y && x < ((bx - ax) * (y - ay)) / (by - ay) + ax)
      inside = !inside;
    const dx = bx - ax,
      dy = by - ay;
    const t = Math.max(
      0,
      Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)),
    );
    if ((x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= radius ** 2)
      return true;
  }
  return inside;
}

export function canWalkTo(east: number, north: number) {
  return (
    Number.isFinite(east) &&
    Number.isFinite(north) &&
    east > -160 &&
    east < 230 &&
    north > -150 &&
    north < 200 &&
    !footprints.some((polygon) => insideOrNear(east, north, polygon, 0.55))
  );
}
