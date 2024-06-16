package service

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	// GetByUNOM возвращает геоданные здания по его уникальному номеру (UNOM).
	GetByUNOM(ctx context.Context, unom int) (models.BuildingGeoData, error)

	// GetByCount возвращает указанное количество геоданных зданий.
	GetByCount(ctx context.Context, count int) ([]models.BuildingGeoData, error)

	// GetByFilter возвращает геоданные зданий, отфильтрованные по заданным фильтрам.
	// Возвращает два набора данных: первый - основные результаты, второй - результаты, сгруппированные по дополнительным критериям.
	GetByFilter(ctx context.Context, filters models.GeoDataFilter) (map[string]models.ResultGeoData, map[string]map[string]models.ResultGeoData, error)
}

type Building interface {
	// GetByUNOM возвращает данные здания по его уникальному номеру (UNOM).
	GetByUNOM(ctx context.Context, unom int) (models.Building, error)

	// GetByCTPID возвращает данные зданий по их идентификатору CTP (CTPID).
	GetByCTPID(ctx context.Context, ctpID string) ([]models.Building, error)
}

type Ctp interface {
	// GetByCTPID возвращает данные CTP по его идентификатору (CTPID).
	GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error)
}

type Incident interface {
	// Create создает новый инцидент и возвращает его идентификатор.
	Create(ctx context.Context, createIncident models.IncidentCreate) (int, error)

	// GetAll возвращает все инциденты.
	GetAll(ctx context.Context) ([]models.IncidentShowUp, error)

	// GetByID возвращает инцидент по его идентификатору (ID).
	GetByID(ctx context.Context, id int) (models.Incident, error)

	// GetAllByUNOM возвращает все инциденты, связанные с заданным уникальным номером здания (UNOM).
	GetAllByUNOM(ctx context.Context, unom int) ([]models.Incident, error)

	// UpdatePayload обновляет данные инцидента.
	UpdatePayload(ctx context.Context, incidentUpdate models.IncidentUpdate) error
}

type MlPredict interface {
	// SavePredictsFromDate сохраняет предсказания в БД, начиная с 14 дней ДО заданной даты и 14 дней ПОСЛЕ.
	SavePredictsFromDate(ctx context.Context, startDate string) error
}
