package repository

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	GetAll(ctx context.Context) ([]models.BuildingGeoData, error)
	GetByUNOM(ctx context.Context, unom int) (models.BuildingGeoData, error)
	GetByCount(ctx context.Context, count int) ([]models.BuildingGeoData, error)
	GetByOneFilter(ctx context.Context, filters models.GeoDataFilter) (map[string]models.ResultGeoData, error)
	GetByTwoFilters(ctx context.Context, filters models.GeoDataFilter) (map[string]map[string]models.ResultGeoData, error)
}

type Building interface {
	GetByUNOM(ctx context.Context, unom int) (models.Building, error)
	GetByCTPID(ctx context.Context, ctpID string) ([]models.Building, error)
}

type Ctp interface {
	GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error)
}
