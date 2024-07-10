const { loginWithUI } = require('./uiAutomation');
const { loginWithAPI } = require('./apiAutomation');
const logger = require('./logger');

(async () => {
    const uiLoginSuccess = await loginWithUI();

    if (!uiLoginSuccess) {
        logger.info('Switching to API login');
        await loginWithAPI();
    }
})();
