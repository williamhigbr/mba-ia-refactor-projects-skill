# frozen_string_literal: true

require 'sqlite3'
require_relative 'settings'

module Config
  module Database
    module_function

    def connection
      @connection ||= begin
        db = SQLite3::Database.new(Config::Settings.db_path)
        db.execute(<<~SQL)
          CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            body TEXT,
            author TEXT
          )
        SQL
        db.execute(<<~SQL)
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT
          )
        SQL
        db
      end
    end
  end
end
