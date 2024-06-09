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

type GeoDataHandler struct {
	geoDataServ service.GeoData
}

func InitGeoDataHandler(geoDataServ service.GeoData) GeoDataHandler {
	return GeoDataHandler{
		geoDataServ: geoDataServ,
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
