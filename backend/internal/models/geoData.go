package models

type GeoData struct {
	Coordinates [][][]float64 `json:"coordinates"`
}

type BuildingGeoData struct {
	Unom        int           `json:"UNOM"`
	Coordinates [][][]float64 `json:"coordinates"`
}

type CtpGeoData struct {
	CtpID  string    `json:"ctp_id"`
	Center []float64 `json:"center"`
}

type ResultGeoData struct {
	Buildings []BuildingGeoData `json:"buildings"`
	Ctps      []CtpGeoData      `json:"ctps"`
}

type GeoDataFilter struct {
	District     bool `json:"district"`
	Tec          bool `json:"tec"`
	HeatNetwork  int  `json:"heat_network"`
	ConsumerType int  `json:"consumer_type"`
}
