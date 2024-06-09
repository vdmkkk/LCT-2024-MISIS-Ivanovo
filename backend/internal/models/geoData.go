package models

type GeoData struct {
	ID          int           `json:"id"`
	Unom        int           `json:"UNOM"`
	Coordinates [][][]float64 `json:"coordinates"`
}
