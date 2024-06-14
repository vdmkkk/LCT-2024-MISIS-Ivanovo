import * as turf from '@turf/turf';

function CreateArea(coordinates: any): google.maps.LatLngLiteral[] {
  // Convert the coordinates to GeoJSON Points
  const points = coordinates.map((coord: any) => turf.point(coord));

  // Create a FeatureCollection from the points
  const featureCollection = turf.featureCollection(points);

  // Compute the Convex Hull
  const convexHull = turf.convex(featureCollection);

  if (!convexHull) {
    throw new Error('Convex Hull could not be computed.');
  }

  // Extract the coordinates from the Convex Hull and convert to google.maps.LatLngLiteral[]
  const path = convexHull.geometry.coordinates[0].map((coord) => ({
    lat: coord[1],
    lng: coord[0],
  }));

  return path;
}

export default CreateArea;
