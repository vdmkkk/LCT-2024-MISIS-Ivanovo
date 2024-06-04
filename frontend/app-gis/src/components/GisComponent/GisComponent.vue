<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { MarkerClusterer } from '@googlemaps/markerclusterer';

import RighPanel from './components/RightPanel/RightPanel.vue';

// all the map controls
const mapRef = ref<google.maps.Map | null>(null);
const markersRef = ref<google.maps.Marker[]>([]);
const markerClustererRef = ref<MarkerClusterer | null>(null);

// reactive stuff
const chosenPlace = ref();

const coordinates = [
  { lat: 55.752004, lng: 37.617734 },
  { lat: 55.752104, lng: 37.617834 },
  { lat: 55.752204, lng: 37.617934 },
  { lat: 55.752304, lng: 37.618034 },
  { lat: 55.752404, lng: 37.618134 },
];

const bindMap = () => {
  const container = document.createElement('div');
  container.className = 'map';
  container.id = 'map';
  container.style.height = '100vh';
  document.getElementById('container')?.appendChild(container);

  const mapOptions: google.maps.MapOptions = {
    center: { lat: 55.752004, lng: 37.617734 },
    zoom: 13,
    disableDefaultUI: true,
    zoomControl: true,
  };

  const map = new google.maps.Map(container, mapOptions);
  map.addListener('click', () => (chosenPlace.value = null));

  mapRef.value = map;

  handleMarkers();
};

const handleMarkers = () => {
  if (!mapRef.value) return;

  markerClustererRef.value = new MarkerClusterer({
    map: mapRef.value,
    markers: [], // not sure why, but it works only if I add markers one-by-one later :/
  });

  coordinates.forEach((position, key) => {
    const marker = new google.maps.Marker({
      position,
      title: 'Marker Title',
    });
    marker.addListener('click', () => (chosenPlace.value = key));
    markersRef.value.push(marker);
    markerClustererRef.value?.addMarker(marker);
  });
};

onMounted(() => {
  if (!window.google) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.VUE_APP_GOOGLE_API}&libraries=places`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      bindMap();
    };
  } else {
    bindMap();
  }
});
</script>

<template>
  <div class="map-container" id="container" />
  <RighPanel :place-id="chosenPlace" />
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
</style>
