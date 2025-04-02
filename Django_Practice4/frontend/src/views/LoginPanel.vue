<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="4" class="rounded-lg">
          <v-card-title class="text-h5 text-center py-4 primary white--text">
            Welcome Back
          </v-card-title>
          
          <v-card-text class="pt-6">
            <v-form @submit.prevent="handleLogin" ref="form">
              <v-text-field
                v-model="username"
                label="Username"
                prepend-inner-icon="mdi-account"
                required
                :rules="[v => !!v || 'Username is required']"
                outlined
                dense
              ></v-text-field>
              
              <v-text-field
                v-model="password"
                label="Password"
                prepend-inner-icon="mdi-lock"
                type="password"
                required
                :rules="[v => !!v || 'Password is required']"
                outlined
                dense
              ></v-text-field>
              
              <v-btn
                color="primary"
                block
                large
                type="submit"
                class="mt-4"
                elevation="2"
                :loading="loading"
              >
                Login
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-card-actions class="pb-4 px-4">
            <v-spacer></v-spacer>
            <v-btn
              text
              color="primary"
              @click="$router.push('/register')"
            >
              Need an account? Register
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      username: '',
      password: '',
      loading: false
    };
  },
  methods: {
    ...mapActions(['login']),
    async handleLogin() {
      if (!this.$refs.form.validate()) return;
      
      this.loading = true;
      try {
        await this.login({ username: this.username, password: this.password });
        this.$router.push('/admin');
      } catch (error) {
        // You might want to add error handling here
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>