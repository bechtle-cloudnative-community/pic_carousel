<template>
  <div>

    <!-- -------------------------------------------------- -->
    <v-card class="ma-6 mt-10 pa-4 elevation-6">
      <!-- <v-card-title class="purple darken-3 white--text py-1 px-4 subtitle-1 ">Users -->
      <v-card-title class="py-2 px-3 text-h7 ">
        <v-row>
          <v-col>Users</v-col>
          <v-col class="text-right">
            <v-btn 
              small
              fab
              class="purple darken-4 white--text"
              @click="dialogUser = !dialogUser"
            >
              <v-icon dark>mdi-plus</v-icon>
            </v-btn>
          </v-col>
          
        </v-row>
      </v-card-title>
      <v-data-table
        :headers="tableHeaders"
        :items="usersData"
        :search="search"
      >
        <template v-slot:item.act="{item}">
          <v-btn light icon @click="open_dialog_user(usersData.indexOf(item))">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </template>
      
      </v-data-table>
    </v-card>

    <!-- -------------------------------------------------- -->
    <v-dialog
      v-model="dialogUser"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
      scrollable
      >
      <v-card title>
        <form @submit.prevent="submit_user_add_edit">
        <v-toolbar flat dark color="purple darken-3" >
          <v-btn icon dark @click="close_dialog_user(cancel=true)" type="button">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>User Settings</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items >
            <v-btn v-if="!editData._id" icon dark type="submit">Create</v-btn>
            <v-btn v-if="editData._id" icon dark type="submit">Save</v-btn>
          </v-toolbar-items>
        </v-toolbar>

        <v-card-text>
            <v-text-field 
              class="pa-3 mx-8 mt-10" 
              required 
              label="Username" 
              v-model="editData.username" ></v-text-field>
            <v-select 
              class="pa-3 mx-8" 
              required 
              label="Role" 
              v-model="editData.role" 
              :items="ddRoles">
            </v-select>
            <v-text-field 
              class="pa-3 mx-8" 
              required 
              label="Email" 
              v-model="editData.email" 
              type="email"></v-text-field>
            <v-text-field 
              class="pa-3 mx-8" 
              label="Firstname" 
              v-model="editData.firstname" ></v-text-field>
            <v-text-field 
              class="pa-3 mx-8" 
              required 
              label="Lastname" 
              v-model="editData.lastname" ></v-text-field>
        </v-card-text>

        </form>

        <v-card-text class="text-center" v-if="editData._id">
          <v-btn 
            small
            dark
            color="purple darken-3" 
            class="mx-4"
            min-width="140"
            @click="dialogPassword = !dialogPassword"
            >Reset Password</v-btn>
          <v-btn 
            small
            dark
            color="blue-grey darken-4" 
            min-width="140"
            @click="dialogDelete = !dialogDelete"
            class="mx-4">Delete User</v-btn>
        </v-card-text>
        
      </v-card>
    </v-dialog>

    <!-- -------------------------------------------------- -->
    <v-dialog
      v-model="dialogPassword"
      max-width="500px"
    >
      <form @submit.prevent="submit_reset_password">
      <v-card class="pb-6">
        <v-card-title class="purple darken-3 white--text mb-2">
          Password Reset for user "{{editData.username}}"
        </v-card-title>
        <v-card-text class="pt-6">
          <v-text-field
            type="password"
            label="Enter new password"
            hint="At least 5 characters"
            required
            minlength="5"
            prepend-icon="mdi-lock"
            v-model="passwordReset"
          ></v-text-field>
          <v-text-field
            type="password"
            label="Repeat new password"
            hint="At least 5 characters"
            required
            minlength="5"
            prepend-icon="mdi-lock"
            v-model="passwordRepeat"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-container class="text-center">
            <v-btn
              dark 
              class="purple darken-3 mx-4" 
              min-width="120"
              type="submit"
            >Submit</v-btn>
            <v-btn
              dark 
              class="grey darken-2 mx-4"
              min-width="120"
              type="button"
              @click="close_reset_password"
            >Close</v-btn>
          </v-container>
        </v-card-actions>
      </v-card>
      </form>
    </v-dialog>

    <!-- -------------------------------------------------- -->
    <v-dialog
      v-model="dialogDelete"
      max-width="500px"
    >
      <v-card class="pb-6">
        <v-card-title class="purple darken-3 white--text mb-6">
          Delete user "{{editData.username}}"?
        </v-card-title>
        <v-card-actions>
          <v-container class="text-center">
            <v-btn
              dark 
              class="purple darken-3 mx-4" 
              min-width="120"
              type="submit"
              @click="submit_user_delete"
            >Submit</v-btn>
            <v-btn
              dark 
              class="grey darken-1 mx-4"
              min-width="120"
              type="button"
              @click="dialogDelete = !dialogDelete"
            >Close</v-btn>
          </v-container>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- -------------------------------------------------- -->
  </div>
