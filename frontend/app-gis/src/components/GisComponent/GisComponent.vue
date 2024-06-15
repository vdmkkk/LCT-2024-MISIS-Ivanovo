<script setup lang="ts">
import { ref, onMounted, watch, toRaw, computed } from 'vue';
import { MarkerClusterer } from '@googlemaps/markerclusterer';

import RighPanel from './components/RightPanel/RightPanel.vue';
import LeftPanel from './components/LeftPanel/LeftPanel.vue';
import getAllPolygons from 'src/api/getAllPolygons';
import getAllIncidents from 'src/api/getAllIncidents';

import { useOptionsStore } from 'src/stores/optionsStore';

import { useQuasar } from 'quasar';
import getGeoByFilters from 'src/api/getGeoByFilters';
import { GeoType1, GeoType2, GeoType3 } from 'src/types/GeoType';
import CreateArea from 'src/composables/createArea';
import Highcharts from 'highcharts';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';

const $q = useQuasar();
const colors = Highcharts.getOptions().colors;
const showIncidentDialog = ref(false);

// all the map controls
const mapRef = ref<google.maps.Map | null>(null);
const markersRef = ref<Map<string, google.maps.Marker>[]>([]);
const markerClustererRef = ref<MarkerClusterer | null>(null);
const polygonsRef = ref<google.maps.Polygon[]>([]);
const areaPolygonsRef = ref<google.maps.Polygon[]>([]);

// reactive stuff
const currPolygon = ref<number | null>();
const currIncident = ref<number | null>();
const currMarker = ref<string | number | null>();
const optionsStore = useOptionsStore();

const coordinates = [
  { lat: 55.752004, lng: 37.617734 },
  { lat: 55.752104, lng: 37.617834 },
  { lat: 55.752204, lng: 37.617934 },
  { lat: 55.752304, lng: 37.618034 },
  { lat: 55.752404, lng: 37.618134 },
];

const clickMap = () => {
  if (optionsStore.mapMode == 'monitoring') {
    currPolygon.value = null;
    currMarker.value = null;
  } else {
    if (!showIncidentDialog.value) {
      currMarker.value = null;
      currIncident.value = null;
    }
  }
  if (optionsStore.leftPanelOption == 'layers')
    optionsStore.setLeftPanelOption(null);
};

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
  map.addListener('click', () => {
    clickMap();
  });

  map.addListener('drag', () => {
    if (optionsStore.leftPanelOption == 'layers')
      optionsStore.setLeftPanelOption(null);
  });

  mapRef.value = map;

  // handleMarkers('ctp');
};

const handleMarkers = (type: 'ctp' | 'tec', ctps: any) => {
  if (!mapRef.value) return;

  const newMarkers = [];
  for (let i = 0; i < ctps.length; i++) {
    const { ctp_id, center: position, Source: tec } = ctps[i];
    if (position) {
      const marker = new google.maps.Marker({
        position: { lat: position[1], lng: position[0] },
        title: 'Marker Title',
        icon: {
          url: `src/assets/markers/${type}${
            currMarker.value == i ? '_active' : ''
          }.png`,
          scaledSize: new window.google.maps.Size(40, 40),
        },
      });

      marker.addListener('click', () => {
        currMarker.value =
          currMarker.value === i.toString() ? null : i.toString();
      });

      markersRef.value.push(
        new Map<string, google.maps.Marker>([[i.toString(), marker]])
      );
      newMarkers.push(marker);
      marker.setMap(mapRef.value);
    }
  }

  // markerClustererRef.value = new MarkerClusterer({
  //   markers: newMarkers,
  //   map: mapRef.value,
  // });
};

const clearMarkers = () => {
  // if (markerClustererRef.value) {
  //   toRaw(markerClustererRef.value).clearMarkers();
  // markerClustererRef.value.setMap(null);
  // @ts-ignore //
  Object.entries(markersRef.value).forEach(([key, marker]) => {
    // @ts-ignore //
    for (const [key, item] of marker.entries()) {
      toRaw(item).setVisible(false);
      toRaw(item).setMap(null);
      toRaw(item).addListener('click', () => {
        console.log();
      });
      toRaw(markerClustererRef.value)?.removeMarker(item);
    }
  });
  markersRef.value = [];
  // console.log(markerClustererRef.value);
  // console.log(markersRef);
  // markersRef.value = [];
  // Object.entries(markersRef.value).forEach(
  //   ([key: number, marker: google.maps.Marker]) => {
  //     console.error(marker);
  //     toRaw(marker).setMap(null);
  //   }
  // );
  // }
};

const updateMarkers = () => {
  const getType = (url: string) => {
    switch (true) {
      case url.includes('ctp'):
        return 'ctp';
      case url.includes('tec'):
        return 'tec';
      case url.includes('building'):
        return 'building';
      default:
        return 'building';
    }
  };

  if (markersRef.value) {
    const mode = optionsStore.mapMode == 'incident' ? '_incident' : '';
    markersRef.value.map((obj) => {
      // honestly it was pure luck and I have no clue how it works. Hopefully it will never break apart or i will kill myself slowly and painfully. Nightmare Nightmare Nightmare Nightmare
      toRaw(obj)
        .get(toRaw(obj).keys().next().value)
        ?.set('icon', {
          url: `src/assets/markers/${getType(
            // @ts-ignore //
            toRaw(obj).get(toRaw(obj).keys().next().value).getIcon().url
          )}${mode}${
            currMarker.value == toRaw(obj).keys().next().value ? '_active' : ''
          }.png`,
          scaledSize: new window.google.maps.Size(40, 40),
        });
    });
  }
};

