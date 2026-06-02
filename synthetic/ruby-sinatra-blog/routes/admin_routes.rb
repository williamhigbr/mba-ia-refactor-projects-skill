# frozen_string_literal: true

require 'sinatra/base'
require 'sinatra/json'
require_relative '../helpers/auth_helpers'

class AdminRoutes < Sinatra::Base
  helpers AuthHelpers

  helpers do
    def admin_controller
      settings.admin_controller
    end
  end

  before do
    authenticate_admin!
  end

  post '/reset' do
    json admin_controller.reset
  end
end
