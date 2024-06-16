<script setup lang="ts">
import { ref, onMounted, watch, toRaw, computed } from 'vue';
import { MarkerClusterer } from '@googlemaps/markerclusterer';

import RighPanel from './components/RightPanel/RightPanel.vue';
import LeftPanel from './components/LeftPanel/LeftPanel.vue';
import getAllIncidents from 'src/api/getAllIncidents';

import { useOptionsStore } from 'src/stores/optionsStore';
import getStats from 'src/api/getStats';

import { useQuasar } from 'quasar';
import getGeoByFilters from 'src/api/getGeoByFilters';
import { GeoType1, GeoType2, GeoType3 } from 'src/types/GeoType';
import CreateArea from 'src/composables/createArea';
import getHeatmapColor from 'src/composables/getHexForHeatmap';
import Highcharts from 'highcharts';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';
import CreateIncidentDialog from 'src/dialogs/CreateIncidentDialog.vue';
import OpenIncidentDialog from './components/OpenIncidentsDialog.vue';
import PredictMode from './components/PredictMode.vue';
import InfoPanel from './components/InfoPanel.vue';
import PredictTimeline from './components/PredictTimeline.vue';
import LegendWidget from './components/LegendWidget.vue';
import CreateIncident from './components/CreateIncident.vue';
import IncidentMode from './components/IncidentMode.vue';
import getIncidentsById from 'src/api/getIncidentsById';

// when building SPA my png's stop working D;. This is a crazy workaround, may the god forgive me
const imageTable = {
  building_incident:
    'https://psv4.userapi.com/c235131/u346561169/docs/d36/63e77c9d3f28/building_incident.png?extra=bCT1vXsS0jqkbSu_7byLbKSdVmamlaYmMl3PkY02yjm98sApiGZf0fQksMkBYAmFOPmM2sl2NS5O4K44BN9qPMH0EWhKZ0yQ04UpmIzXjR2VOFQ0gHGKs4xx5u8c8gVn2S6g2jlXn5V92jwTXs5kFtCVoA',
  building_incident_active:
    'https://psv4.userapi.com/c235131/u346561169/docs/d43/dc4eb347de8a/building_incident_active.png?extra=PDPZmmmtHNDajV0zWEj0xnOE_jc8kTcuaCnsdJHZ8lRFrM3-ewPEIRIA-v_vzQdH5cNSiUS_u7JtkijnPaW1DomiQ91Oh1G7JcibGmB-vm2uWUTtaOfDVqaGCsdy5SwuJdoEzZBTzpaHiYxBYNJtIonoHw',
  ctp: 'https://psv4.userapi.com/c235131/u346561169/docs/d9/bcd6f4760b61/ctp.png?extra=7TPWruHnksx3cRtQH3ZpVjpXczL0ldrAoVTQtzrFmhgRsRmGyLc2hpGoX1kYctmCvRJtCQs8bD15sDfeTVoCFTUi7fK24N0AxSpPEg1A-QEtHNmdCeMrASttzWliSNIk7qFQ4IJ0pixc9CDqboMIKkjp1w',
  ctp_active:
    'https://psv4.userapi.com/c235131/u346561169/docs/d5/580d666c1aad/ctp_active.png?extra=vLBE4E-Ty9Wbx_9m6a9gMSsnIPz-LLwwDOgr7SzPUVkmaaZfdmtNZFOu7UThnFsPwFG_90FUvuts2hI1uT79zfFkBlZrN3AEyqEC3cT2FRV6Jqc3MKK_L7WqYqGzKJoVUV2TWd7c9CRaSnpsz0stl68RsQ',
  ctp_incident:
    'https://psv4.userapi.com/c235131/u346561169/docs/d5/326ef2bd8f43/ctp_incident.png?extra=FxVHT7lLlgKvdsRELZfMIxMOem6e2JKjU_Uwes4TaYLpndwmfV6Hss4tJ_T7aq9omq9oTc50GZiWxD6bbdLcpCsFfiGXa5KDTCIYU0NmgmC1Ptluo6PYEIk1SdM72FS8RlHzMuvuiKwhPzkbaI08r-vaqQ',
  ctp_incident_active:
    'https://psv4.userapi.com/c235131/u346561169/docs/d6/bf44690ff414/ctp_incident_active.png?extra=ITPYkTlUmYDHhgVBdkiuE6gWfeS5I-tgN5Ir8gVTmjfPx_Srdx8cKTYfgYlYPrwvUMspwn2odwCLwijMY0atdAEDX-_j5awrr_pmgMVddL1HodMeRIXQW4ECtD8XPjOdqcVjQN-ebrwlRuhXPCl1KznSmA',
};

