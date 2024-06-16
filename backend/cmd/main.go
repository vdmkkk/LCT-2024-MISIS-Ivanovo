package main

import (
	"lct/internal/delivery"
	"lct/pkg/config"
	"lct/pkg/database"
	"lct/pkg/log"
)

func main() {
	config.InitConfig()

	logger, infoLogFile, errorLogFile := log.InitLogger()
	defer func() {
		infoLogFile.Close()
		errorLogFile.Close()
	}()

	// TODO: startup things

	db := database.MustGetDB()

	delivery.Start(db, logger)
}
