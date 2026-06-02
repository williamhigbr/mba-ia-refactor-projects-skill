const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  dbUser: process.env.DB_USER || 'admin_master',
  dbPass: process.env.DB_PASS || 'change-me',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'change-me',
  smtpUser: process.env.SMTP_USER || 'no-reply@fullcycle.com.br',
};

module.exports = { config };
