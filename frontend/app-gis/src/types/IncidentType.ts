interface IncidentType {
  coordinates: number[];
  ctp_id: string | null;
  handled_unoms: Array<{
    unom: number;
    hours_to_cool: number;
    priority_group: number;
  }> | null;
  id: number;
  payload: Array<any> | Map<string, any>;
}

export default IncidentType;
