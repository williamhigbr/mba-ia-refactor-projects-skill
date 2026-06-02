# frozen_string_literal: true

require_relative '../config/settings'

class UsersController
  attr_reader :user_model

  def initialize(user_model)
    @user_model = user_model
  end

  def create(email:, password:)
    raise ArgumentError, 'email is required' if email.nil? || email.strip.empty?
    raise ArgumentError, 'password is required' if password.nil? || password.strip.empty?

    user_model.create(email: email, password: password)
    { ok: true }
  end

  def login(email:, password:)
    user_id = user_model.authenticate(email: email, password: password)
    return nil unless user_id

    { token: "token-uid-#{user_id}" }
  end
end
