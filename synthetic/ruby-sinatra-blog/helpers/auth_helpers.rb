# frozen_string_literal: true

require_relative '../config/settings'

module AuthHelpers
  def authenticate_admin!
    api_key = env['HTTP_X_API_KEY']
    unless api_key == Config::Settings.admin_api_key
      halt 403, { 'Content-Type' => 'application/json' }, JSON.generate(error: 'forbidden')
    end
  end
end
