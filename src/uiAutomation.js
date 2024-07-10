const { chromium } = require('playwright');
const config = require('./config');
const logger = require('./logger');

async function loginWithUI() {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    let success = false;

    for (let attempt = 1; attempt <= config.retries; attempt++) {
        try {
            logger.info(`Attempt ${attempt}: Trying to login via UI`);
            await page.goto(config.ui.loginUrl);
            await page.fill(config.ui.usernameSelector, config.ui.username);
            await page.fill(config.ui.passwordSelector, config.ui.password);
            await page.click(config.ui.loginButtonSelector);

            // Wait for some element that appears only on successful login
            await page.waitForSelector(config.ui.successElementSelector, { timeout: 5000 });
            logger.info('Login successful with UI automation');
            success = true;
            break;
        } catch (error) {
            logger.error(`UI login attempt ${attempt} failed: ${error.message}`);
        }
    }

    await browser.close();
    return success;
}

module.exports = { loginWithUI };
