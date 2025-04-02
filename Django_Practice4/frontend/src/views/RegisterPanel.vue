<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="4" class="rounded-lg">
          <v-card-title class="text-h5 text-center py-4 primary white--text">
            Create Account
          </v-card-title>
          
          <v-card-text class="pt-6">
            <v-form @submit.prevent="register" ref="form">
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
                v-model="email"
                label="Email"
                prepend-inner-icon="mdi-email"
                type="email"
                required
                :rules="[
                  v => !!v || 'Email is required',
                  v => /.+@.+\..+/.test(v) || 'Email must be valid'
                ]"
                outlined
                dense
              ></v-text-field>
              
              <v-select
                v-model="role"
                :items="roles"
                label="Role"
                prepend-inner-icon="mdi-shield-account"
                required
                outlined
                dense
              ></v-select>
              
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
              
              <v-text-field
                v-model="password2"
                label="Confirm Password"
                prepend-inner-icon="mdi-lock-check"
                type="password"
                required
                :rules="[
                  v => !!v || 'Confirmation is required',
                  v => v === password || 'Passwords must match'
                ]"
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
                Register
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-card-actions class="pb-4 px-4">
            <v-spacer></v-spacer>
            <v-btn
              text
              color="primary"
              @click="$router.push('/')"
            >
              Already have an account? Login
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      email: '',
      role: 'user',
      roles: ['user', 'admin'],
      password: '',
      password2: '',
      loading: false
    };
  },
  methods: {
    async register() {
      if (!this.$refs.form.validate()) return;
      
      this.loading = true;
      try {
        await axios.post('http://127.0.0.1:8000/api/register/', {
          username: this.username,
          email: this.email,
          role: this.role,
          password: this.password,
          password2: this.password2,
        });
        this.$router.push('/');
      } catch (error) {
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>