package service

import (
	"context"
	"lct/internal/models"
	"lct/internal/repository"
	"lct/pkg/log"
	"math/rand"
)

type incidentServ struct {
	incidentRepo repository.Incident
	ctpRepo      repository.Ctp
	buildingRepo repository.Building
	logs         *log.Logs
}

func InitIncidentService(incidentRepo repository.Incident, ctpRepo repository.Ctp, buildingRepo repository.Building,
	logs *log.Logs) Incident {
	return incidentServ{
		incidentRepo: incidentRepo,
		ctpRepo:      ctpRepo,
		buildingRepo: buildingRepo,
		logs:         logs,
	}
}

func imitateMLProcessing(input []int) []models.HandledUnom {
	res := make([]models.HandledUnom, 0, len(input))
	for _, v := range input {
		var handledUnom models.HandledUnom
		handledUnom.Unom = v
		handledUnom.HoursToCool = rand.Intn(40)
		handledUnom.PriorityGroup = rand.Intn(4)
		if handledUnom.PriorityGroup == 0 {
			handledUnom.PriorityGroup = 1
		}

		res = append(res, handledUnom)
	}

	return res
}

func (i incidentServ) Create(ctx context.Context, createIncident models.IncidentCreate) (int, error) {
	var incident models.Incident

	incident.Payload = createIncident.Payload

	if createIncident.CtpID != "" {
		ctp, err := i.ctpRepo.GetByCTPID(ctx, createIncident.CtpID)
		if err != nil {
			i.logs.Error(err.Error())
			return 0, err
		}

		incident.Coordinates = ctp.Center
		incident.CtpID = createIncident.CtpID

		buildings, err := i.buildingRepo.GetByCTPID(ctx, createIncident.CtpID)
		if err != nil {
			i.logs.Error(err.Error())
			return 0, err
		}

		unomsToProcess := make([]int, 0, len(buildings))
		for _, v := range buildings {
			unomsToProcess = append(unomsToProcess, v.Unom)
		}

		incident.HandledUnoms = imitateMLProcessing(unomsToProcess)
	} else {
		building, err := i.buildingRepo.GetByUNOM(ctx, createIncident.Unom)
		if err != nil {
			i.logs.Error(err.Error())
			return 0, err
		}

		incident.Coordinates = building.GeoDataCenter

		incident.HandledUnoms = imitateMLProcessing([]int{building.Unom})
	}

	incidentID, err := i.incidentRepo.Create(ctx, incident)
	if err != nil {
		i.logs.Error(err.Error())
		return 0, err
	}

	return incidentID, nil
}

func (i incidentServ) GetAll(ctx context.Context) ([]models.IncidentShowUp, error) {
	incidents, err := i.incidentRepo.GetAll(ctx)
	if err != nil {
		i.logs.Error(err.Error())
		return nil, err
	}

	return incidents, nil
}

func (i incidentServ) GetByID(ctx context.Context, id int) (models.Incident, error) {
	incident, err := i.incidentRepo.GetByID(ctx, id)
	if err != nil {
		i.logs.Error(err.Error())
		return models.Incident{}, err
	}

	return incident, nil
}
