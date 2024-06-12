// src/utils/getCurrentMicroservice.ts
export function getCurrentService(): string {
  const hostname = window.location.hostname;

  if (hostname.includes('gis')) {
    return 'gis';
  } else if (hostname.includes('service-desk')) {
    return 'service-desk';
  } else {
    return 'unknown';
  }
}
