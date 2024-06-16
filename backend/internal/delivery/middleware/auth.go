package middleware

import (
	"errors"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
	"net/http"
	"strings"
)

func (m Middleware) Authorization() gin.HandlerFunc {
	return func(c *gin.Context) {
		auth := c.GetHeader("Authorization")
		if !strings.Contains(auth, "Bearer") {
			m.logger.Info(fmt.Sprintf("unathorized (NO JWT) access at: %v", c.Request.URL.Path))
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": "no bearer provided in authorization"})
			return
		}

		jwtToken := strings.Split(auth, " ")[1]

		isAccessed, err := m.jwtUtil.Authorize(jwtToken)
		if errors.Is(err, jwt.ErrTokenExpired) {
			m.logger.Info(fmt.Sprintf("token expired at: %v", c.Request.URL.Path))
			c.AbortWithStatusJSON(http.StatusUpgradeRequired, gin.H{"detail": "JWT expired"})
			return
		}
		if err != nil {
			m.logger.Error(fmt.Sprintf("token parse error at: %v", c.Request.URL.Path))
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": "error on parsing JWT"})
			return
		}

		if !isAccessed {
			m.logger.Info(fmt.Sprintf("error on authorizing access JWT at: %v", c.Request.URL.Path))
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"detail": "error on authorizing access JWT"})
			return
		}

		c.Next()
	}
}
