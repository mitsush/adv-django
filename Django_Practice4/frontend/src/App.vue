<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-title>Inventory Manager</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="$store.state.user" text @click="$router.push('/admin')">Admin</v-btn>
      <v-btn v-if="!$store.state.user" text @click="$router.push('/')">Login</v-btn>
      <v-btn v-if="!$store.state.user" text @click="$router.push('/register')">Register</v-btn>
      <v-btn v-if="$store.state.user" text @click="logout">Logout</v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app color="primary" dark class="text-center">
      <v-col class="text-center">
        &copy; {{ new Date().getFullYear() }} - Inventory Manager
      </v-col>
    </v-footer>
  </v-app>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  methods: {
    ...mapActions(['logout']),
  }
}
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
  line-height: 1.5;
}
</style>