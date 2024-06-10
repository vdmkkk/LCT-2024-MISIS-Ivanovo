package models

import "github.com/guregu/null/v5"

type Building struct {
	Unom                       int           // Unom is the primary key.
	Ctp                        null.String   // Ctp is a varchar(255).
	ExternalSystemAddress      null.String   // External system address as TEXT.
	ExternalSystemID           null.Float    // External system ID as FLOAT8.
	BTIAddress                 null.String   // BTI address as TEXT.
	District                   null.String   // District as TEXT.
	Area                       null.String   // Area as TEXT.
	ProjectSeries              null.String   // Project series as TEXT.
	NumberOfFloors             null.Float    // Number of floors as FLOAT8.
	NumberOfEntrances          null.Float    // Number of entrances as FLOAT8.
	NumberOfApartments         null.Float    // Number of apartments as FLOAT8.
	TotalArea                  null.Float    // Total area as FLOAT8.
	TotalResidentialArea       null.Float    // Total residential area as FLOAT8.
	TotalNonResidentialArea    null.Float    // Total non-residential area as TEXT (using null.Float for potential NULL value).
	WearAndTearBTI             null.String   // Wear and tear BTI as TEXT.
	WallMaterials              null.String   // Wall materials as TEXT.
	EmergencyStatus            null.Float    // Emergency status as FLOAT8.
	NumberOfPassengerElevators null.Float    // Number of passenger elevators as FLOAT8.
	NumberOfFreightElevators   null.Float    // Number of freight elevators as FLOAT8.
	RoofCleaningPriority       null.String   // Roof cleaning priority as TEXT.
	RoofMaterials              null.String   // Roof materials as TEXT.
	HousingFundTypes           null.Float    // Housing fund types as FLOAT8.
	MKDStatuses                null.Float    // MKD statuses as FLOAT8.
	Consumers                  null.String   // Consumers as TEXT.
	GroupType                  null.String   // Group type as TEXT.
	CentralHeating             null.String   // Central heating as TEXT.
	MeterBrand                 null.String   // Meter brand as TEXT.
	MeterSerialNumber          null.String   // Meter serial number as TEXT.
	IDUU                       null.Float    // ID UU as FLOAT8.
	FullAddress                null.String   // Full address as TEXT.
	OdsNumber                  null.String   // ODS number as TEXT.
	OdsAddress                 null.String   // ODS address as TEXT.
	SerialNumber               null.String   // Serial number as TEXT.
	City                       null.String   // City as TEXT.
	AdministrativeDistrict     null.String   // Administrative district as TEXT.
	MunicipalDistrict          null.String   // Municipal district as TEXT.
	Locality                   null.String   // Locality as TEXT.
	Street                     null.String   // Street as TEXT.
	HouseNumberType            null.String   // House number type as TEXT.
	HouseNumber                null.String   // House number as TEXT.
	BuildingNumber             null.String   // Building number as TEXT.
	StructureNumberType        null.String   // Structure number type as TEXT.
	StructureNumber            null.String   // Structure number as TEXT.
	UNAD                       null.Float    // UNAD as FLOAT8.
	Material                   null.String   // Material as TEXT.
	Purpose                    null.String   // Purpose as TEXT.
	Class                      null.String   // Class as TEXT.
	Type                       null.String   // Type as TEXT.
	Sign                       null.String   // Sign as TEXT.
	GlobalID                   null.Float    // Global ID as FLOAT8.
	ObjectType                 null.String   // Object type as TEXT.
	AddressX                   null.String   // Address X as TEXT.
	MunicipalDistrict1         null.String   // Municipal district 1 as TEXT.
	PlanningElementName        null.String   // Planning element name as TEXT.
	HouseOwnershipNumberType   null.String   // House ownership number type as TEXT.
	IntraCityArea              null.String   // Intra city area as TEXT.
	AdmArea                    null.String   // ADM area as TEXT.
	District1                  null.String   // District 1 as TEXT.
	NREG                       null.String   // NREG as TEXT.
	DREG                       null.String   // DREG as TEXT.
	NFIAS                      null.String   // NFIA as TEXT.
	DFIAS                      null.String   // DFA as TEXT.
	KADN                       null.String   // KADN as TEXT.
	KADZU                      null.String   // KADZU as TEXT.
	KLADR                      null.String   // KLADR as TEXT.
	TDOC                       null.String   // TDOC as TEXT.
	NDOC                       null.String   // NDOC as TEXT.
	DDOC                       null.String   // DDOC as TEXT.
	AddrType                   null.String   // Address type as TEXT.
	VID                        null.String   // VID as TEXT.
	SOSTAD                     null.String   // SOSTAD as TEXT.
	Status                     null.String   // Status as TEXT.
	GeoData                    [][][]float64 // Geo data as DOUBLE PRECISION[][][]. Simplified representation.
	GeoDataCenter              []float64     // Geo data center as DOUBLE PRECISION[]. Simplified representation.
	IDODS                      null.Float    // ID ODS as FLOAT8.
	PhoneNumber                null.String   // Phone number as TEXT.
}