watch(currMarker, () => updateMarkers());

const handleBuildingRender = (buidlings: GeoType3) => {
  // @ts-ignore // sorry, too tired for this dumb shit. Tried my best
  const allCoordinates: number[][] = [];
  buidlings.forEach(
    ({ UNOM: unom, coordinates: coords, Area: string }: any) => {
      coords.forEach((newObj: any) => {
        allCoordinates.push(newObj);
        const newPolygon = new google.maps.Polygon({
          paths: newObj.map(([lat, lng]: [number, number]) => {
            return { lat: lng, lng: lat };
          }),
          strokeColor: '#9c9c9c',
          strokeOpacity: 0.8,
          strokeWeight: 2,
          fillColor: '#9c9c9c',
          fillOpacity: 0.35,
          zIndex: 999,
        });
        polygonsRef.value.push(newPolygon);
        newPolygon.setMap(mapRef.value);
        newPolygon.addListener('click', () => (currPolygon.value = unom));
      });
    }
  );
  return allCoordinates.flat(1);
};

onMounted(() => {
  loadData();
});

const getDataMonitoring = async () => {
  await getGeoByFilters()
    .then((res) => {
      (Object.entries(res) as GeoType1[]).forEach(([district, districtObj]) => {
        (Object.entries(districtObj) as GeoType2[]).forEach(
          ([tec, tecObjects], index) => {
            const allCoordinates = handleBuildingRender(
              // @ts-ignore //
              tecObjects['buildings']
            );
            // @ts-ignore //
            handleMarkers('ctp', tecObjects['ctps']);
            // @ts-ignore //
            if (tec != 'null' && tec != '') {
              const newPolygon = new google.maps.Polygon({
                paths: CreateArea(allCoordinates),
                strokeColor: colors?.[index % 10].toString(),
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: colors?.[index % 10].toString(),
                fillOpacity: 0.2,
              });
              areaPolygonsRef.value.push(newPolygon);
              newPolygon.setMap(mapRef.value);
              newPolygon.addListener('click', () => clickMap());
            }
          }
        );
      });
      $q.loading.hide();
    })
    .catch((e) => {
      $q.loading.hide();
    });
};

const handleMarkersIncident = (incidents: any) => {
  if (!mapRef.value) return;

  const newMarkers = [];
  for (let i = 0; i < incidents.length; i++) {
    const { ctp_id, coordinates: position, id } = incidents[i];
    if (position) {
      const marker = new google.maps.Marker({
        position: { lat: position[1], lng: position[0] },
        title: 'Marker Title',
        icon: {
          url: `src/assets/markers/${
            ctp_id === '' ? 'building' : 'ctp'
          }_incident${currMarker.value == i ? '_active' : ''}.png`,
          scaledSize: new window.google.maps.Size(40, 40),
        },
      });

      marker.addListener('click', () => {
        currIncident.value = currMarker.value === i.toString() ? null : id;
        currMarker.value =
          currMarker.value === i.toString() ? null : i.toString();
        showIncidentDialog.value = true;
        console.log(currIncident.value);
      });

      markersRef.value.push(
        new Map<string, google.maps.Marker>([[i.toString(), marker]])
      );
      newMarkers.push(marker);
      marker.setMap(mapRef.value);
    }
  }

  // markerClustererRef.value = new MarkerClusterer({
  //   markers: newMarkers,
  //   map: mapRef.value,
  // });
};

const getDataIncident = async () => {
  await getAllIncidents().then((res) => {
    handleMarkersIncident(res); // TODO: later get type from inside the incident object
    $q.loading.hide();
  });
};

const getDataPredict = async () => {
  console.log();
};

const loadData = async () => {
  $q.loading.show({ message: 'Идет загрузка карты. Пожалуйста, подождите' });

  currIncident.value = null;
  currPolygon.value = null;
  currMarker.value = null;

  if (polygonsRef.value.length > 0) {
    polygonsRef.value.forEach((polygon) => {
      toRaw(polygon).setMap(null);
      toRaw(polygon).setPath([]);
    });
    polygonsRef.value = [];
  }

  if (areaPolygonsRef.value.length > 0) {
    areaPolygonsRef.value.forEach((polygon) => {
      toRaw(polygon).setMap(null);
      toRaw(polygon).setPath([]);
    });
    areaPolygonsRef.value = [];
  }

  clearMarkers();

  switch (true) {
    case optionsStore.mapMode == 'monitoring':
      await getDataMonitoring();
    case optionsStore.mapMode == 'incident':
      await getDataIncident();
    case optionsStore.mapMode == 'predict':
      await getDataPredict();
  }
};

const filtersObject = computed(() => {
  const obj: Record<string, string | null> = {};
  optionsStore.filters.forEach((value, key) => {
    obj[key] = value;
  });
  return obj;
});

watch(
  filtersObject,
  (newValue, oldValue) => {
    loadData();
  },
  { deep: true }
);

const mapModeObject = computed(() => {
  const obj: Record<string, string> = {};
  obj['mode'] = optionsStore.mapMode;
  return obj;
});

watch(mapModeObject, loadData);

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

watch(showIncidentDialog, clickMap);
</script>

<template>
  <div class="map-container" id="container" />
  <IncidentDialog v-model="showIncidentDialog" :incident-id="currIncident!" />
  <RighPanel :place-id="currPolygon!" />
  <LeftPanel />
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
</style>
