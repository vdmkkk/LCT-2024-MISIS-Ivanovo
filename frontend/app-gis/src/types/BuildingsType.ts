interface BuildingType {
  unom: number;
  ctp: string;
  external_system_address: string;
  external_system_id: number;
  bti_address: string;
  district: string;
  area: string;
  project_series: string;
  number_of_floors: number;
  number_of_entrances: number;
  number_of_apartments: number;
  total_area: number;
  total_residential_area: number;
  total_non_residential_area: string;
  wear_and_tear_bti: string;
  wall_materials: string;
  emergency_status: number;
  number_of_passenger_elevators: number;
  number_of_freight_elevators: number;
  roof_cleaning_priority: string;
  roof_materials: string;
  housing_fund_types: number;
  mkd_statuses: number;
  consumers: string;
  group_type: string;
  central_heating: string;
  meter_brand: string;
  meter_serial_number: string;
  id_uu: number;
  full_address: string;
  ods_number: string;
  ods_address: string;
  serial_number: string;
  city: string;
  administrative_district: string;
  municipal_district: string;
  locality: string;
  street: string;
  house_number_type: string;
  house_number: string;
  building_number: string;
  structure_number_type: string;
  structure_number: string;
  unad: number;
  material: string;
  purpose: string;
  class: string;
  type: string;
  sign: string;
  global_id: number;
  obj_type: string;
  address_x: string;
  municipal_district_1: string;
  planning_element_name: string;
  house_ownership_number_type: string;
  intra_city_area: string;
  adm_area: string;
  district_1: string;
  nreg: string;
  dreg: string;
  n_fias: string;
  d_fias: string;
  kad_n: string;
  kad_zu: string;
  kladr: string;
  tdoc: string;
  ndoc: string;
  ddoc: string;
  adr_type: string;
  vid: string;
  sostad: string;
  status: string;
  geo_data: number[][][];
  geo_data_center: number[];
  id_ods: number;
  phone_number: string;
}

export default BuildingType;
