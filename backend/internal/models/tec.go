package models

import "github.com/guregu/null/v5"

type Tec struct {
	Name        null.String `json:"name"`
	Address     null.String `json:"address"`
	PhoneNumber null.String `json:"phone_number"`
	Coordinates []float64   `json:"coordinates"`
}
