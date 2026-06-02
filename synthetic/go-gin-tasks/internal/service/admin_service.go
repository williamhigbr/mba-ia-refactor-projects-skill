package service

import "example.com/synthetic/tasks/internal/repository"

type AdminService struct {
	taskRepo *repository.TaskRepo
	userRepo *repository.UserRepo
}

func NewAdminService(taskRepo *repository.TaskRepo, userRepo *repository.UserRepo) *AdminService {
	return &AdminService{taskRepo: taskRepo, userRepo: userRepo}
}

func (s *AdminService) Reset() error {
	if err := s.taskRepo.DeleteAll(); err != nil {
		return err
	}
	return s.userRepo.DeleteAll()
}
