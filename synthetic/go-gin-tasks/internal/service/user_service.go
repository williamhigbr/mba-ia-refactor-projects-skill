package service

import (
	"errors"
	"fmt"

	"example.com/synthetic/tasks/internal/repository"
)

type UserService struct {
	repo      *repository.UserRepo
	secretKey string
}

func NewUserService(repo *repository.UserRepo, secretKey string) *UserService {
	return &UserService{repo: repo, secretKey: secretKey}
}

func (s *UserService) Create(email, password string) error {
	if email == "" {
		return errors.New("email is required")
	}
	if password == "" {
		return errors.New("password is required")
	}
	return s.repo.Create(email, password)
}

func (s *UserService) Login(email, password string) (string, error) {
	id, err := s.repo.FindByCredentials(email, password)
	if err != nil {
		return "", errors.New("invalid credentials")
	}
	token := fmt.Sprintf("%s-for-user-%d", s.secretKey, id)
	return token, nil
}
