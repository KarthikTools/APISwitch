const fetch = require('node-fetch');
const config = require('./config');
const logger = require('./logger');

async function loginWithAPI() {
    logger.info('Attempting to login via API');
    const response = await fetch(config.api.loginUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: config.api.username,
            password: config.api.password
        })
    });

    if (response.ok) {
        logger.info('Login successful with API');
    } else {
        logger.error(`API login failed: ${response.statusText}`);
    }
}

module.exports = { loginWithAPI };
