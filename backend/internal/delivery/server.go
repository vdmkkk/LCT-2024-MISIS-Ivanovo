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
	"lct/pkg/security"

	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

func Start(db *sqlx.DB, logger *log.Logs) {
	r := gin.Default()

	docs.SwaggerInfo.BasePath = "/"
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	jwtUtil := security.InitJWTUtil()

	mdw := middleware.InitMiddleware(logger, jwtUtil)

	r.Use(mdw.CORSMiddleware())
	r.Use(mdw.Authorization())

	mlPredictRepo := repository.InitMlPredictRepo(db)

	geoDataRepo := repository.InitGeoDataRepo(db, mlPredictRepo)
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
	r.GET("/incidents_by_unom", incidentHandler.GetByUNOM)
	r.PUT("/incident", incidentHandler.Update)

	mlPredictService := service.InitMlPredictService(logger, mlPredictRepo)
	mlPredictHandler := handlers.InitMlPredictHandler(mlPredictService)

	r.POST("/ml_predict_write", mlPredictHandler.SavePredictsFromDate)

	authHandler := handlers.InitAuthHandler()
	r.POST("/login", authHandler.Login)

	if err := r.Run("0.0.0.0:8080"); err != nil {
		panic(fmt.Sprintf("error running client: %v", err.Error()))
	}
}
