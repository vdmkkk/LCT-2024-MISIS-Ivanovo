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
