package handlers

import (
	"context"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"lct/internal/service"
	"lct/pkg/config"
	"net/http"
	"strconv"
	"time"
)

type BuildingHandler struct {
	buildingServ service.Building
}

func InitBuildingHandler(buildingServ service.Building) BuildingHandler {
	return BuildingHandler{
		buildingServ: buildingServ,
	}
}

// @Summary Get building
// @Tags building
// @Accept  json
// @Produce  json
// @Param unom query int true "unom"
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /building [get]
func (b BuildingHandler) GetByUNOM(c *gin.Context) {
	unomRaw := c.Query("unom")
	unom, err := strconv.Atoi(unomRaw)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	building, err := b.buildingServ.GetByUNOM(ctx, unom)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, building)
}

// @Summary Get buildings by ctp
// @Tags building
// @Accept  json
// @Produce  json
// @Param ctp query string true "ctp"
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /building/by_ctp [get]
func (b BuildingHandler) GetByCTPID(c *gin.Context) {
	ctp := c.Query("ctp")
	if ctp == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no ctp provided"})
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	buildings, err := b.buildingServ.GetByCTPID(ctx, ctp)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, buildings)
}
