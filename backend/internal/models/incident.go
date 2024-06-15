package models

type IncidentShowUp struct {
	ID          int       `json:"id"`
	Coordinates []float64 `json:"coordinates"`
	CtpID       string    `json:"ctp_id"`
}

type HandledUnom struct {
	Unom          int `json:"unom"`
	HoursToCool   int `json:"hours"`
	PriorityGroup int `json:"Rank"`
}

type IncidentBase struct {
	CtpID   string      `json:"ctp_id"`
	Payload interface{} `json:"payload"`
}

type Incident struct {
	ID           int           `json:"id"`
	Coordinates  []float64     `json:"coordinates"`
	HandledUnoms []HandledUnom `json:"handled_unoms"`
	CtpCenter    []float64     `json:"ctp_center"`
	IncidentBase
}

type IncidentCreate struct {
	Unom int
	IncidentBase
}

type IncidentUpdate struct {
	ID      int         `json:"id"`
	Payload interface{} `json:"payload"`
}
