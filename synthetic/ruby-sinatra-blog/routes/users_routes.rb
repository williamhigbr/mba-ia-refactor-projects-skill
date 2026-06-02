# frozen_string_literal: true

require 'sinatra/base'
require 'sinatra/json'

class UsersRoutes < Sinatra::Base
  helpers do
    def users_controller
      settings.users_controller
    end
  end

  post '/users' do
    data = JSON.parse(request.body.read) rescue {}
    result = users_controller.create(
      email: data['email'],
      password: data['password']
    )
    status 201
    json result
  end

  post '/login' do
    data = JSON.parse(request.body.read) rescue {}
    result = users_controller.login(
      email: data['email'],
      password: data['password']
    )
    if result
      json result
    else
      status 401
      json error: 'invalid'
    end
  end
end
