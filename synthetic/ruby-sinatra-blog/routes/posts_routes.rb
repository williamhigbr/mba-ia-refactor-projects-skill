# frozen_string_literal: true

require 'sinatra/base'
require 'sinatra/json'

class PostsRoutes < Sinatra::Base
  helpers do
    def posts_controller
      settings.posts_controller
    end
  end

  get '/posts' do
    json posts_controller.index
  end

  get '/posts/search' do
    json posts_controller.search(params['q'].to_s)
  end

  post '/posts' do
    data = JSON.parse(request.body.read) rescue {}
    result = posts_controller.create(
      title: data['title'],
      body: data['body'],
      author: data['author']
    )
    status 201
    json result
  end

  delete '/posts/:id' do
    posts_controller.delete(params['id'].to_i)
    status 204
  end
end
