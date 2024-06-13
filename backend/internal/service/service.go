package service

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	GetByUNOM(ctx context.Context, unom int) (models.BuildingGeoData, error)
	GetByCount(ctx context.Context, count int) ([]models.BuildingGeoData, error)
	GetByFilter(ctx context.Context, filters models.GeoDataFilter) (map[string]models.ResultGeoData,
		map[string]map[string]models.ResultGeoData, error)
}

type Building interface {
	GetByUNOM(ctx context.Context, unom int) (models.Building, error)
	GetByCTPID(ctx context.Context, ctpID string) ([]models.Building, error)
}

type Ctp interface {
	GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error)
}

type Incident interface {
	Create(ctx context.Context, createIncident models.IncidentCreate) (int, error)
	GetAll(ctx context.Context) ([]models.IncidentShowUp, error)
	GetByID(ctx context.Context, id int) (models.Incident, error)
}

type MlPredict interface {
	SavePredictsFromDate(ctx context.Context, startDate string) error
}
