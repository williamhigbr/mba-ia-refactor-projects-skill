package service

import (
	"errors"

	"example.com/synthetic/tasks/internal/domain"
	"example.com/synthetic/tasks/internal/repository"
)

type TaskService struct {
	repo *repository.TaskRepo
}

func NewTaskService(repo *repository.TaskRepo) *TaskService {
	return &TaskService{repo: repo}
}

func (s *TaskService) List() ([]domain.Task, error) {
	return s.repo.ListAll()
}

func (s *TaskService) Search(q string) ([]domain.Task, error) {
	return s.repo.Search(q)
}

func (s *TaskService) Create(title, owner string) error {
	if title == "" {
		return errors.New("title is required")
	}
	if owner == "" {
		return errors.New("owner is required")
	}
	return s.repo.Create(title, owner)
}

func (s *TaskService) Delete(id string) error {
	if id == "" {
		return errors.New("id is required")
	}
	return s.repo.Delete(id)
}
