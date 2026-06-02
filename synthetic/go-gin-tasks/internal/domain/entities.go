package domain

type Task struct {
	ID     int    `json:"id"`
	Title  string `json:"title"`
	Owner  string `json:"owner"`
	Status string `json:"status"`
}

type User struct {
	ID       int    `json:"id"`
	Email    string `json:"email"`
	Password string `json:"-"`
}
