package config

import "os"

type Config struct {
	Addr      string
	DSN       string
	SecretKey string
}

func Load() *Config {
	return &Config{
		Addr:      getenv("ADDR", ":7004"),
		DSN:       getenv("DSN", "tasks.db"),
		SecretKey: getenv("SECRET_KEY", "change-me-in-production"),
	}
}

func getenv(key, fallback string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return fallback
}
