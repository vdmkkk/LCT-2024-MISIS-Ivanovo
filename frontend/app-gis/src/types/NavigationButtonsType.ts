import PassportWidget from 'src/components/GisComponent/components/RightPanel/components/Monitoring/PassportWidget.vue';
import ReportWidget from 'src/components/GisComponent/components/RightPanel/components/Monitoring/ReportWidget.vue';
import IncidentsWidget from 'src/components/GisComponent/components/RightPanel/components/Monitoring/IncidentsWidget.vue';
import PredictWidget from 'src/components/GisComponent/components/RightPanel/components/Monitoring/PredictWidget/PredictWidget.vue';

import IncidentWidget from 'src/components/GisComponent/components/RightPanel/components/Incidents/IncidentWidget.vue';
import StatsWidget from 'src/components/GisComponent/components/RightPanel/components/Incidents/StatsWidget.vue';
import UnomsWidget from 'src/components/GisComponent/components/RightPanel/components/Incidents/UnomsWidget.vue';

type NavigationMonitoringButtonType = {
  name: string;
  type: 'report' | 'passport' | 'incidents' | 'predicts';
  logo: string;
};

type NavigationIncidentsButtonType = {
  name: string;
  type: 'incident' | 'unoms' | 'stats';
  logo: string;
};

const RightPanelMonitoringWidgets = {
  report: ReportWidget,
  passport: PassportWidget,
  incidents: IncidentsWidget,
  predicts: PredictWidget,
};

const RightPanelIncidentsWidgets = {
  incident: IncidentWidget,
  unoms: UnomsWidget,
  stats: StatsWidget,
};

export { RightPanelMonitoringWidgets, RightPanelIncidentsWidgets };
export type { NavigationMonitoringButtonType, NavigationIncidentsButtonType };
