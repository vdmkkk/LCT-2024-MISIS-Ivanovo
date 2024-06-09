package service

import (
	"context"
	"lct/internal/models"
	"lct/internal/repository"
	"lct/pkg/log"
)

type geoDataService struct {
	repo repository.GeoData
	logs *log.Logs
}

func InitGeoDataService(repo repository.GeoData, logs *log.Logs) GeoData {
	return geoDataService{
		repo: repo,
		logs: logs,
	}
}

func (g geoDataService) GetByCount(ctx context.Context, count int) ([]models.GeoData, error) {
	if count == 0 {
		geoDatas, err := g.repo.GetAll(ctx)
		if err != nil {
			g.logs.Error(err.Error())
			return nil, err
		}
		return geoDatas, nil
	}

	geoDatas, err := g.repo.GetByCount(ctx, count)
	if err != nil {
		g.logs.Error(err.Error())
		return nil, err
	}
	return geoDatas, nil
}

func (g geoDataService) GetByUNOM(ctx context.Context, unom int) (models.GeoData, error) {
	geoData, err := g.repo.GetByUNOM(ctx, unom)
	if err != nil {
		g.logs.Error(err.Error())
		return models.GeoData{}, err
	}

	return geoData, nil
}
