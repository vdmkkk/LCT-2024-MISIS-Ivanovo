package service

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/spf13/viper"
	"lct/internal/models"
	"lct/internal/repository"
	"lct/pkg/config"
	"lct/pkg/log"
	"math/rand"
	"net/http"
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

func mlProcessing(unomsToProcess []int) ([]models.HandledUnom, error) {
	res := make([]models.HandledUnom, 0, len(unomsToProcess))

	url := fmt.Sprintf("http://%v:8000/ccalc_cooldown/", viper.GetString(config.MlAppHost))

	jsonData, err := json.Marshal(res)
	if err != nil {
		return nil, fmt.Errorf("error marshalling data:", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("error creating request:", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error making request:", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("error: received non-200 response status:", resp.Status)
	}

	err = json.NewDecoder(resp.Body).Decode(&res)
	if err != nil {
		return nil, fmt.Errorf("error decoding response:", err)
	}

	return res, nil
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

		incident.HandledUnoms, err = mlProcessing(unomsToProcess)
		if err != nil {
			i.logs.Error(err.Error())
			return 0, err
		}
	} else {
		building, err := i.buildingRepo.GetByUNOM(ctx, createIncident.Unom)
		if err != nil {
			i.logs.Error(err.Error())
			return 0, err
		}

		incident.Coordinates = building.GeoDataCenter

		incident.HandledUnoms, err = mlProcessing([]int{building.Unom})
		if err != nil {
			i.logs.Error(err.Error())
			return 0, err
		}
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

func (i incidentServ) GetAllByUNOM(ctx context.Context, unom int) ([]models.Incident, error) {
	incidents, err := i.incidentRepo.GetAllByUNOM(ctx, unom)
	if err != nil {
		i.logs.Error(err.Error())
		return nil, err
	}

	return incidents, nil
}
