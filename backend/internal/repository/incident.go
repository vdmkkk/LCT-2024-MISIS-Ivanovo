package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	"lct/internal/models"
)

type incidentRepo struct {
	db *sqlx.DB
}

func InitIncidentRepo(db *sqlx.DB) Incident {
	return incidentRepo{db: db}
}

func (i incidentRepo) createUnomIncidentRelation(ctx context.Context, tx *sql.Tx, unomID int, incidentID int) error {
	relationQuery := `INSERT INTO incidents_handled_unoms (incident_id, handled_unom) VALUES ($1, $2)`

	_, err := tx.ExecContext(ctx, relationQuery, incidentID, unomID)
	if err != nil {
		return err
	}

	return nil
}

func (i incidentRepo) createUnomsAndRelations(ctx context.Context, tx *sql.Tx, handledUnoms []models.HandledUnom, incidentID int) error {
	unomQuery := `INSERT INTO handled_unoms (unom, hours_to_cool, priority_group) VALUES ($1, $2, $3) RETURNING id;`

	for _, handledUnom := range handledUnoms {
		row := tx.QueryRowContext(ctx, unomQuery, handledUnom.Unom, handledUnom.HoursToCool, handledUnom.PriorityGroup)

		var handledUnomID int
		err := row.Scan(&handledUnomID)
		if err != nil {
			return err
		}

		err = i.createUnomIncidentRelation(ctx, tx, handledUnomID, incidentID)
		if err != nil {
			return err
		}
	}

	return nil
}

func (i incidentRepo) Create(ctx context.Context, processedIncident models.Incident) (int, error) {
	incidentQuery := `INSERT INTO incidents (coordinates, ctp_id, payload) VALUES ($1, $2, $3) RETURNING id;`

	tx, err := i.db.Begin()
	if err != nil {
		return 0, err
	}

	var payloadJSON []byte
	if processedIncident.Payload != nil {
		payloadJSON, err = json.Marshal(processedIncident.Payload)
		if err != nil {
			rbErr := tx.Rollback()
			if rbErr != nil {
				return 0, fmt.Errorf("error: %v, rollback error: %v", err, rbErr)
			}
			return 0, err
		}
	}

	row := tx.QueryRowContext(ctx, incidentQuery, pq.Array(processedIncident.Coordinates), processedIncident.CtpID, payloadJSON)

	var incidentID int
	err = row.Scan(&incidentID)
	if err != nil {
		rbErr := tx.Rollback()
		if rbErr != nil {
			return 0, fmt.Errorf("error: %v, rollback error: %v", err, rbErr)
		}
		return 0, err
	}

	err = i.createUnomsAndRelations(ctx, tx, processedIncident.HandledUnoms, incidentID)
	if err != nil {
		rbErr := tx.Rollback()
		if rbErr != nil {
			return 0, fmt.Errorf("error: %v, rollback error: %v", err, rbErr)
		}
		return 0, err
	}

	err = tx.Commit()
	if err != nil {
		return 0, err
	}

	return incidentID, nil
}

