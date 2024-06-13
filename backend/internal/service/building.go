package service

import (
	"context"
	"lct/internal/models"
	"lct/internal/repository"
	"lct/pkg/log"
)

type buidlingService struct {
	repo repository.Building
	logs *log.Logs
}

func InitBuildingService(repo repository.Building, logs *log.Logs) Building {
	return buidlingService{
		repo: repo,
		logs: logs,
	}
}

func (b buidlingService) GetByUNOM(ctx context.Context, unom int) (models.Building, error) {
	building, err := b.repo.GetByUNOM(ctx, unom)
	if err != nil {
		b.logs.Error(err.Error())
		return models.Building{}, err
	}

	return building, nil
}

func (b buidlingService) GetByCTPID(ctx context.Context, ctpID string) ([]models.Building, error) {
	buildings, err := b.repo.GetByCTPID(ctx, ctpID)
	if err != nil {
		b.logs.Error(err.Error())
		return nil, err
	}

	return buildings, nil
}