</template>


<script>
  // import HelloWorld from '../components/HelloWorld'
  import axios from 'axios'
  import { mapMutations } from 'vuex'

  export default {
    name: 'Users',
    data: () => ({
      title: "Users",
      tableHeaders: [
        { text: 'Username', value: 'username' },
        { text: 'Role', value: 'role' },
        { text: 'Email', value: 'email' },
        { text: 'Firstname', value: 'firstname' },
        { text: 'Lastname', value: 'lastname' },
        { text: 'Action', value: 'act' },
      ],
      search: null,
      usersData: [],
    
      editData:{
        _id: null,
        username: null,
        role: null,
        email: null,
        firstname: null,
        lastname: null
      },
      resetData:{},

      ddRoles:[
        {
          text: "Administrator",
          value: "admin"
        },
        {
          text: "User",
          value: "user"
        },
        {
          text: "Penner",
          value: "penner"
        }
      ],
      
      dialogUser: false,
      dialogUserIdx: null,

      dialogPassword: false,
      passwordReset: null,
      passwordRepeat: null,

      dialogDelete: false,

    }),
    components: {
      
    },
    methods:{
      ...mapMutations([ "set_err", "reset_err" ]),

      //-------------------------------------------
      call_users_data(){
        axios.get("/api/users", this.$store.getters.create_bearer_auth_header)
        .then((res)=>{
          // console.log(res.data)
          this.usersData = res.data
          // this.open_dialog_user(1) Just for tests
        })
        .catch((err)=>{
          // console.log(err.message)
          this.set_err(err.message)
        })
      },

      open_dialog_user(idx){
        this.dialogUser = true
        this.dialogUserIdx = idx
        this.editData = this.usersData[idx]
        this.resetData = {...this.usersData[idx]}
      },
      close_dialog_user(cancel=false){
        if(cancel){
          for(let prop in this.resetData){
            this.editData[prop] = this.resetData[prop]
          }
        }
        this.dialogUser = false
        this.dialogUserIdx = null
        this.resetData = {}

        let tmpData = {}
        for(let prop in this.editData){
          tmpData[prop] = null
        }
        this.editData = {...tmpData}
      },

      submit_user_add_edit(){
        if( JSON.stringify(this.editData) === JSON.stringify(this.resetData) ){
          console.log("nothing toDo")
          this.close_dialog_user()
          return
        }

        let met = "post"
        let url = "/api/users"
        if(this.editData._id){
          met = "put"
          url = "/api/user/"+this.editData._id
        } 
        axios[met](
          url, 
          this.editData,
          this.$store.getters.create_bearer_auth_header
        )
        .then((res)=>{
          // console.log(res.data._id)
          if(this.editData._id){
            this.close_dialog_user()
          }
          else{
            this.editData._id = res.data._id
            this.usersData.push(this.editData)
          }
        })
        .catch((err)=>{
          this.set_err(err.message)
          this.close_dialog_user(true)
        })
      },

      close_reset_password(){
        this.passwordReset = null
        this.passwordRepeat = null
        this.dialogPassword = false
      },
      submit_reset_password(){
        if(this.passwordReset!=this.passwordRepeat){
          this.set_err("password repeate does not match")
          this.passwordRepeat = null
          return
        }
        axios.put(
          "/api/user/password/"+this.editData._id, 
          { password: this.passwordReset},
          this.$store.getters.create_bearer_auth_header
        )
        .then((res)=>{
          this.close_reset_password()
        })
        .catch((err)=>{
          this.set_err(err.message)
        })
      },

      submit_user_delete(){
        axios.delete(
          "/api/user/"+this.editData._id, 
          this.$store.getters.create_bearer_auth_header
        )
        .then((res)=>{
          this.dialogDelete = !this.dialogDelete
          this.usersData.splice(this.dialogUserIdx, 1); 
          this.close_dialog_user()
        })
        .catch((err)=>{
          this.set_err(err.message)
        })
      }

    },
    mounted: function(){
      this.call_users_data()
    }
  }
</script>


<style >
.v-data-table th {
  padding-top:30px !important;
  font-size: 14px !important;
}
.v-data-table td {
  font-size: 15px !important;
}
.v-data-table tr:hover {
  background-color: transparent !important;
}
</style>