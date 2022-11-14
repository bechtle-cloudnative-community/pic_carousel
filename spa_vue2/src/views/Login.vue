<template>
  <v-container>
    <v-spacer style="height: 15vh"></v-spacer>
    <v-card elevation="8" class="mx-auto" max-width="600" >
      <v-card-title class="purple darken-3 white--text pl-7 " >Login</v-card-title>
      
      <form @submit.prevent="submit">
        <v-text-field 
          prepend-icon="mdi-account"
          label="Username"
          required
          class="mt-8 mx-5"
          v-model="payload.username"
          ></v-text-field>

        <v-text-field 
          prepend-icon="mdi-lock"
          label="Password"
          type="password"
          required
          class="mt-5 mx-5"
          v-model="payload.password"
          ></v-text-field>

        <v-container class="text-center pa-5">
          <v-btn dark color="purple darken-3" min-width="120" type="submit">
            Login
          </v-btn>
        </v-container>
      </form>

  </v-card>

  </v-container>
  
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'Login',
    data: () => ({
      payload:{
        username: null,
        password: null
      }
    }),  
    components: {
      
    },
    methods:{
      submit(){
      // console.log(this.payload )
      const params = new URLSearchParams();
      for(let prop in this.payload){
        params.append(prop, this.payload[prop])
      }
      axios.post('/auth', params )
      .then(response => { 
        // console.log(response.data.access_token);
        this.$store.dispatch("login", response.data.access_token)//.then( console.log(this.$store.state.bearer))
        this.$router.push('/').then( ()=>{ this.$store.dispatch("set_active_tab") } )
      })
      .catch(error => {
        // console.log(error);
        // context.commit('reset_bearer');
        this.payload.username = null;
        this.payload.password = null;
      });
    }
    }
  }
</script>
