package models

import "github.com/guregu/null/v5"

type Ctp struct {
	ID             int64       `json:"id"`
	CtpId          string      `json:"ctp_id"`
	Address        null.String `json:"address"`
	Type           null.String `json:"type"`
	PlacementType  null.String `json:"placement_type"`
	Source         null.String `json:"source"`
	Administrative null.String `json:"administrative"`
	Municipal      null.String `json:"municipal"`
	StartDate      null.String `json:"start_date"`
	BalanceHolder  null.String `json:"balance_holder"`
	Polygon        [][]float64 `json:"polygon"`
	Center         []float64   `json:"center"`
}
