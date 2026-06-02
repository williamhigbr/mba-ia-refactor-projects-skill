# frozen_string_literal: true

class AdminController
  attr_reader :post_model, :user_model

  def initialize(post_model, user_model)
    @post_model = post_model
    @user_model = user_model
  end

  def reset
    post_model.delete_all
    user_model.delete_all
    { reset: true }
  end
end
