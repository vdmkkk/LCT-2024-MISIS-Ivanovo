package repository

import (
	"context"
	"encoding/json"
	"github.com/jmoiron/sqlx"
	"lct/internal/models"
)

type ctpRepo struct {
	db *sqlx.DB
}

func InitCtpRepo(db *sqlx.DB) Ctp {
	return ctpRepo{db: db}
}

func (c ctpRepo) GetByCTPID(ctx context.Context, ctpID string) (models.Ctp, error) {
	query := `SELECT id, ctp_id, address, type, placement_type, source, administrative, municipal, start_date, balance_holder,
		to_json(polygon), to_json(center)
	FROM ctps
	WHERE ctp_id = $1;`

	row := c.db.QueryRowContext(ctx, query, ctpID)

	var ctp models.Ctp
	var polygonJSON []byte
	var centerJSON []byte
	err := row.Scan(&ctp.ID, &ctp.CtpId, &ctp.Address, &ctp.Type, &ctp.PlacementType, &ctp.Source, &ctp.Administrative,
		&ctp.Municipal, &ctp.StartDate, &ctp.BalanceHolder, &polygonJSON, &centerJSON)
	if err != nil {
		return models.Ctp{}, err
	}

	if polygonJSON != nil {
		err = json.Unmarshal(polygonJSON, &ctp.Polygon)
		if err != nil {
			return models.Ctp{}, err
		}
	}

	if centerJSON != nil {
		err = json.Unmarshal(centerJSON, &ctp.Center)
		if err != nil {
			return models.Ctp{}, err
		}
	}

	return ctp, nil
}
