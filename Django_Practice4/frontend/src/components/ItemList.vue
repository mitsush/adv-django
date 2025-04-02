<template>
  <v-container>
    <v-card elevation="4" class="rounded-lg">
      <v-toolbar flat color="primary" dark>
        <v-toolbar-title>Item List</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="refreshItems">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>
      
      <v-card-text>
        <v-row>
          <v-col cols="12" md="8">
            <v-list two-line>
              <v-list-item-group>
                <v-list-item v-for="item in items" :key="item.id">
                  <v-list-item-content>
                    <v-list-item-title class="text-h6">{{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
              <v-divider></v-divider>
            </v-list>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card outlined class="pa-4">
              <v-card-title class="text-h6">Add New Item</v-card-title>
              <v-card-text>
                <v-form @submit.prevent="addItem" ref="form">
                  <v-text-field
                    v-model="newItem.name"
                    label="Name"
                    required
                    :rules="[v => !!v || 'Name is required']"
                    outlined
                    dense
                  ></v-text-field>
                  
                  <v-textarea
                    v-model="newItem.description"
                    label="Description"
                    required
                    :rules="[v => !!v || 'Description is required']"
                    outlined
                    dense
                    rows="3"
                  ></v-textarea>
                  
                  <v-btn
                    color="primary"
                    block
                    type="submit"
                    :loading="loading"
                  >
                    Add Item
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { getItems, createItem } from '../api';

export default {
  data() {
    return {
      items: [],
      newItem: { name: '', description: '' },
      loading: false
    };
  },
  async created() {
    await this.fetchItems();
  },
  methods: {
    async fetchItems() {
      this.loading = true;
      try {
        this.items = await getItems();
      } catch (error) {
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    refreshItems() {
      this.fetchItems();
    },
    
    async addItem() {
      if (!this.$refs.form.validate()) return;
      
      this.loading = true;
      try {
        const item = await createItem(this.newItem);
        this.items.push(item);
        this.newItem = { name: '', description: '' };
        this.$refs.form.reset();
      } catch (error) {
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>