func (i incidentRepo) GetAll(ctx context.Context) ([]models.IncidentShowUp, error) {
	query := `SELECT id, to_json(coordinates), ctp_id, payload FROM incidents`

	rows, err := i.db.QueryContext(ctx, query)
	if err != nil {
		return nil, err
	}

	var incidents []models.IncidentShowUp
	for rows.Next() {
		var incident models.IncidentShowUp
		var coordinatesJSON []byte
		var payloadJSON []byte

		err = rows.Scan(&incident.ID, &coordinatesJSON, &incident.CtpID, &payloadJSON)
		if err != nil {
			return nil, err
		}

		if coordinatesJSON != nil {
			err = json.Unmarshal(coordinatesJSON, &incident.Coordinates)
			if err != nil {
				return nil, err
			}
		}

		if payloadJSON != nil {
			err = json.Unmarshal(payloadJSON, &incident.Payload)
			if err != nil {
				return nil, err
			}
		}

		incidents = append(incidents, incident)
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return incidents, nil
}

func (i incidentRepo) GetByID(ctx context.Context, id int) (models.Incident, error) {
	query := `SELECT i.id, to_json(coordinates), payload, ctp_id, hu.unom, hours_to_cool, priority_group, b.bti_address, 
       b.full_address, to_json(b.geo_data)
	FROM incidents i
	LEFT JOIN incidents_handled_unoms ihu on i.id = ihu.incident_id
	LEFT JOIN handled_unoms hu on hu.id = ihu.handled_unom
	LEFT JOIN buildings b on hu.unom = b.unom
	WHERE i.id = $1`

	rows, err := i.db.QueryContext(ctx, query, id)
	if err != nil {
		return models.Incident{}, err
	}

	var incident models.Incident
	var handledUnoms []models.HandledUnom
	for rows.Next() {
		var handledUnom models.HandledUnom
		var coordinatesJSON []byte
		var payloadJSON []byte
		var geoDataJSON []byte

		err = rows.Scan(&incident.ID, &coordinatesJSON, &payloadJSON, &incident.CtpID,
			&handledUnom.Unom, &handledUnom.HoursToCool, &handledUnom.PriorityGroup, &handledUnom.BtiAddress,
			&handledUnom.FullAddress, &geoDataJSON)
		if err != nil {
			return models.Incident{}, err
		}

		if payloadJSON != nil {
			err = json.Unmarshal(payloadJSON, &incident.Payload)
			if err != nil {
				return models.Incident{}, err
			}
		}

		if coordinatesJSON != nil {
			err = json.Unmarshal(coordinatesJSON, &incident.Coordinates)
			if err != nil {
				return models.Incident{}, err
			}
		}

		err = json.Unmarshal(geoDataJSON, &handledUnom.GeoData)
		if err != nil {
			var coordinatesFourDims [][][][]float64
			err = json.Unmarshal(geoDataJSON, &coordinatesFourDims)
			if err != nil {
				return models.Incident{}, err
			}

			handledUnom.GeoData = *FlatMap(coordinatesFourDims)
		}

		handledUnoms = append(handledUnoms, handledUnom)
	}

	incident.HandledUnoms = handledUnoms

	err = rows.Err()
	if err != nil {
		return models.Incident{}, err
	}

	return incident, nil
}

func (i incidentRepo) GetAllByUNOM(ctx context.Context, unom int) ([]models.Incident, error) {
	query := `SELECT ihu.incident_id FROM handled_unoms RIGHT JOIN incidents_handled_unoms ihu on handled_unoms.id = ihu.handled_unom
    WHERE unom = $1`

	rows, err := i.db.QueryContext(ctx, query, unom)
	if err != nil {
		return nil, err
	}

	var incidents []models.Incident
	for rows.Next() {
		var incidentID int
		err = rows.Scan(&incidentID)
		if err != nil {
			return nil, err
		}

		incident, err := i.GetByID(ctx, incidentID)
		if err != nil {
			return nil, err
		}
		incidents = append(incidents, incident)
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return incidents, nil
}

func (i incidentRepo) UpdatePayload(ctx context.Context, incidentUpdate models.IncidentUpdate) error {
	tx, err := i.db.Begin()
	if err != nil {
		return err
	}

	query := `UPDATE incidents SET payload = $2 WHERE id = $1`

	payloadJSON, err := json.Marshal(incidentUpdate.Payload)
	if err != nil {
		rbErr := tx.Rollback()
		if rbErr != nil {
			return fmt.Errorf("error: %v, rbErr: %v", err, rbErr)
		}
		return err
	}

	_, err = tx.ExecContext(ctx, query, incidentUpdate.ID, payloadJSON)
	if err != nil {
		rbErr := tx.Rollback()
		if rbErr != nil {
			return fmt.Errorf("error: %v, rbErr: %v", err, rbErr)
		}
		return err
	}

	err = tx.Commit()
	if err != nil {
		return err
	}

	return nil
}
