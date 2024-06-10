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
