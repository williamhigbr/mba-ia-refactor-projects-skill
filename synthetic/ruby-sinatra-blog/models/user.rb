# frozen_string_literal: true

class User
  attr_reader :db

  def initialize(db)
    @db = db
  end

  def create(email:, password:)
    db.execute('INSERT INTO users (email, password) VALUES (?, ?)', [email, password])
  end

  def authenticate(email:, password:)
    row = db.execute('SELECT id FROM users WHERE email = ? AND password = ?', [email, password]).first
    row&.first
  end

  def delete_all
    db.execute('DELETE FROM users')
  end
end
