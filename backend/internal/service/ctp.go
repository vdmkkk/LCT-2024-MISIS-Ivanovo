package service

import (
	"context"
	"lct/internal/models"
	"lct/internal/repository"
	"lct/pkg/log"
)

type ctpService struct {
	repo repository.Ctp
	logs *log.Logs
}

func InitCtpService(repo repository.Ctp, logs *log.Logs) Ctp {
	return ctpService{
		repo: repo,
		logs: logs,
	}
}

func (c ctpService) GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error) {
	ctp, err := c.repo.GetByCTPID(ctx, ctpID)
	if err != nil {
		c.logs.Error(err.Error())
		return models.Ctp{}, err
	}

	return ctp, nil
}
