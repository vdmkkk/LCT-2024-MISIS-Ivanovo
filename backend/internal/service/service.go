package service

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	GetByCount(ctx context.Context, count int) ([]models.GeoData, error)
}
