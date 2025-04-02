import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginPanel.vue';
import Admin from '../views/AdminPanel.vue';
import Register from '../views/RegisterPanel.vue';
import ItemList from '../views/ItemList.vue';
import store from '../store';

const routes = [
    { 
        path: '/', 
        component: Login,
        meta: { guest: true } 
    },
    { 
        path: '/register', 
        component: Register,
        meta: { guest: true } 
    },
    {
        path: '/admin',
        component: Admin,
        meta: { requiresAdmin: true },
    },
    {
        path: '/items',
        component: ItemList,
        meta: { requiresAuth: true },
    },
    { 
        path: '/:pathMatch(.*)*', 
        redirect: '/' 
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach(async (to, from, next) => {
    const hasToken = !!store.state.token;
    
    if (to.meta.requiresAdmin) {
        if (!hasToken) {
            return next('/');
        }
        
        if (!store.state.user) {
            try {
                await store.dispatch('fetchUser');
            } catch (error) {
                store.dispatch('logout');
                return next('/');
            }
        }
        
        if (store.state.user?.role === 'admin') {
            return next();
        } else {
            return next('/items');
        }
    }
    
    if (to.meta.requiresAuth) {
        if (!hasToken) {
            return next('/');
        }
        
        if (!store.state.user) {
            try {
                await store.dispatch('fetchUser');
            } catch (error) {
                store.dispatch('logout');
                return next('/');
            }
        }
        
        return next();
    }
    
    if (to.meta.guest && hasToken) {
        return next('/items');
    }
    
    next();
});

export default router;