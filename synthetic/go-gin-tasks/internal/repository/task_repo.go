package repository

import (
	"database/sql"

	"example.com/synthetic/tasks/internal/domain"
)

type TaskRepo struct {
	db *sql.DB
}

func NewTaskRepo(db *sql.DB) *TaskRepo {
	return &TaskRepo{db: db}
}

func (r *TaskRepo) ListAll() ([]domain.Task, error) {
	rows, err := r.db.Query(`
		SELECT t.id, t.title, COALESCE(u.email, t.owner) AS owner, t.status
		FROM tasks t LEFT JOIN users u ON t.owner = u.email`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []domain.Task
	for rows.Next() {
		var t domain.Task
		if err := rows.Scan(&t.ID, &t.Title, &t.Owner, &t.Status); err != nil {
			return nil, err
		}
		tasks = append(tasks, t)
	}
	return tasks, rows.Err()
}

func (r *TaskRepo) Search(q string) ([]domain.Task, error) {
	rows, err := r.db.Query("SELECT id, title FROM tasks WHERE title LIKE ?", "%"+q+"%")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []domain.Task
	for rows.Next() {
		var t domain.Task
		if err := rows.Scan(&t.ID, &t.Title); err != nil {
			return nil, err
		}
		tasks = append(tasks, t)
	}
	return tasks, rows.Err()
}

func (r *TaskRepo) Create(title, owner string) error {
	_, err := r.db.Exec("INSERT INTO tasks (title, owner, status) VALUES (?, ?, ?)", title, owner, "pending")
	return err
}

func (r *TaskRepo) Delete(id string) error {
	_, err := r.db.Exec("DELETE FROM tasks WHERE id = ?", id)
	return err
}

func (r *TaskRepo) DeleteAll() error {
	_, err := r.db.Exec("DELETE FROM tasks")
	return err
}
