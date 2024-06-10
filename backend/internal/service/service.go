package service

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	GetByUNOM(ctx context.Context, unom int) (models.GeoData, error)
	GetByCount(ctx context.Context, count int) ([]models.GeoData, error)
}

type Building interface {
	GetByUNOM(ctx context.Context, unom int) (models.Building, error)
}

type Ctp interface {
	GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error)
}
