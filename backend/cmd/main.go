package main

import (
	"bytes"
	"fmt"
	"github.com/jmoiron/sqlx"
	"github.com/pressly/goose/v3"
	"github.com/spf13/viper"
	"io/ioutil"
	"lct/internal/delivery"
	"lct/pkg/config"
	"lct/pkg/database"
	"lct/pkg/log"
	"net/http"
)

func applyMigrations(db *sqlx.DB) {
	goose.SetBaseFS(nil)
	migrationsDir := "../deploy/migrations"

	if err := goose.Up(db.DB, migrationsDir); err != nil {
		fmt.Printf("error while applying migrations: %v", err.Error())
	}
}

func loadTecs() {
	url := fmt.Sprintf("http://%v:8001/upload_file/tecs/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjIxNDM4NzcsIklEIjoxLCJVc2VyVHlwZSI6IiJ9.4Dvv-2I4sFpwsBMEJA3HTjyh8PrbEtfgXikDx54xXog", viper.GetString(config.MlAppHost))
	method := "POST"

	client := &http.Client{}
	req, err := http.NewRequest(method, url, bytes.NewBuffer([]byte("")))
	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("accept", "application/json")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}

	if res.StatusCode != 200 {
		body, err := ioutil.ReadAll(res.Body)
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Printf("error while uploadint tecs: %v", string(body))
	}
	defer res.Body.Close()
}

func main() {
	config.InitConfig()

	logger, infoLogFile, errorLogFile := log.InitLogger()
	defer func() {
		infoLogFile.Close()
		errorLogFile.Close()
	}()

	// TODO: startup things

	db := database.MustGetDB()

	applyMigrations(db)
	loadTecs()

	delivery.Start(db, logger)
}
