package repository

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	GetAll(ctx context.Context) ([]models.BuildingGeoData, error)
	GetByUNOM(ctx context.Context, unom int) (models.BuildingGeoData, error)
	GetByCount(ctx context.Context, count int) ([]models.BuildingGeoData, error)
	GetByFiltersWithBuildings(ctx context.Context, filters models.GeoDataFilter) (map[string]map[string]models.ResultGeoData, error)
}

type Building interface {
	GetByUNOM(ctx context.Context, unom int) (models.Building, error)
	GetByCTPID(ctx context.Context, ctpID string) ([]models.Building, error)
}

type Ctp interface {
	GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error)
}

type Incident interface {
	GetAll(ctx context.Context) ([]models.IncidentShowUp, error)
	GetByID(ctx context.Context, id int) (models.Incident, error)
	Create(ctx context.Context, processedIncident models.Incident) (int, error)
	GetAllByUNOM(ctx context.Context, unom int) ([]models.Incident, error)
	UpdatePayload(ctx context.Context, incidentUpdate models.IncidentUpdate) error
}

type MlPredict interface {
	GetByUNOMAndDate(ctx context.Context, unom int, datetime string) ([]float64, error)
	SavePredictsFromDate(ctx context.Context, startDate string) error
}
