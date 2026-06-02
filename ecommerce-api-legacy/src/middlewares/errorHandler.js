function errorHandler(err, req, res, _next) {
  console.error(`[ERROR] ${err.message}`);
  res.status(500).json({ error: 'Internal Server Error' });
}

module.exports = { errorHandler };
