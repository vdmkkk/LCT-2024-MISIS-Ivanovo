package repository

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/jmoiron/sqlx"
	"lct/internal/models"
)

type geoDataRepo struct {
	db *sqlx.DB
}

func InitGeoDataRepo(db *sqlx.DB) GeoData {
	return geoDataRepo{db: db}
}

func flatMap(input [][][][]float64) *[][][]float64 {
	output := make([][][]float64, 0, len(input))
	for _, firstDimVal := range input {
		for _, secondDimVal := range firstDimVal {
			output = append(output, secondDimVal)
		}
	}

	return &output
}

func (g geoDataRepo) GetAll(ctx context.Context) ([]models.GeoData, error) {
	rows, err := g.db.QueryContext(ctx, `SELECT id, unom, to_json(coordinates) FROM geolocations;`)
	if err != nil {
		return nil, err
	}

	var geoDatas []models.GeoData
	for rows.Next() {
		var geoData models.GeoData
		var coordinatesJSON []byte
		err = rows.Scan(&geoData.ID, &geoData.Unom, &coordinatesJSON)
		if err != nil {
			return nil, err
		}
		err = json.Unmarshal(coordinatesJSON, &geoData.Coordinates)
		if err != nil {
			var coordinatesFourDims [][][][]float64
			err = json.Unmarshal(coordinatesJSON, &coordinatesFourDims)
			if err != nil {
				return nil, err
			}

			geoData.Coordinates = *flatMap(coordinatesFourDims)
		}

		geoDatas = append(geoDatas, geoData)
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return geoDatas, nil
}

func (g geoDataRepo) GetByCount(ctx context.Context, count int) ([]models.GeoData, error) {
	rows, err := g.db.QueryContext(ctx, `SELECT id, unom, to_json(coordinates) FROM geolocations LIMIT $1;`, count)
	if err != nil {
		return nil, err
	}

	var geoDatas []models.GeoData
	for rows.Next() {
		var geoData models.GeoData
		var coordinatesJSON []byte
		err = rows.Scan(&geoData.ID, &geoData.Unom, &coordinatesJSON)
		if err != nil {
			return nil, err
		}

		err = json.Unmarshal(coordinatesJSON, &geoData.Coordinates)
		if err != nil {
			var coordinatesFourDims [][][][]float64
			err = json.Unmarshal(coordinatesJSON, &coordinatesFourDims)
			if err != nil {
				return nil, err
			}

			geoData.Coordinates = *flatMap(coordinatesFourDims)
		}

		geoDatas = append(geoDatas, geoData)
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return geoDatas, nil
}

func (g geoDataRepo) GetByUNOM(ctx context.Context, unom int) (models.GeoData, error) {
	row := g.db.QueryRowContext(ctx, `SELECT id, unom, to_json(coordinates) FROM geolocations WHERE unom = $1;`, unom)

	var geoData models.GeoData
	var coordinatesJSON []byte

	err := row.Scan(&geoData.ID, &geoData.Unom, &coordinatesJSON)
	if err != nil {
		return models.GeoData{}, err
	}

	fmt.Printf("Coordinates JSON: %s\n", coordinatesJSON)

	err = json.Unmarshal(coordinatesJSON, &geoData.Coordinates)
	if err != nil {
		var coordinatesFourDims [][][][]float64
		err = json.Unmarshal(coordinatesJSON, &coordinatesFourDims)
		if err != nil {
			return models.GeoData{}, err
		}

		geoData.Coordinates = *flatMap(coordinatesFourDims)
	}

	return geoData, nil
}
