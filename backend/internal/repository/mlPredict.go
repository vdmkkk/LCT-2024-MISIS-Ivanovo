package repository

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	"github.com/spf13/viper"
	"io/ioutil"
	"lct/pkg/config"
	"net/http"
	"net/url"
	"strconv"
	"time"
)

type mlPredict struct {
	db *sqlx.DB
}

func InitMlPredictRepo(db *sqlx.DB) MlPredict {
	return mlPredict{db: db}
}

func (m mlPredict) GetByUNOMAndDate(ctx context.Context, unom int, datetime string) ([]float64, error) {
	query := `SELECT to_json(probabilites) FROM ml_predict WHERE unom = $1 AND datetime = $2`

	row := m.db.QueryRowContext(ctx, query, unom, datetime)

	var probabilitiesJSON []byte
	err := row.Scan(&probabilitiesJSON)
	if err != nil {
		return nil, err
	}

	var probabilities []float64

	err = json.Unmarshal(probabilitiesJSON, &probabilities)
	if err != nil {
		return nil, err
	}

	return probabilities, nil
}

func getFromMLService(date string) (map[string][]float64, error) {
	baseUrl := fmt.Sprintf("http://%v:8000/predict_all/", viper.GetString(config.MlAppHost))

	params := url.Values{}
	params.Add("date", date)

	fullURL := fmt.Sprintf("%s?%s", baseUrl, params.Encode())

	req, err := http.NewRequest("POST", fullURL, bytes.NewBuffer([]byte("")))
	if err != nil {
		return nil, fmt.Errorf("error creating request: %v", err)
	}

	client := &http.Client{}

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %v", err)
	}

	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %v", err)
	}

	probs := map[string][]float64{}

	err = json.Unmarshal(body, &probs)
	if err != nil {
		fmt.Println(string(body))
		return nil, fmt.Errorf("error unmarshalling JSON: %v", err)
	}

	return probs, nil
}

func (m mlPredict) SaveProbsByUnomAndDate(ctx context.Context, unom int, date string, probs []float64) error {
	query := `INSERT INTO ml_predict (unom, datetime, probabilites) VALUES ($1, $2, $3)`

	_, err := m.db.ExecContext(ctx, query, unom, date, pq.Array(probs))
	if err != nil {
		return err
	}

	return nil
}

// 2024-06-13T23:59:59
func (m mlPredict) SavePredictsFromDate(ctx context.Context, startDate string) error {
	layout := "2006-01-02T15:04:05"
	inputDate, err := time.Parse(layout, startDate)
	if err != nil {
		return fmt.Errorf("error parsing date: %v", err)
	}

	beforeStartDate := inputDate.AddDate(0, 0, -14)
	endDate := inputDate.AddDate(0, 0, 14)

	for date := beforeStartDate; !date.After(endDate); date = date.AddDate(0, 0, 1) {
		formattedTime := date.Format(layout)

		probs, err := getFromMLService(formattedTime)
		if err != nil {
			return err
		}

		for key, val := range probs {
			unom, err := strconv.Atoi(key)
			if err != nil {
				return err
			}

			err = m.SaveProbsByUnomAndDate(ctx, unom, formattedTime, val)
		}
	}

	return nil
}
