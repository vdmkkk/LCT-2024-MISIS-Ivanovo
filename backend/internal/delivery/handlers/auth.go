package handlers

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

type AuthHandler struct {
}

func InitAuthHandler() AuthHandler {
	return AuthHandler{}
}

// @Summary Login
// @Tags auth
// @Accept  json
// @Produce  json
// @Param login query string true "login"
// @Param password query string true "password"
// @Success 200 {object} int "Successfully"
// @Failure 400 {object} map[string]string "Invalid input"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /login [post]
func (a AuthHandler) Login(c *gin.Context) {
	login := c.Query("login")
	password := c.Query("password")
	if login != "admin" || password != "admin" {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "wrong password or login"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"JWT": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjIxNDM4NzcsIklEIjoxLCJVc2VyVHlwZSI6IiJ9.4Dvv-2I4sFpwsBMEJA3HTjyh8PrbEtfgXikDx54xXog"})
}
