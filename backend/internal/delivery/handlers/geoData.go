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

type GeoDataHandler struct {
	geoDataServ service.GeoData
}

func InitGeoDataHandler(geoDataServ service.GeoData) GeoDataHandler {
	return GeoDataHandler{
		geoDataServ: geoDataServ,
	}
}

// @Summary Get by filter
// @Tags geo
// @Accept  json
// @Produce  json
// @Param data body models.GeoDataFilter true "Filters"
// @Success 200 {object} int "Successfully"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /geo/by_filters [put]
func (g GeoDataHandler) GetByFilter(c *gin.Context) {
	var filters models.GeoDataFilter

	if err := c.ShouldBindJSON(&filters); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	oneFilterRes, twoFilterRes, err := g.geoDataServ.GetByFilter(ctx, filters)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if oneFilterRes != nil {
		c.JSON(http.StatusOK, oneFilterRes)
	} else if twoFilterRes != nil {
		c.JSON(http.StatusOK, twoFilterRes)
	} else {
		c.JSON(http.StatusTeapot, gin.H{"error": "no result from filters"})
		panic("WTF???")
	}
}

// @Summary Get geo datas
// @Tags geo
// @Accept  json
// @Produce  json
// @Param count query int true "How many geos to return. If 0 then returns all"
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /geo [get]
func (g GeoDataHandler) GetByCount(c *gin.Context) {
	countRaw := c.Query("count")
	count, err := strconv.Atoi(countRaw)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	geoDatas, err := g.geoDataServ.GetByCount(ctx, count)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, geoDatas)
}

// @Summary Get geo data by UNOM
// @Tags geo
// @Accept  json
// @Produce  json
// @Param unom query int true "UNOM"
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /geo/unom [get]
func (g GeoDataHandler) GetByUNOM(c *gin.Context) {
	unomRaw := c.Query("unom")
	unom, err := strconv.Atoi(unomRaw)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	geoDatas, err := g.geoDataServ.GetByUNOM(ctx, unom)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, geoDatas)
}
