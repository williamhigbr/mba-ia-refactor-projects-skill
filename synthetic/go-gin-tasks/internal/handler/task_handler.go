package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"example.com/synthetic/tasks/internal/service"
)

type TaskHandler struct {
	svc *service.TaskService
}

func NewTaskHandler(svc *service.TaskService) *TaskHandler {
	return &TaskHandler{svc: svc}
}

func (h *TaskHandler) Register(rg *gin.RouterGroup) {
	rg.GET("", h.list)
	rg.POST("", h.create)
	rg.GET("/search", h.search)
	rg.DELETE("/:id", h.delete)
}

func (h *TaskHandler) list(c *gin.Context) {
	tasks, err := h.svc.List()
	if err != nil {
		_ = c.Error(err)
		return
	}
	c.JSON(http.StatusOK, tasks)
}

type createTaskInput struct {
	Title string `json:"title" binding:"required"`
	Owner string `json:"owner" binding:"required"`
}

func (h *TaskHandler) create(c *gin.Context) {
	var in createTaskInput
	if err := c.ShouldBindJSON(&in); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if err := h.svc.Create(in.Title, in.Owner); err != nil {
		_ = c.Error(err)
		return
	}
	c.JSON(http.StatusCreated, gin.H{"ok": true})
}

func (h *TaskHandler) search(c *gin.Context) {
	q := c.Query("q")
	tasks, err := h.svc.Search(q)
	if err != nil {
		_ = c.Error(err)
		return
	}
	c.JSON(http.StatusOK, tasks)
}

func (h *TaskHandler) delete(c *gin.Context) {
	id := c.Param("id")
	if err := h.svc.Delete(id); err != nil {
		_ = c.Error(err)
		return
	}
	c.Status(http.StatusNoContent)
}
