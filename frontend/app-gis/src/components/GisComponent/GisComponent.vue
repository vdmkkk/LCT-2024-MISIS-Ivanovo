<script setup lang="ts">
import { ref, onMounted } from 'vue';

const mapRef = ref();

const bindMap = () => {
  const container = document.createElement('div');
  container.className = 'map';
  container.id = 'map';
  container.style.height = '100vh';
  document.getElementById('container')?.appendChild(container);

  const mapOptions: google.maps.MapOptions = {
    center: { lat: 55.752004, lng: 37.617734 },
    zoom: 13,
  };

  const map = new google.maps.Map(container, mapOptions);

  mapRef.value = map;

  addMarker({ lat: 55.752004, lng: 37.617734 });
};

const addMarker = (position: google.maps.LatLngLiteral) => {
  if (!mapRef.value) return;

  const marker = new google.maps.Marker({
    position,
    map: mapRef.value,
    title: 'Marker Title', // Optional: Add a title for the marker
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
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%; /* or any other height you prefer */
}
</style>
