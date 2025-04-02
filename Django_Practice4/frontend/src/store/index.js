import { createStore } from 'vuex';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/';

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      store.commit('LOGOUT');
    }
    return Promise.reject(error);
  }
);

const store = createStore({
    state: {
        user: null,
        token: localStorage.getItem('token') || '',
        loading: false,
        error: null
    },
    getters: {
        isAuthenticated: state => !!state.token,
        isAdmin: state => state.user && state.user.role === 'admin',
        authStatus: state => state.status,
    },
    mutations: {
        SET_LOADING(state, isLoading) {
            state.loading = isLoading;
        },
        SET_ERROR(state, error) {
            state.error = error;
        },
        SET_USER(state, user) {
            state.user = user;
        },
        SET_TOKEN(state, token) {
            state.token = token;
            localStorage.setItem('token', token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        },
        LOGOUT(state) {
            state.user = null;
            state.token = '';
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
        },
    },
    actions: {
        async login({ commit, dispatch }, credentials) {
            commit('SET_LOADING', true);
            commit('SET_ERROR', null);
            
            try {
                const response = await axios.post(`${API_URL}login/`, credentials);
                const token = response.data.access;
                commit('SET_TOKEN', token);
                
                await dispatch('fetchUser');
                
                return response;
            } catch (error) {
                commit('SET_ERROR', error.response ? error.response.data : 'Authentication failed');
                throw error;
            } finally {
                commit('SET_LOADING', false);
            }
        },
        
        async fetchUser({ commit, state }) {
            if (!state.token) return;
            
            commit('SET_LOADING', true);
            try {
                const response = await axios.get(`${API_URL}user/`, {
                    headers: { Authorization: `Bearer ${state.token}` }
                });
                commit('SET_USER', response.data);
                return response;
            } catch (error) {
                commit('SET_ERROR', error.response ? error.response.data : 'Failed to fetch user');
                throw error;
            } finally {
                commit('SET_LOADING', false);
            }
        },
        
        logout({ commit }) {
            commit('LOGOUT');
        },
    },
});

if (store.state.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${store.state.token}`;
}

export default store;