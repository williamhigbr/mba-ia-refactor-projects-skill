# frozen_string_literal: true

require 'sinatra/base'
require 'rack'

require_relative 'config/settings'
require_relative 'config/database'
require_relative 'middlewares/error_handler'
require_relative 'models/post'
require_relative 'models/user'
require_relative 'controllers/posts_controller'
require_relative 'controllers/users_controller'
require_relative 'controllers/admin_controller'
require_relative 'routes/posts_routes'
require_relative 'routes/users_routes'
require_relative 'routes/admin_routes'
require_relative 'routes/health_routes'

# Composition root: wire dependencies, mount routes, start server.

db = Config::Database.connection

post_model = Post.new(db)
user_model = User.new(db)

posts_controller = PostsController.new(post_model)
users_controller = UsersController.new(user_model)
admin_controller = AdminController.new(post_model, user_model)

# Inject controllers into route apps via settings
PostsRoutes.set :posts_controller, posts_controller
UsersRoutes.set :users_controller, users_controller
AdminRoutes.set :admin_controller, admin_controller

app = Rack::Builder.new do
  use ErrorHandler

  map '/admin' do
    run AdminRoutes
  end

  map '/' do
    run Rack::Cascade.new([HealthRoutes, PostsRoutes, UsersRoutes])
  end
end

if __FILE__ == $PROGRAM_NAME
  require 'rack/handler'
  Rack::Handler.default.run(
    app,
    Host: Config::Settings.bind,
    Port: Config::Settings.port
  )
end
