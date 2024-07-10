module.exports = {
    retries: 3,
    ui: {
        loginUrl: 'https://example.com/login',
        usernameSelector: '#username',
        passwordSelector: '#password',
        loginButtonSelector: '#loginButton',
        successElementSelector: '#successElement',
        username: 'user',
        password: 'password'
    },
    api: {
        loginUrl: 'https://example.com/api/login',
        username: 'user',
        password: 'password'
    }
};
