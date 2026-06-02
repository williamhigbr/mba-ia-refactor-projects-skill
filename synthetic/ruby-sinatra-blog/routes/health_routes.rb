# frozen_string_literal: true

require 'sinatra/base'
require 'sinatra/json'

class HealthRoutes < Sinatra::Base
  get '/health' do
    json status: 'ok'
  end
end
