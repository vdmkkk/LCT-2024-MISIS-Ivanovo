package models

type IncidentShowUp struct {
	ID          int       `json:"id"`
	Coordinates []float64 `json:"coordinates"`
}

type HandledUnom struct {
	Unom          int `json:"unom"`
	HoursToCool   int `json:"hours_to_cool"`
	PriorityGroup int `json:"priority_group"`
}

type IncidentBase struct {
	CtpID   string      `json:"ctp_id"`
	Payload interface{} `json:"payload"`
}

type Incident struct {
	ID           int           `json:"id"`
	Coordinates  []float64     `json:"coordinates"`
	HandledUnoms []HandledUnom `json:"handled_unoms"`
	IncidentBase
}

type IncidentCreate struct {
	Unom int
	IncidentBase
}