const $q = useQuasar();
const colors = Highcharts.getOptions().colors;
const showIncidentDialog = ref(false);
const showIncidentCreateDialog = ref(false);

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
const currPredictDate = ref('2024-04-01T00:00:00');
const predictMode = ref(0);
const incidentMode = ref(0);
const optionsStore = useOptionsStore();

const clickMap = () => {
  if (optionsStore.mapMode == 'monitoring') {
    currPolygon.value = null;
    currMarker.value = null;
  }
  if (optionsStore.mapMode == 'incident') {
    if (!showIncidentDialog.value) {
      currMarker.value = null;
      currIncident.value = null;
    }
    currPolygon.value = null;

    if (polygonsRef.value.length > 0) {
      polygonsRef.value.forEach((polygon) => {
        toRaw(polygon).setMap(null);
        toRaw(polygon).setPath([]);
      });
      polygonsRef.value = [];
    }
  }
  if (optionsStore.mapMode == 'predict') {
    currPolygon.value = null;
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
        title: `ЦТП ${ctp_id}`,
        icon: {
          // @ts-ignore //
          url: imageTable[`${type}${currMarker.value == i ? '_active' : ''}`],
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
          // @ts-ignore //
          url: imageTable[
            `${getType(
              // @ts-ignore //
              toRaw(obj).get(toRaw(obj).keys().next().value).getIcon().url
            )}${mode}${
              currMarker.value == toRaw(obj).keys().next().value
                ? '_active'
                : ''
            }`
          ],
          scaledSize: new window.google.maps.Size(40, 40),
        });
    });
  }
};

watch(currMarker, () => updateMarkers());

