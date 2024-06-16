package repository

import (
	"context"
	"lct/internal/models"
)

type GeoData interface {
	// GetAll возвращает все геоданные зданий.
	GetAll(ctx context.Context) ([]models.BuildingGeoData, error)

	// GetByUNOM возвращает геоданные здания по его уникальному номеру (UNOM).
	GetByUNOM(ctx context.Context, unom int) (models.BuildingGeoData, error)

	// GetByCount возвращает указанное количество геоданных зданий.
	GetByCount(ctx context.Context, count int) ([]models.BuildingGeoData, error)

	// GetByFiltersWithBuildings возвращает геоданные зданий, ЦТП и ТЭЦ, отфильтрованные по заданным фильтрам.
	GetByFiltersWithBuildings(ctx context.Context, filters models.GeoDataFilter) (map[string]map[string]models.ResultGeoData, error)
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
	// GetAll возвращает все инциденты.
	GetAll(ctx context.Context) ([]models.IncidentShowUp, error)

	// GetByID возвращает инцидент по его идентификатору (ID).
	GetByID(ctx context.Context, id int) (models.Incident, error)

	// Create создает новый инцидент и возвращает его идентификатор.
	Create(ctx context.Context, processedIncident models.Incident) (int, error)

	// GetAllByUNOM возвращает все инциденты, связанные с заданным уникальным номером здания (UNOM).
	GetAllByUNOM(ctx context.Context, unom int) ([]models.Incident, error)

	// UpdatePayload обновляет данные инцидента.
	UpdatePayload(ctx context.Context, incidentUpdate models.IncidentUpdate) error
}

type MlPredict interface {
	// GetByUNOMAndDate возвращает предсказания по уникальному номеру здания (UNOM) и дате.
	GetByUNOMAndDate(ctx context.Context, unom int, datetime string) ([]float64, error)

	// SavePredictsFromDate сохраняет предсказания в БД, начиная с 14 дней ДО заданной даты и 14 дней ПОСЛЕ.
	SavePredictsFromDate(ctx context.Context, startDate string) error
}
