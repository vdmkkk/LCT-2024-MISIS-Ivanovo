package repository

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	GetAll(ctx context.Context) ([]models.GeoData, error)
	GetByUNOM(ctx context.Context, unom int) (models.GeoData, error)
	GetByCount(ctx context.Context, count int) ([]models.GeoData, error)
}
