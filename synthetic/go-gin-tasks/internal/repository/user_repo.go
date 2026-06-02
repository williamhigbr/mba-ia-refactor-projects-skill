package repository

import (
	"database/sql"
)

type UserRepo struct {
	db *sql.DB
}

func NewUserRepo(db *sql.DB) *UserRepo {
	return &UserRepo{db: db}
}

func (r *UserRepo) Create(email, password string) error {
	_, err := r.db.Exec("INSERT INTO users (email, password) VALUES (?, ?)", email, password)
	return err
}

func (r *UserRepo) FindByCredentials(email, password string) (int, error) {
	var id int
	err := r.db.QueryRow("SELECT id FROM users WHERE email = ? AND password = ?", email, password).Scan(&id)
	if err != nil {
		return 0, err
	}
	return id, nil
}

func (r *UserRepo) DeleteAll() error {
	_, err := r.db.Exec("DELETE FROM users")
	return err
}
