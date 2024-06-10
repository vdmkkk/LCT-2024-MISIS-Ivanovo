package repository

import (
	"context"
	"encoding/json"
	"github.com/jmoiron/sqlx"
	"lct/internal/models"
)

type buildingRepo struct {
	db *sqlx.DB
}

func InitBuildingRepo(db *sqlx.DB) Building {
	return buildingRepo{db: db}
}

func (b buildingRepo) GetByUNOM(ctx context.Context, unom int) (models.Building, error) {
	query := `SELECT unom, ctp, external_system_address, external_system_id, bti_address, district, area, project_series, 
       number_of_floors, number_of_entrances, number_of_apartments, total_area, total_residential_area, 
       total_non_residential_area, wear_and_tear_bti, wall_materials, emergency_status, 
       number_of_passenger_elevators, number_of_freight_elevators, roof_cleaning_priority, 
       roof_materials, housing_fund_types, mkd_statuses, consumers, group_type, central_heating, 
       meter_brand, meter_serial_number, id_uu, full_address, ods_number, ods_address, serial_number, 
       city, administrative_district, municipal_district, locality, street, house_number_type, 
       house_number, building_number, structure_number_type, structure_number, unad, material, 
       purpose, class, type, sign, global_id, obj_type, address_x, municipal_district_1, 
       planning_element_name, house_ownership_number_type, intra_city_area, adm_area, district_1, 
       nreg, dreg, n_fias, d_fias, kad_n, kad_zu, kladr, tdoc, ndoc, ddoc, adr_type, vid, 
       sostad, status, to_json(geo_data),to_json(geo_data_center), id_ods, phone_number
		FROM buildings
		WHERE unom = $1;`

	row := b.db.QueryRowContext(ctx, query, unom)

	var building models.Building
	var geoDataJSON []byte
	var geoDataCenterJSON []byte
	err := row.Scan(&building.Unom,
		&building.Ctp,
		&building.ExternalSystemAddress,
		&building.ExternalSystemID,
		&building.BTIAddress,
		&building.District,
		&building.Area,
		&building.ProjectSeries,
		&building.NumberOfFloors,
		&building.NumberOfEntrances,
		&building.NumberOfApartments,
		&building.TotalArea,
		&building.TotalResidentialArea,
		&building.TotalNonResidentialArea,
		&building.WearAndTearBTI,
		&building.WallMaterials,
		&building.EmergencyStatus,
		&building.NumberOfPassengerElevators,
		&building.NumberOfFreightElevators,
		&building.RoofCleaningPriority,
		&building.RoofMaterials,
		&building.HousingFundTypes,
		&building.MKDStatuses,
		&building.Consumers,
		&building.GroupType,
		&building.CentralHeating,
		&building.MeterBrand,
		&building.MeterSerialNumber,
		&building.IDUU,
		&building.FullAddress,
		&building.OdsNumber,
		&building.OdsAddress,
		&building.SerialNumber,
		&building.City,
		&building.AdministrativeDistrict,
		&building.MunicipalDistrict,
		&building.Locality,
		&building.Street,
		&building.HouseNumberType,
		&building.HouseNumber,
		&building.BuildingNumber,
		&building.StructureNumberType,
		&building.StructureNumber,
		&building.UNAD,
		&building.Material,
		&building.Purpose,
		&building.Class,
		&building.Type,
		&building.Sign,
		&building.GlobalID,
		&building.ObjectType,
		&building.AddressX,
		&building.MunicipalDistrict1,
		&building.PlanningElementName,
		&building.HouseOwnershipNumberType,
		&building.IntraCityArea,
		&building.AdmArea,
		&building.District1,
		&building.NREG,
		&building.DREG,
		&building.NFIAS,
		&building.DFIAS,
		&building.KADN,
		&building.KADZU,
		&building.KLADR,
		&building.TDOC,
		&building.NDOC,
		&building.DDOC,
		&building.AddrType,
		&building.VID,
		&building.SOSTAD,
		&building.Status,
		&geoDataJSON,
		&geoDataCenterJSON,
		&building.IDODS,
		&building.PhoneNumber)
	if err != nil {
		return models.Building{}, err
	}

	err = json.Unmarshal(geoDataJSON, &building.GeoData)
	if err != nil {
		var coordinatesFourDims [][][][]float64
		err = json.Unmarshal(geoDataJSON, &coordinatesFourDims)
		if err != nil {
			return models.Building{}, err
		}

		building.GeoData = *flatMap(coordinatesFourDims)
	}

	err = json.Unmarshal(geoDataCenterJSON, &building.GeoDataCenter)
	if err != nil {
		return models.Building{}, err
	}

	return building, nil
}