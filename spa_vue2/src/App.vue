<template>
  <v-app>
    <v-container dark class="purple darken-3 pa-0 elevation-4" fluid app>
      <v-row no-gutters>
        <v-col cols="4">
          <v-sheet class="purple darken-3 title py-2 px-6 " dark >
            PicCarousel - Example App
          </v-sheet>
        </v-col>

        <v-col >
          <v-tabs
            v-model="$store.state.active_tab"
            class="px-0 "
            background-color="purple darken-3"
            center-active
            dark
            right
          >
            <v-tab v-for="(tab,idx) in $store.getters.filtered_tabs" :key="idx" @click="go_to_lnk(tab)">{{tab.txt}}</v-tab>
          </v-tabs>
        </v-col>

      </v-row>
    </v-container>

    <v-dialog v-model="$store.state.err" width="500">
      <v-card>
        <v-card-title class="text-h5 white--text red darken-4" >Error</v-card-title>
        <v-card-text  class="subtitle-1 pt-4">{{$store.state.err_msg}}</v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="purple darken-4" text @click="reset_err">
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <v-main class="ma-2">
      <router-view/>
    </v-main>
  </v-app>
</template>

<script>

import { mapMutations } from 'vuex'

export default {
  name: 'App',

  data: () => ({
    msg: "Hallo Welt",
  }),
  methods:{  
    ...mapMutations([ "set_err", "reset_err" ]),

    go_to_lnk(tab){
      if(tab.lnk){
        location.hash = tab.lnk;
      }
      if(tab.func){
        this.$store.dispatch(tab.func).then(location.hash = "/")
      }
    },


  },
  mounted: function(){
    // this.update_active_hash()
    this.$store.dispatch("set_active_tab")
  },

  updated: function(){
    
  }

  
};
</script>
