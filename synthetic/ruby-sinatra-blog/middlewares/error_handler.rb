# frozen_string_literal: true

require 'json'

class ErrorHandler
  def initialize(app)
    @app = app
  end

  def call(env)
    @app.call(env)
  rescue ArgumentError => e
    [422, { 'Content-Type' => 'application/json' }, [JSON.generate(error: e.message)]]
  rescue StandardError => e
    warn "ERROR: #{e.class}: #{e.message}"
    [500, { 'Content-Type' => 'application/json' }, [JSON.generate(error: 'internal server error')]]
  end
end
