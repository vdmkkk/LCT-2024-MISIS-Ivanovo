package models

import "github.com/guregu/null/v5"

type GeoData struct {
	Coordinates [][][]float64 `json:"coordinates"`
}

type BuildingGeoData struct {
	Unom        int           `json:"UNOM"`
	Coordinates [][][]float64 `json:"coordinates"`
}

type CtpGeoData struct {
	CtpID  null.String `json:"ctp_id"`
	Center []float64   `json:"center"`
}

type ResultGeoData struct {
	Buildings []BuildingWithMetaGeoData `json:"buildings"`
	Ctps      []CtpWithMetaGeoData      `json:"ctps"`
	Tecs      []Tec                     `json:"tecs"`
}

type GeoDataFilter struct {
	District     bool   `json:"district"`
	Tec          bool   `json:"tec"`
	HeatNetwork  int    `json:"heat_network"`
	ConsumerType int    `json:"consumer_type"`
	Date         string `json:"date"`
}

type BuildingWithMetaGeoData struct {
	BuildingGeoData
	Area         null.String
	Probabilites []float64 `json:"probabilites"`
}

type CtpWithMetaGeoData struct {
	CtpGeoData
	Source null.String
}
