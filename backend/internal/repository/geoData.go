package repository

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/Masterminds/squirrel"
	"github.com/jmoiron/sqlx"
	"lct/internal/models"
	"strings"
)

type geoDataRepo struct {
	db        *sqlx.DB
	mlPredict MlPredict
}

func InitGeoDataRepo(db *sqlx.DB, predict MlPredict) GeoData {
	return geoDataRepo{db: db, mlPredict: predict}
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

var mkd = []string{
	"многоквартирный дом",
	"блокированный жилой дом",
}

var social = []string{
	"общежитие",
	"детский дом культуры",
	"школьное",
	"отделение милиции",
	"ясли",
	"стоматологическая поликлиника",
	"учебно-воспитательное",
	"учреждение,мастерские",
	"музей",
	"детское дошкольное учреждение",
	"школа-интернат",
	"учебно-воспитателный комбинат",
	"спортивный павильон",
	"центр обслуживания",
	"библиотека",
	"консультативная поликлинника",
	"ясли-сад",
	"центр реабилитации",
	"гимназия",
	"наркологический диспансер",
	"отделение судебно-медицинской экспертизы",
	"блок-пристройка начальных классов",
	"лаборатория",
	"детский санаторий",
	"техническое училище",
	"спальный корпус",
	"спортивный корпус",
	"спецшкола",
	"клуб",
	"терапевтический корпус",
	"профтехучилище",
	"учебно-производственный комбинат",
	"хирургический корпус",
	"колледж",
	"подстанция скорой помощи",
	"учреждение",
	"административное",
	"выставочный павильон",
	"школа",
	"научное",
	"плавательный бассейн",
	"лечебный корпус",
	"лечебное",
	"интернат",
	"санаторий",
	"музыкальная школа",
	"столовая",
	"больница",
	"пункт охраны",
	"медучилище",
	"культурно-просветительное",
	"детсад-ясли",
	"гостиница",
	"кафе",
	"физкультурно-оздоровительный комплекс",
	"дом детского творчества",
	"спортивная школа",
	"детский сад",
	"спортивный клуб",
	"поликлиника",
	"ПТУ",
	"дом ребенка",
	"административно-бытовой",
	"пищеблок",
	"прачечная",
	"детские ясли",
	"морг",
	"родильный дом",
	"станция скорой помощи",
	"учебный корпус",
	"училище",
	"техникум",
	"школа-сад",
	"учебное",
	"диспансер",
	"лечебно-санитарное",
	"спортивный комплекс",
	"бассейн и спортзал",
	"спортивное",
}

var industrial = []string{
	"нежилое",
	"гараж",
	"ЦТП",
	"уборная",
	"хранилище",
	"склад",
	"архив",
	"дезинфекционная камера",
	"кухня клиническая",
	"хозблок",
	"трансформаторная подстанция",
	"овощехранилище",
	"нежилое,ГПТУ",
}

func (g geoDataRepo) GetByFiltersWithBuildings(ctx context.Context, filters models.GeoDataFilter) (map[string]map[string]models.ResultGeoData, error) {
	psql := squirrel.StatementBuilder.PlaceholderFormat(squirrel.Dollar)
	queryBuilder := psql.Select("b.area", "b.unom", "to_json(b.geo_data)", "c.ctp_id", "c.source",
		"to_json(c.center)", "t.name", "t.address", "t.phone_number", "to_json(t.coordinates)").
		From("buildings b").LeftJoin("ctps c on b.ctp = c.ctp_id").LeftJoin("tecs t on c.source = t.name")

	switch filters.HeatNetwork {
	case 1:
		queryBuilder = queryBuilder.Where("c.type = ?", "ИТП")
	case 2:
		queryBuilder = queryBuilder.Where("c.type = ?", "ЦТП")
	case 3:
		queryBuilder = queryBuilder.Where("c.type = ? AND c.source LIKE ?", "ЦТП", "ТЭЦ%")
	}

	switch filters.ConsumerType {
	case 1:
		queryBuilder = queryBuilder.Where("b.purpose IN ('многоквартирный дом'," +
			"'блокированный жилой дом')")
	case 2:
		queryBuilder = queryBuilder.Where("b.purpose IN ('общежитие','детский дом культуры','школьное','отделение " +
			"милиции','ясли','стоматологическая поликлиника','учебно-воспитательное','учреждение,мастерские','музей'," +
			"'детское дошкольное учреждение','школа-интернат','учебно-воспитателный комбинат','спортивный павильон'," +
			"'центр обслуживания','библиотека','консультативная поликлинника','ясли-сад','центр реабилитации','гимназия'" +
			",'наркологический диспансер','отделение судебно-медицинской экспертизы','блок-пристройка начальных классов'," +
			"'лаборатория','детский санаторий','техническое училище','спальный корпус','спортивный корпус','спецшкола'," +
			"'клуб','терапевтический корпус','профтехучилище','учебно-производственный комбинат','хирургический корпус" +
			"','колледж','подстанция скорой помощи','учреждение','административное','выставочный павильон','школа','на" +
			"учное','плавательный бассейн','лечебный корпус','лечебное','интернат','санаторий','музыкальная школа'," +
			"'столовая','больница','пункт охраны','медучилище','культурно-просветительное','детсад-ясли','гостиница'," +
			"'кафе','физкультурно-оздоровительный комплекс','дом детского творчества','спортивная школа','детский сад'," +
			"'спортивный клуб','поликлиника','ПТУ','дом ребенка','административно-бытовой','пищеблок','прачечная'," +
			"'детские ясли','морг','родильный дом','станция скорой помощи','учебный корпус','училище','техникум'," +
			"'школа-сад','учебное','диспансер','лечебно-санитарное','спортивный комплекс','бассейн и спортзал'," +
			"'спортивное')")
	case 3:
		queryBuilder = queryBuilder.Where("b.purpose IN ('нежилое','гараж','ЦТП','уборная','хранилище','склад'," +
			"'архив','дезинфекционная камера','кухня клиническая','хозблок','трансформаторная подстанция','овощехранилище'," +
			"'нежилое,ГПТУ')")
	}

	res := map[string]map[string]models.ResultGeoData{}

	query, args, err := queryBuilder.ToSql()
	if err != nil {
		return nil, err
	}

	rows, err := g.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}

	ctpIDs := map[string]struct{}{}
	for rows.Next() {
		var buildingGeo models.BuildingWithMetaGeoData
		var ctpGeo models.CtpWithMetaGeoData
		var tec models.Tec
		var coordinatesJSON []byte
		var centerJSON []byte
		var tecCoordinatesJSON []byte

		err = rows.Scan(&buildingGeo.Area, &buildingGeo.Unom, &coordinatesJSON, &ctpGeo.CtpID, &ctpGeo.Source, &centerJSON,
			&tec.Name, &tec.Address, &tec.PhoneNumber, &tecCoordinatesJSON)
		if err != nil {
			return nil, err
		}

		if !buildingGeo.Area.Valid || buildingGeo.Area.String == "" {
			buildingGeo.Area.SetValid("null")
		}
		if !ctpGeo.CtpID.Valid || ctpGeo.CtpID.String == "" {
			ctpGeo.CtpID.SetValid("null")
		}
		if !ctpGeo.Source.Valid || ctpGeo.Source.String == "" {
			ctpGeo.Source.SetValid("null")
		}

		err = json.Unmarshal(coordinatesJSON, &buildingGeo.Coordinates)
		if err != nil {
			var coordinatesFourDims [][][][]float64
			err = json.Unmarshal(coordinatesJSON, &coordinatesFourDims)
			if err != nil {
				return nil, err
			}

			buildingGeo.Coordinates = *FlatMap(coordinatesFourDims)
		}

		err = json.Unmarshal(centerJSON, &ctpGeo.Center)
		if err != nil {
			if !strings.Contains(err.Error(), "unexpected") {
				return nil, err
			}
		}

		err = json.Unmarshal(tecCoordinatesJSON, &tec.Coordinates)
		if err != nil {
			return nil, err
		}

		if filters.Date != "" {
			buildingGeo.Probabilites, err = g.mlPredict.GetByUNOMAndDate(ctx, buildingGeo.Unom, filters.Date)
			if err != nil {
				return nil, err
			}
		}

		var outerKey string
		if !filters.Tec || !filters.District {
			outerKey = "all"
		} else {
			outerKey = ctpGeo.Source.String
		}

		var innerKey string
		if filters.District {
			innerKey = buildingGeo.Area.String
		} else if filters.Tec {
			innerKey = ctpGeo.Source.String
		}
		if _, ok := res[outerKey]; !ok {
			res[outerKey] = map[string]models.ResultGeoData{}
		}
		if _, ok := res[outerKey][innerKey]; !ok {
			res[outerKey][innerKey] = models.ResultGeoData{
				Buildings: []models.BuildingWithMetaGeoData{buildingGeo},
				Ctps:      []models.CtpWithMetaGeoData{},
				Tecs:      []models.Tec{},
			}
			if ctpGeo.CtpID.Valid {
				if _, ok := ctpIDs[ctpGeo.CtpID.String]; !ok {
					elem := res[outerKey][innerKey]
					elem.Ctps = append(elem.Ctps, ctpGeo)
					if tec.Name.Valid {
						elem.Tecs = append(elem.Tecs, tec)
					}
					res[outerKey][innerKey] = elem
					ctpIDs[ctpGeo.CtpID.String] = struct{}{}
				}
			}
		} else {
			elem := res[outerKey][innerKey]
			elem.Buildings = append(elem.Buildings, buildingGeo)
			res[outerKey][innerKey] = elem
			if ctpGeo.CtpID.Valid {
				if _, ok := ctpIDs[ctpGeo.CtpID.String]; !ok {
					elem := res[outerKey][innerKey]
					elem.Ctps = append(elem.Ctps, ctpGeo)
					if tec.Name.Valid {
						elem.Tecs = append(elem.Tecs, tec)
					}
					res[outerKey][innerKey] = elem
					ctpIDs[ctpGeo.CtpID.String] = struct{}{}
				}
			}
		}
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}

	return res, nil
}

func FlatMap(input [][][][]float64) *[][][]float64 {
	output := make([][][]float64, 0, len(input))
	for _, firstDimVal := range input {
		for _, secondDimVal := range firstDimVal {
			output = append(output, secondDimVal)
		}
	}

	return &output
}

func (g geoDataRepo) GetAll(ctx context.Context) ([]models.BuildingGeoData, error) {
	rows, err := g.db.QueryContext(ctx, `SELECT unom, to_json(coordinates) FROM geolocations;`)
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

			geoData.Coordinates = *FlatMap(coordinatesFourDims)
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

			geoData.Coordinates = *FlatMap(coordinatesFourDims)
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

		geoData.Coordinates = *FlatMap(coordinatesFourDims)
	}

	return geoData, nil
}
