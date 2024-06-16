package middleware

import (
	"lct/pkg/log"
	"lct/pkg/security"
)

type Middleware struct {
	logger  *log.Logs
	jwtUtil security.JWTUtil
}

func InitMiddleware(logger *log.Logs, jwtUtil security.JWTUtil) Middleware {
	return Middleware{
		logger:  logger,
		jwtUtil: jwtUtil,
	}
}
