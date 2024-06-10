package models

import "github.com/guregu/null/v5"

type Building struct {
	Unom                       int           `json:"unom"`                          // Unom is the primary key.
	Ctp                        null.String   `json:"ctp"`                           // Ctp is a varchar(255).
	ExternalSystemAddress      null.String   `json:"external_system_address"`       // External system address as TEXT.
	ExternalSystemID           null.Float    `json:"external_system_id"`            // External system ID as FLOAT8.
	BTIAddress                 null.String   `json:"bti_address"`                   // BTI address as TEXT.
	District                   null.String   `json:"district"`                      // District as TEXT.
	Area                       null.String   `json:"area"`                          // Area as TEXT.
	ProjectSeries              null.String   `json:"project_series"`                // Project series as TEXT.
	NumberOfFloors             null.Float    `json:"number_of_floors"`              // Number of floors as FLOAT8.
	NumberOfEntrances          null.Float    `json:"number_of_entrances""`          // Number of entrances as FLOAT8.
	NumberOfApartments         null.Float    `json:"number_of_apartments"`          // Number of apartments as FLOAT8.
	TotalArea                  null.Float    `json:"total_area"`                    // Total area as FLOAT8.
	TotalResidentialArea       null.Float    `json:"total_residential_area"`        // Total residential area as FLOAT8.
	TotalNonResidentialArea    null.Float    `json:"total_non_residential_area"`    // Total non-residential area as TEXT (using null.Float for potential NULL value).
	WearAndTearBTI             null.String   `json:"wear_and_tear_bti"`             // Wear and tear BTI as TEXT.
	WallMaterials              null.String   `json:"wall_materials"`                // Wall materials as TEXT.
	EmergencyStatus            null.Float    `json:"emergency_status"`              // Emergency status as FLOAT8.
	NumberOfPassengerElevators null.Float    `json:"number_of_passenger_elevators"` // Number of passenger elevators as FLOAT8.
	NumberOfFreightElevators   null.Float    `json:"number_of_freight_elevators"`   // Number of freight elevators as FLOAT8.
	RoofCleaningPriority       null.String   `json:"roof_cleaning_priority"`        // Roof cleaning priority as TEXT.
	RoofMaterials              null.String   `json:"roof_materials"`                // Roof materials as TEXT.
	HousingFundTypes           null.Float    `json:"housing_fund_types"`            // Housing fund types as FLOAT8.
	MKDStatuses                null.Float    `json:"mkd_statuses"`                  // MKD statuses as FLOAT8.
	Consumers                  null.String   `json:"consumers"`                     // Consumers as TEXT.
	GroupType                  null.String   `json:"group_type"`                    // Group type as TEXT.
	CentralHeating             null.String   `json:"central_heating"`               // Central heating as TEXT.
	MeterBrand                 null.String   `json:"meter_brand"`                   // Meter brand as TEXT.
	MeterSerialNumber          null.String   `json:"meter_serial_number"`           // Meter serial number as TEXT.
	IDUU                       null.Float    `json:"iduu"`                          // ID UU as FLOAT8.
	FullAddress                null.String   `json:"full_address"`                  // Full address as TEXT.
	OdsNumber                  null.String   `json:"ods_number"`                    // ODS number as TEXT.
	OdsAddress                 null.String   `json:"ods_address"`                   // ODS address as TEXT.
	SerialNumber               null.String   `json:"serial_number"`                 // Serial number as TEXT.
	City                       null.String   `json:"city"`                          // City as TEXT.
	AdministrativeDistrict     null.String   `json:"administrative_district"`       // Administrative district as TEXT.
	MunicipalDistrict          null.String   `json:"municipal_district"`            // Municipal district as TEXT.
	Locality                   null.String   `json:"locality"`                      // Locality as TEXT.
	Street                     null.String   `json:"street"`                        // Street as TEXT.
	HouseNumberType            null.String   `json:"house_number_type""`            // House number type as TEXT.
	HouseNumber                null.String   `json:"house_number"`                  // House number as TEXT.
	BuildingNumber             null.String   `json:"building_number"`               // Building number as TEXT.
	StructureNumberType        null.String   `json:"structure_number_type"`         // Structure number type as TEXT.
	StructureNumber            null.String   `json:"structure_number"`              // Structure number as TEXT.
	UNAD                       null.Float    `json:"unad"`                          // UNAD as FLOAT8.
	Material                   null.String   `json:"material"`                      // Material as TEXT.
	Purpose                    null.String   `json:"purpose"`                       // Purpose as TEXT.
	Class                      null.String   `json:"class"`                         // Class as TEXT.
	Type                       null.String   `json:"type"`                          // Type as TEXT.
	Sign                       null.String   `json:"sign"`                          // Sign as TEXT.
	GlobalID                   null.Float    `json:"global_id"`                     // Global ID as FLOAT8.
	ObjectType                 null.String   `json:"object_type"`                   // Object type as TEXT.
	AddressX                   null.String   `json:"address_x"`                     // Address X as TEXT.
	MunicipalDistrict1         null.String   `json:"municipal_district_1"`          // Municipal district 1 as TEXT.
	PlanningElementName        null.String   `json:"planning_element_name"`         // Planning element name as TEXT.
	HouseOwnershipNumberType   null.String   `json:"house_ownership_number_type"`   // House ownership number type as TEXT.
	IntraCityArea              null.String   `json:"intra_city_area"`               // Intra city area as TEXT.
	AdmArea                    null.String   `json:"adm_area"`                      // ADM area as TEXT.
	District1                  null.String   `json:"district_1"`                    // District 1 as TEXT.
	NREG                       null.String   `json:"nreg"`                          // NREG as TEXT.
	DREG                       null.String   `json:"dreg"`                          // DREG as TEXT.
	NFIAS                      null.String   `json:"nfias"`                         // NFIA as TEXT.
	DFIAS                      null.String   `json:"dfias"`                         // DFA as TEXT.
	KADN                       null.String   `json:"kadn"`                          // KADN as TEXT.
	KADZU                      null.String   `json:"kadzu"`                         // KADZU as TEXT.
	KLADR                      null.String   `json:"kladr"`                         // KLADR as TEXT.
	TDOC                       null.String   `json:"tdoc"`                          // TDOC as TEXT.
	NDOC                       null.String   `json:"ndoc"`                          // NDOC as TEXT.
	DDOC                       null.String   `json:"ddoc"`                          // DDOC as TEXT.
	AddrType                   null.String   `json:"addr_type"`                     // Address type as TEXT.
	VID                        null.String   `json:"vid"`                           // VID as TEXT.
	SOSTAD                     null.String   `json:"sostad"`                        // SOSTAD as TEXT.
	Status                     null.String   `json:"status"`                        // Status as TEXT.
	GeoData                    [][][]float64 `json:"geo_data"`                      // Geo data as DOUBLE PRECISION[][][]. Simplified representation.
	GeoDataCenter              []float64     `json:"geo_data_center"`               // Geo data center as DOUBLE PRECISION[]. Simplified representation.
	IDODS                      null.Float    `json:"idods"`                         // ID ODS as FLOAT8.
	PhoneNumber                null.String   `json:"phone_number"`                  // Phone number as TEXT.
}
