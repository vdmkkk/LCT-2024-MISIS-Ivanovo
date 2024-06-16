package handlers

import (
	"context"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"lct/internal/service"
	"lct/pkg/config"
	"net/http"
	"time"
)

type MlPredictHandler struct {
	mlPredictService service.MlPredict
}

func InitMlPredictHandler(mlPredictServ service.MlPredict) MlPredictHandler {
	return MlPredictHandler{
		mlPredictService: mlPredictServ,
	}
}

// @Summary Save predicts from two weeks before start date and two weeks after
// @Tags ml
// @Accept  json
// @Produce  json
// @Param start_date query string true "Incident create"
// @Success 200 {object} int "Successfully"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /ml_predict_write [post]
func (m MlPredictHandler) SavePredictsFromDate(c *gin.Context) {
	date := c.Query("start_date")

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	err := m.mlPredictService.SavePredictsFromDate(ctx, date)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusOK)
}
