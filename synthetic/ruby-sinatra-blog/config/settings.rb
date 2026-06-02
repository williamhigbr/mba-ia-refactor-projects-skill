# frozen_string_literal: true

module Config
  module Settings
    module_function

    def secret_key
      ENV.fetch('SECRET_KEY', 'change-me-in-production')
    end

    def admin_api_key
      ENV.fetch('ADMIN_API_KEY', 'change-me-in-production')
    end

    def db_path
      ENV.fetch('DB_PATH', 'blog.db')
    end

    def port
      ENV.fetch('PORT', '4567').to_i
    end

    def bind
      ENV.fetch('BIND', '0.0.0.0')
    end
  end
end
