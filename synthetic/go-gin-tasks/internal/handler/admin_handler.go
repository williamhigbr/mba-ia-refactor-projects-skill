package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"example.com/synthetic/tasks/internal/service"
)

type AdminHandler struct {
	svc *service.AdminService
}

func NewAdminHandler(svc *service.AdminService) *AdminHandler {
	return &AdminHandler{svc: svc}
}

func (h *AdminHandler) Register(rg *gin.RouterGroup) {
	rg.POST("/reset", h.reset)
	// adminQuery (raw SQL execution) removed — no safe form exists.
}

func (h *AdminHandler) reset(c *gin.Context) {
	if err := h.svc.Reset(); err != nil {
		_ = c.Error(err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"reset": true})
}
