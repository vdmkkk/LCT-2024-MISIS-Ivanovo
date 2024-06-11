package repository

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/Masterminds/squirrel"
	"github.com/guregu/null/v5"
	"github.com/jmoiron/sqlx"
	"lct/internal/models"
)

type geoDataRepo struct {
	db *sqlx.DB
}

func contains(inpt []string, elem string) bool {
	for _, val := range inpt {
		if val == elem {
			return true
		}
	}

	return false
}

func (g geoDataRepo) GetCtpGeoData(ctx context.Context, ctpID string) (models.CtpGeoData, error) {
	row := g.db.QueryRowContext(ctx, `SELECT ctp_id, to_json(center) FROM ctps WHERE ctp_id = $1`, ctpID)

	var ctpGeoData models.CtpGeoData
	var coordinatesJSON []byte

	err := row.Scan(&ctpGeoData.CtpID, &coordinatesJSON)
	if err != nil {
		return models.CtpGeoData{}, err
	}

	err = json.Unmarshal(coordinatesJSON, &ctpGeoData.Center)
	if err != nil {
		if err.Error() == "unexpected end of JSON input" {
			return ctpGeoData, nil
		}
		return models.CtpGeoData{}, err
	}

	return ctpGeoData, nil
}

func (g geoDataRepo) GetByOneFilter(ctx context.Context, filters models.GeoDataFilter) (map[string]models.ResultGeoData, error) {
	psql := squirrel.StatementBuilder.PlaceholderFormat(squirrel.Dollar)

	var queryBuilder squirrel.SelectBuilder

	if filters.District {
		queryBuilder = psql.Select("buildings.area, buildings.unom", "to_json(buildings.geo_data), ctps.ctp_id").
			From("buildings").
			LeftJoin("ctps ON buildings.ctp = ctps.ctp_id").
			OrderBy("buildings.area")
	} else if filters.Tec {
		queryBuilder = psql.Select("ctps.source, buildings.unom", "to_json(buildings.geo_data), ctps.ctp_id").
			From("buildings").
			LeftJoin("ctps ON buildings.ctp = ctps.ctp_id").
			Where("ctps.source LIKE ?", "ТЭЦ%"). // maybe 'ТЭЦ%' ??
			OrderBy("ctps.source")
	} else {
		return nil, fmt.Errorf("error no map key filters provided")
	}

	switch filters.HeatNetwork {
	case 0:
		break
	case 1:
		queryBuilder = queryBuilder.Where("ctps.type = ?", "ИТП") // maybe 'ИТП' ??
	case 2:
		queryBuilder = queryBuilder.Where("ctps.type = ?", "ЦТП") // maybe 'ЦТП' ??
	}

	switch filters.ConsumerType {
	case 1:
		break
	case 2:
		break
	case 3:
		break
	}

	query, args, err := queryBuilder.ToSql()
	if err != nil {
		return nil, err
	}

	rows, err := g.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}

	res := map[string]models.ResultGeoData{}
	var buildingsGeo []models.BuildingGeoData
	var ctpsGeo []models.CtpGeoData
	var ctpsIds []string
	var prevKey string
	for rows.Next() {
		var buildingGeo models.BuildingGeoData
		var coordinatesJSON []byte
		var ctpID null.String
		var ctpGeo models.CtpGeoData
		var key string

		err = rows.Scan(&key, &buildingGeo.Unom, &coordinatesJSON, &ctpID)
		if err != nil {
			return nil, err
		}

		if ctpID.Valid {
			if !contains(ctpsIds, ctpID.String) {
				ctpsIds = append(ctpsIds, ctpID.String)
				ctpGeo, err = g.GetCtpGeoData(ctx, ctpID.String)
				if err != nil {
					return nil, err
				}
			}
		}

		err = json.Unmarshal(coordinatesJSON, &buildingGeo.Coordinates)
		if err != nil {
			return nil, err
		}

		if prevKey == "" {
			prevKey = key
		}

		if prevKey == key {
			buildingsGeo = append(buildingsGeo, buildingGeo)
			if ctpGeo.CtpID != "" {
				ctpsGeo = append(ctpsGeo, ctpGeo)
			}
		} else {
			if filters.HeatNetwork == 3 {
				buildingsGeo = nil
			}

			if prevKey == "" {
				res["null"] = models.ResultGeoData{
					Buildings: buildingsGeo,
					Ctps:      ctpsGeo,
				}
			} else {
				res[prevKey] = models.ResultGeoData{
					Buildings: buildingsGeo,
					Ctps:      ctpsGeo,
				}
			}

			prevKey = key
			buildingsGeo = []models.BuildingGeoData{buildingGeo}
			if ctpGeo.CtpID != "" {
				ctpsGeo = []models.CtpGeoData{ctpGeo}
			}
		}
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return res, nil
}

func (g geoDataRepo) GetByTwoFilters(ctx context.Context, filters models.GeoDataFilter) (map[string]map[string]models.ResultGeoData, error) {
	//TODO implement me
	panic("implement me")
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

func (g geoDataRepo) GetAll(ctx context.Context) ([]models.BuildingGeoData, error) {
	rows, err := g.db.QueryContext(ctx, `SELECT id, unom, to_json(coordinates) FROM geolocations;`)
	if err != nil {
		return nil, err
	}

	var geoDatas []models.BuildingGeoData
	for rows.Next() {
		var geoData models.BuildingGeoData
		var coordinatesJSON []byte
		err = rows.Scan(&geoData.Unom, &coordinatesJSON)
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

func (g geoDataRepo) GetByCount(ctx context.Context, count int) ([]models.BuildingGeoData, error) {
	rows, err := g.db.QueryContext(ctx, `SELECT unom, to_json(coordinates) FROM geolocations LIMIT $1;`, count)
	if err != nil {
		return nil, err
	}

	var geoDatas []models.BuildingGeoData
	for rows.Next() {
		var geoData models.BuildingGeoData
		var coordinatesJSON []byte
		err = rows.Scan(&geoData.Unom, &coordinatesJSON)
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

func (g geoDataRepo) GetByUNOM(ctx context.Context, unom int) (models.BuildingGeoData, error) {
	row := g.db.QueryRowContext(ctx, `SELECT unom, to_json(coordinates) FROM geolocations WHERE unom = $1;`, unom)

	var geoData models.BuildingGeoData
	var coordinatesJSON []byte

	err := row.Scan(&geoData.Unom, &coordinatesJSON)
	if err != nil {
		return models.BuildingGeoData{}, err
	}

	fmt.Printf("Coordinates JSON: %s\n", coordinatesJSON)

	err = json.Unmarshal(coordinatesJSON, &geoData.Coordinates)
	if err != nil {
		var coordinatesFourDims [][][][]float64
		err = json.Unmarshal(coordinatesJSON, &coordinatesFourDims)
		if err != nil {
			return models.BuildingGeoData{}, err
		}

		geoData.Coordinates = *flatMap(coordinatesFourDims)
	}

	return geoData, nil
}
