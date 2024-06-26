import PassportWidget from 'src/components/GisComponent/components/RightPanel/components/PassportWidget.vue';
import ReportWidget from 'src/components/GisComponent/components/RightPanel/components/ReportWidget.vue';
import IncidentsWidget from 'src/components/GisComponent/components/RightPanel/components/IncidentsWidget.vue';
import PredictWidget from 'src/components/GisComponent/components/RightPanel/components/PredictWidget/PredictWidget.vue';

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

const RightPanelWidgets = {
  report: ReportWidget,
  passport: PassportWidget,
  incidents: IncidentsWidget,
  predicts: PredictWidget,
};

export { RightPanelWidgets };
export type { NavigationMonitoringButtonType, NavigationIncidentsButtonType };
