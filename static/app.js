// app.js
const axios = require('axios');

const isLoggedIn = false;
const loginData = { email: '', password: '' };
const registerData = { name: '', email: '', password: '' };
const userData = {};

const login = async () => {
    try {
        const response = await axios.post('/api/login', loginData);
        userData = response.data;
        isLoggedIn = true;
    } catch (error) {
        console.error('Failed to login');
    }
};

const register = async () => {
    try {
        const response = await axios.post('/api/register', registerData);
        userData = response.data;
        isLoggedIn = true;
    } catch (error) {
        console.error('Failed to register');
    }
};

const logout = () => {
    isLoggedIn = false;
    userData = {};
};
