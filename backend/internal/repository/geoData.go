package repository

import (
	"context"
	"encoding/json"
	"github.com/jmoiron/sqlx"
	"lct/internal/models"
)

type geoDataRepo struct {
	db *sqlx.DB
}

func InitGeoDataRepo(db *sqlx.DB) GeoData {
	return geoDataRepo{db: db}
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
			return nil, err
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
			return nil, err
		}

		geoDatas = append(geoDatas, geoData)
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return geoDatas, nil
}
