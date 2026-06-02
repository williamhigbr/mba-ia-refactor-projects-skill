# frozen_string_literal: true

class Post
  attr_reader :db

  def initialize(db)
    @db = db
  end

  def all_with_authors
    db.execute(<<~SQL)
      SELECT posts.id, posts.title, posts.body, users.email
      FROM posts
      LEFT JOIN users ON posts.author = users.email
    SQL
  end

  def search(query)
    db.execute('SELECT id, title FROM posts WHERE title LIKE ?', ["%#{query}%"])
  end

  def create(title:, body:, author:)
    db.execute('INSERT INTO posts (title, body, author) VALUES (?, ?, ?)', [title, body, author])
  end

  def delete(id)
    db.execute('DELETE FROM posts WHERE id = ?', [id])
  end

  def delete_all
    db.execute('DELETE FROM posts')
  end
end
