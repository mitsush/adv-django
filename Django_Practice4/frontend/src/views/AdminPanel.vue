<template>
  <v-container>
    <v-card elevation="4" class="rounded-lg">
      <v-toolbar flat color="primary" dark>
        <v-toolbar-title>Admin Dashboard</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="refreshItems">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>
      
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="items"
          :loading="loading"
          class="elevation-1"
          :items-per-page="10"
        >
          <template v-slot:top>
            <v-dialog v-model="dialog" max-width="500px">
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  color="primary"
                  dark
                  class="mb-2"
                  v-bind="attrs"
                  v-on="on"
                >
                  Add New Item
                </v-btn>
              </template>
              <v-card>
                <v-card-title>
                  <span class="text-h5">New Item</span>
                </v-card-title>
                <v-card-text>
                  <v-container>
                    <v-row>
                      <v-col cols="12">
                        <v-text-field
                          v-model="editedItem.name"
                          label="Name"
                          required
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="editedItem.description"
                          label="Description"
                          required
                          rows="3"
                        ></v-textarea>
                      </v-col>
                    </v-row>
                  </v-container>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="blue darken-1"
                    text
                    @click="close"
                  >
                    Cancel
                  </v-btn>
                  <v-btn
                    color="blue darken-1"
                    text
                    @click="save"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-icon
              small
              class="mr-2"
              @click="editItem(item)"
            >
              mdi-pencil
            </v-icon>
            <v-icon
              small
              @click="deleteConfirm(item)"
            >
              mdi-delete
            </v-icon>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete this item? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="gray" text @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" text @click="deleteItem">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import axios from 'axios';

export default {
  data() {
    return {
      loading: true,
      dialog: false,
      deleteDialog: false,
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Description', value: 'description', sortable: false },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      items: [],
      itemToDelete: null,
      editedIndex: -1,
      editedItem: {
        name: '',
        description: ''
      },
      defaultItem: {
        name: '',
        description: ''
      }
    };
  },
  computed: {
    ...mapState(['token']),
  },
  async created() {
    await this.fetchItems();
  },
  methods: {
    ...mapActions(['logout']),
    
    async fetchItems() {
      this.loading = true;
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/items/', {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.items = response.data;
      } catch (error) {
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    refreshItems() {
      this.fetchItems();
    },
    
    editItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },
    
    deleteConfirm(item) {
      this.itemToDelete = item;
      this.deleteDialog = true;
    },
    
    async deleteItem() {
      try {
        await axios.delete(`http://127.0.0.1:8000/api/items/${this.itemToDelete.id}/`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.items = this.items.filter(item => item.id !== this.itemToDelete.id);
      } catch (error) {
        console.error(error);
      } finally {
        this.deleteDialog = false;
        this.itemToDelete = null;
      }
    },
    
    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },
    
    async save() {
      try {
        if (this.editedIndex > -1) {
          // Edit existing item
          await axios.put(`http://127.0.0.1:8000/api/items/${this.editedItem.id}/`, this.editedItem, {
            headers: { Authorization: `Bearer ${this.token}` },
          });
          Object.assign(this.items[this.editedIndex], this.editedItem);
        } else {
          // Add new item
          const response = await axios.post('http://127.0.0.1:8000/api/items/', this.editedItem, {
            headers: { Authorization: `Bearer ${this.token}` },
          });
          this.items.push(response.data);
        }
        this.close();
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>