const handleBuildingRender = (buidlings: GeoType3, predictDate: string) => {
  // @ts-ignore // sorry, too tired for this dumb shit. Tried my best
  const allCoordinates: number[][] = [];
  buidlings.forEach(
    ({
      UNOM: unom,
      coordinates: coords,
      Area: string,
      probabilites: probabilites,
    }: any) => {
      coords.forEach((newObj: any) => {
        allCoordinates.push(newObj);
        const newPolygon = new google.maps.Polygon({
          paths: newObj.map(([lat, lng]: [number, number]) => {
            return { lat: lng, lng: lat };
          }),
          strokeColor:
            predictDate === ''
              ? '#db8d78'
              : predictMode.value == 5
              ? getHeatmapColor(
                  // @ts-ignore //
                  probabilites.reduce((partialSum, a) => partialSum + a, 0) -
                    probabilites[3]
                )
              : getHeatmapColor(probabilites[predictMode.value]),
          strokeOpacity: 0.8,
          strokeWeight: 2,
          fillColor:
            predictDate === ''
              ? '#db8d78'
              : predictMode.value == 5
              ? getHeatmapColor(
                  // @ts-ignore //
                  probabilites.reduce((partialSum, a) => partialSum + a, 0) -
                    probabilites[3]
                )
              : getHeatmapColor(probabilites[predictMode.value]),
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
  getStats()
    .then((res) => {
      distributionData.value = res['event_counts'];
      tasksData.value = {
        // @ts-ignore //
        'Без событий': res['n_unoms_without_events'],
      };
    })
    .then();
});

const getDataMonitoring = async (predictDate = '') => {
  await getGeoByFilters(predictDate)
    .then((res) => {
      (Object.entries(res) as GeoType1[]).forEach(([district, districtObj]) => {
        (Object.entries(districtObj) as GeoType2[]).forEach(
          ([tec, tecObjects], index) => {
            const allCoordinates = handleBuildingRender(
              // @ts-ignore //
              tecObjects['buildings'],
              predictDate
            );
            // @ts-ignore //
            if (predictDate === '') handleMarkers('ctp', tecObjects['ctps']);
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

const handleIncidentPolygons = (unoms: any) => {
  currPolygon.value = null;

  if (polygonsRef.value.length > 0) {
    polygonsRef.value.forEach((polygon) => {
      toRaw(polygon).setMap(null);
      toRaw(polygon).setPath([]);
    });
    polygonsRef.value = [];
  }
  const getColorsByRank = (rank: number) => {
    if (rank == 1) return '#eb6e6e';
    else if (rank == 2) return '#ebe46e';
    else return '#92eb6e';
  };
  var maxHours = 0;
  // @ts-ignore //
  unoms.forEach(({ hours }) => {
    if (hours > maxHours) maxHours = hours;
  });
  unoms.forEach(({ unom: unom, GeoData: coords, Rank: rank, hours }: any) => {
    coords.forEach((newObj: any) => {
      const newPolygon = new google.maps.Polygon({
        paths: newObj.map(([lat, lng]: [number, number]) => {
          return { lat: lng, lng: lat };
        }),
        strokeColor:
          incidentMode.value == 1
            ? getColorsByRank(rank)
            : getHeatmapColor(1 - hours / maxHours),
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor:
          incidentMode.value == 1
            ? getColorsByRank(rank)
            : getHeatmapColor(1 - hours / maxHours),
        fillOpacity: 0.35,
        zIndex: 999,
      });
      polygonsRef.value.push(newPolygon);
      newPolygon.setMap(mapRef.value);
      newPolygon.addListener('click', () => (currPolygon.value = unom));
    });
  });
};

const handleMarkersIncident = (incidents: any) => {
  if (!mapRef.value) return;

  const newMarkers = [];
  for (let i = 0; i < incidents.length; i++) {
    const { ctp_id, coordinates: position, id, handled_unoms } = incidents[i];
    if (position) {
      const marker = new google.maps.Marker({
        position: { lat: position[1], lng: position[0] },
        title: `Инцидент #${id}`,
        icon: {
          // @ts-ignore //
          url: imageTable[
            `${ctp_id === '' ? 'building' : 'ctp'}_incident${
              currMarker.value == i ? '_active' : ''
            }`
          ],
          scaledSize: new window.google.maps.Size(40, 40),
        },
      });

      console.log(handled_unoms);

      marker.addListener('click', () => {
        currIncident.value = currMarker.value === i.toString() ? null : id;
        currMarker.value =
          currMarker.value === i.toString() ? null : i.toString();
        if (currMarker.value === i.toString())
          getIncidentsById(id).then((res) => {
            handleIncidentPolygons(res['handled_unoms']);
          });

        // else handleIncidentPolygons(handled_unoms);
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

  if (optionsStore.mapMode === 'monitoring') {
    await getDataMonitoring();
  }
  if (optionsStore.mapMode === 'incident') {
    await getDataIncident();
  }
  if (optionsStore.mapMode === 'predict') {
    await getDataMonitoring(currPredictDate.value);
    // $q.loading.hide();
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

watch(predictMode, loadData);
watch(currPredictDate, loadData);
watch(incidentMode, () => {
  if (currIncident.value) {
    console.warn(currIncident.value);
    getIncidentsById(currIncident.value).then((res) => {
      handleIncidentPolygons(res['handled_unoms']);
    });
  }
});


const distributionData = ref<Map<string, number[]>>();
const tasksData = ref<Map<string, number[]>>();


</script>

<template>
  <div class="map-container" id="container" />
  <OpenIncidentDialog
    :incident-id="currIncident!"
    v-model="showIncidentDialog"
  />
  <InfoPanel :data="tasksData!" />
  <PredictMode v-model="predictMode" />
  <IncidentMode :shown="currIncident" v-model="incidentMode" />
  <PredictTimeline v-model="currPredictDate" />
  <LegendWidget :incident-id="currIncident" :incident-mode="incidentMode" />
  <CreateIncident @click="showIncidentCreateDialog = true" />
  <CreateIncidentDialog v-model="showIncidentCreateDialog" />
  <IncidentDialog v-model="showIncidentDialog" :incident-id="currIncident" />
  <RighPanel :place-id="currPolygon!" />
  <LeftPanel />
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
</style>
