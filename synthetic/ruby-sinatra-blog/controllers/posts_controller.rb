# frozen_string_literal: true

class PostsController
  attr_reader :post_model

  def initialize(post_model)
    @post_model = post_model
  end

  def index
    rows = post_model.all_with_authors
    rows.map { |id, title, body, email| { id: id, title: title, body: body, author: email } }
  end

  def search(query)
    rows = post_model.search(query)
    rows.map { |id, title| { id: id, title: title } }
  end

  def create(title:, body:, author:)
    raise ArgumentError, 'title is required' if title.nil? || title.strip.empty?
    raise ArgumentError, 'body is required' if body.nil? || body.strip.empty?

    post_model.create(title: title, body: body, author: author)
    { ok: true }
  end

  def delete(id)
    post_model.delete(id)
  end
end
