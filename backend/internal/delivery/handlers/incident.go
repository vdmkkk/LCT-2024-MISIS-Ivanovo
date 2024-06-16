package handlers

import (
	"context"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"lct/internal/models"
	"lct/internal/service"
	"lct/pkg/config"
	"net/http"
	"strconv"
	"time"
)

type IncidentHandler struct {
	incidentServ service.Incident
}

func InitIncidentHandler(incidentServ service.Incident) IncidentHandler {
	return IncidentHandler{
		incidentServ: incidentServ,
	}
}

// @Summary Create incident
// @Tags incident
// @Accept  json
// @Produce  json
// @Param data body models.IncidentCreate true "Incident create"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /incident [post]
func (i IncidentHandler) Create(c *gin.Context) {
	var incidentCreate models.IncidentCreate

	if err := c.ShouldBindJSON(&incidentCreate); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	incidentID, err := i.incidentServ.Create(ctx, incidentCreate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, incidentID)
}

// @Summary Get all incidents
// @Tags incident
// @Accept  json
// @Produce  json
// @Success 200 {object} []models.IncidentShowUp "Successfully"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /incident/all [get]
func (i IncidentHandler) GetAll(c *gin.Context) {
	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	incidents, err := i.incidentServ.GetAll(ctx)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, incidents)
}

// @Summary Get incident by ID
// @Tags incident
// @Accept  json
// @Produce  json
// @Param id query int true "Incident create"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Success 200 {object} models.Incident "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /incident [get]
func (i IncidentHandler) GetByID(c *gin.Context) {
	idRaw := c.Query("id")
	id, err := strconv.Atoi(idRaw)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no valid id provided"})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	incident, err := i.incidentServ.GetByID(ctx, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, incident)
}

// @Summary Get incidents by unom
// @Tags incident
// @Accept  json
// @Produce  json
// @Param unom query int true "Unom"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Success 200 {object} []models.Incident "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /incidents_by_unom [get]
func (i IncidentHandler) GetByUNOM(c *gin.Context) {
	unomRaw := c.Query("unom")
	unom, err := strconv.Atoi(unomRaw)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no valid id provided"})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	incidents, err := i.incidentServ.GetAllByUNOM(ctx, unom)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, incidents)
}

// @Summary Update incident payload
// @Tags incident
// @Accept  json
// @Produce  json
// @Param data body models.IncidentUpdate true "Incident update"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /incident [put]
func (i IncidentHandler) Update(c *gin.Context) {
	var incidentUpdate models.IncidentUpdate

	if err := c.ShouldBindJSON(&incidentUpdate); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	err := i.incidentServ.UpdatePayload(ctx, incidentUpdate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusOK)
}
