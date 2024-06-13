package service

import (
	"context"
	"lct/internal/repository"
	"lct/pkg/log"
)

type mlPredictService struct {
	logs          *log.Logs
	mlPredictRepo repository.MlPredict
}

func InitMlPredictService(logs *log.Logs, mlPredictRepo repository.MlPredict) MlPredict {
	return mlPredictService{
		logs:          logs,
		mlPredictRepo: mlPredictRepo,
	}
}

func (m mlPredictService) SavePredictsFromDate(ctx context.Context, startDate string) error {
	err := m.mlPredictRepo.SavePredictsFromDate(ctx, startDate)
	if err != nil {
		m.logs.Error(err.Error())
		return err
	}

	return nil
}
