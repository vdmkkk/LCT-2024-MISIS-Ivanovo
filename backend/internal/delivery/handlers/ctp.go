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

type CtpHandler struct {
	ctpServ service.Ctp
}

func InitCtpHandler(ctpServ service.Ctp) CtpHandler {
	return CtpHandler{
		ctpServ: ctpServ,
	}
}

// @Summary Get ctp
// @Tags ctp
// @Accept  json
// @Produce  json
// @Param ctp_id query string true "ctp_id STRING"
// @Param Authorization header string true "Insert your access token" default(Bearer <Add access token here>)
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /ctp [get]
func (ct CtpHandler) GetByCTPID(c *gin.Context) {
	ctpID := c.Query("ctp_id")
	if ctpID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no ctp_id given"})
		return
	}

	ctx := c.Request.Context()
	ctx, cancel := context.WithTimeout(ctx, time.Duration(viper.GetInt(config.TimeOut))*time.Millisecond)
	defer cancel()

	geoDatas, err := ct.ctpServ.GetByCTPID(ctx, ctpID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, geoDatas)
}
