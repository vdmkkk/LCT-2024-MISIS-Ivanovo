package security

import (
	"github.com/golang-jwt/jwt/v4"
	"github.com/spf13/viper"
	"lct/pkg/config"
	"time"
)

const (
	Corporative = "corporative"
	Mobile      = "mobile"
	General     = "general"
)

type JWTUtil struct {
	expireTimeOut time.Duration
	secret        string
}

func InitJWTUtil() JWTUtil {
	return JWTUtil{
		expireTimeOut: time.Duration(1000 * time.Hour),
		secret:        viper.GetString(config.Secret),
	}
}

type userClaim struct {
	jwt.RegisteredClaims
	ID       int
	UserType string
}

func (j JWTUtil) CreateToken(id int) string {
	expiredAt := time.Now().Add(j.expireTimeOut)

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, userClaim{
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: &jwt.NumericDate{
				Time: expiredAt,
			},
		},
		ID: id,
	})

	signedString, _ := token.SignedString([]byte(j.secret))

	return signedString
}

func (j JWTUtil) Authorize(tokenString string) (bool, error) {
	var userClaim userClaim

	token, err := jwt.ParseWithClaims(tokenString, &userClaim, func(token *jwt.Token) (interface{}, error) {
		return []byte(j.secret), nil
	})
	if err != nil {
		return false, err
	}

	if !token.Valid {
		return false, nil
	}

	return true, nil
}
