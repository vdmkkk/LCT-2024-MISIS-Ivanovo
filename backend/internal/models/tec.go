package models

type Tec struct {
	Name        string    `json:"name"`
	Address     string    `json:"address"`
	PhoneNumber string    `json:"phone_number"`
	Coordinates []float64 `json:"coordinates"`
}
