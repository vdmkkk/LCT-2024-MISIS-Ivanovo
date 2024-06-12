package delivery

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/jmoiron/sqlx"
	"lct/internal/delivery/docs"
	"lct/internal/delivery/handlers"
	"lct/internal/delivery/middleware"
	"lct/internal/repository"
	"lct/internal/service"
	"lct/pkg/log"

	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

func Start(db *sqlx.DB, logger *log.Logs) {
	r := gin.Default()

	docs.SwaggerInfo.BasePath = "/"
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	mdw := middleware.InitMiddleware(logger)

	r.Use(mdw.CORSMiddleware())

	geoDataRepo := repository.InitGeoDataRepo(db)
	geoDataService := service.InitGeoDataService(geoDataRepo, logger)
	geoDataHandler := handlers.InitGeoDataHandler(geoDataService)

	r.GET("/geo", geoDataHandler.GetByCount)
	r.GET("/geo/unom", geoDataHandler.GetByUNOM)
	r.PUT("/geo/by_filters", geoDataHandler.GetByFilter)

	buildingRepo := repository.InitBuildingRepo(db)
	buildingServ := service.InitBuildingService(buildingRepo, logger)
	buildingHandler := handlers.InitBuildingHandler(buildingServ)

	r.GET("/building", buildingHandler.GetByUNOM)
	r.GET("/building/by_ctp", buildingHandler.GetByCTPID)

	ctpRepo := repository.InitCtpRepo(db)
	ctpServ := service.InitCtpService(ctpRepo, logger)
	ctpHandler := handlers.InitCtpHandler(ctpServ)

	r.GET("/ctp", ctpHandler.GetByCTPID)

	incidentRepo := repository.InitIncidentRepo(db)
	incidentServ := service.InitIncidentService(incidentRepo, ctpRepo, buildingRepo, logger)
	incidentHandler := handlers.InitIncidentHandler(incidentServ)

	r.POST("/incident", incidentHandler.Create)
	r.GET("/incident/all", incidentHandler.GetAll)
	r.GET("/incident", incidentHandler.GetByID)

	if err := r.Run("0.0.0.0:8080"); err != nil {
		panic(fmt.Sprintf("error running client: %v", err.Error()))
	}
}
