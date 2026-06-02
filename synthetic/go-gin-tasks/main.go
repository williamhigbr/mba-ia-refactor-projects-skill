package main

import (
	"log"

	"github.com/gin-gonic/gin"

	"example.com/synthetic/tasks/internal/config"
	"example.com/synthetic/tasks/internal/handler"
	"example.com/synthetic/tasks/internal/middleware"
	"example.com/synthetic/tasks/internal/repository"
	"example.com/synthetic/tasks/internal/service"
)

func main() {
	cfg := config.Load()

	db, err := repository.NewDB(cfg.DSN)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	taskRepo := repository.NewTaskRepo(db)
	userRepo := repository.NewUserRepo(db)

	taskSvc := service.NewTaskService(taskRepo)
	userSvc := service.NewUserService(userRepo, cfg.SecretKey)
	adminSvc := service.NewAdminService(taskRepo, userRepo)

	taskHandler := handler.NewTaskHandler(taskSvc)
	userHandler := handler.NewUserHandler(userSvc)
	adminHandler := handler.NewAdminHandler(adminSvc)

	r := gin.New()
	r.Use(gin.Recovery(), middleware.ErrorHandler())

	taskHandler.Register(r.Group("/tasks"))
	userHandler.Register(r.Group("/users"))
	adminHandler.Register(r.Group("/admin"))

	if err := r.Run(cfg.Addr); err != nil {
		log.Fatal(err)
	}
}
