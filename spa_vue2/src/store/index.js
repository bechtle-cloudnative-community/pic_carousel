import Vue from 'vue'
import Vuex from 'vuex'

import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    init: false,

    username: null,
    role: null,
    bearer: null,

    err: false,
    err_msg: null,
    
    active_tab: 0,
    tabs:[
      {
        txt: "Home",
        lnk: "/",
        roles: ["user", "admin"],
        auth: false
      },
      {
        txt: "Images",
        lnk: "/images",
        roles: ["user", "admin"],
        auth: true
      },
      {
        txt: "Carousels",
        lnk: "/carousels",
        roles: ["user", "admin"],
        auth: true
      },
      {
        txt: "Users",
        lnk: "/users",
        roles: ["admin"],
        auth: true
      },
      {
        txt: "Login",
        lnk: "/login",
        roles: ["user", "admin"],
        auth: false
      },
      {
        txt: "Logout",
        func: "logout",
        roles: ["user", "admin"],
        auth: true
      }
    ],

    loader:{
      main: false,
      snap: false
    },

    images:{
      viewSelected: "thumbs",
      sortSelected: null
    },
    dataStore:{
      thumbs:[],
      carousels:[]
    }

  },
  getters: {
    filtered_tabs(state){
      let tabs = []
      for(let idx in state.tabs){
        if(state.tabs[idx].lnk === '/login' && state.role){
          continue
        }
        else if(!state.tabs[idx].auth){
          tabs.push(state.tabs[idx])
          continue
        }
        else if( state.tabs[idx].roles.includes(state.role) ){
          tabs.push(state.tabs[idx])
          continue
        }
      }
      return tabs
    },

    get_tab_by_lnk: (state) => (lnk)=>{
      return state.tabs.find(tab => tab.lnk === lnk) //AAAAALLLLLTER
    },

    create_bearer_auth_header(state){
      return {headers: { Authorization: `Bearer ${state.bearer}` }}
    },

  },

  mutations: {
    set_userdata(state, token){
      let tokenData = JSON.parse(atob(token.split('.')[1]));
      state.username = tokenData.username;
      state.role = tokenData.role;
      state.bearer = token;
    },
    reset_userdata(state){
      state.username = null;
      state.role = null;
      state.bearer = null;
    },
    set_active_tab(state, idx){
      state.active_tab = idx;
    },

    set_err(state, msg){
      state.err = true
      state.err_msg = msg
    },
    reset_err(state){
      state.err = false
      state.err_msg = null
    },

    set_loader(state, typ){
      state.loader[typ] = true
    },
    reset_loader(state, typ){
      state.loader[typ] = false
    },

    set_thumbs_data(state, data){
      state.dataStore.thumbs = data
    },
    set_carousels_data(state, data){
      state.dataStore.carousels = data
    },

    add_carousel(state, item){
      state.dataStore.carousels.push(item)
    },
    remove_carousel_by_item(state, item){
      let idx = state.dataStore.carousels.findIndex(elm => elm._id == item._id) //UIUIUI
      // console.log(idx) 
      state.dataStore.carousels.splice(idx, 1)
    }
    

    

  },
  actions: {
    //-----------------------------------------------
    login(context, token){
      localStorage.setItem("bearer", token)
      context.commit('set_userdata', token) // => SAUBER!!!
      // this.state.username = tokenData.username
      // this.state.role = tokenData.role
    },

    logout(context){
      context.commit('reset_userdata')
      localStorage.removeItem("bearer")
      context.state.init = false
      // this.state.username = null
      // this.state.role = null
    },
    
    //-----------------------------------------------
    check_token(context){
      var chk = false
      let token = localStorage.getItem("bearer")
      if(token){
        let tokenData = JSON.parse(atob(token.split('.')[1]));
        let nowTs = Date.now() / 1000 | 0
        if(tokenData.expires > nowTs){
          context.commit('set_userdata', token)
          chk = true
        }
      }
      if(token && !this.state.init){
        this.dispatch('call_thumbs')
        this.dispatch('call_carousels')
        this.state.init = true
      }
      return chk
    },
    
    //-----------------------------------------------
    set_active_tab(context){
      for(let idx in this.getters.filtered_tabs){ //UIUIUIUIUIUIU
        if(this.getters.filtered_tabs[idx].lnk == location.hash.substring(1)){
          context.commit('set_active_tab', parseInt(idx)) // => SUBBERSAUBER!!!
          break;
        }
      }
    },
    
    //-----------------------------------------------
    call_thumbs(context){
      context.commit('set_loader', 'main')
      new Promise((resolve, reject)=>{
        axios.get( "/api/thumbs?b64_data=yes", this.getters.create_bearer_auth_header)
        .then((res)=>{
          // console.log(res.data)
          context.commit('set_thumbs_data', res.data)
          context.dispatch('sort_thumbs')
          resolve()
        })
        .catch((err)=>{
          // console.log(err.message)
          context.commit('set_err', err.message)
          reject()
        })
        .finally(()=>{
          context.commit('reset_loader', 'main')
        })
      })
    },
    sort_thumbs(context){
      let sortAry = this.state.images.sortSelected
      // console.log(this.state.dataStore.thumbs)
      if(!sortAry) return
      let sortedData = JSON.parse(JSON.stringify(this.state.dataStore.thumbs))
      if(sortAry[1] == "desc"){
        sortedData.sort((b, a)=> a[sortAry[0]].localeCompare(b[sortAry[0]])) // !!!CRAZY!!!
      }
      else{
        sortedData.sort((a, b)=> a[sortAry[0]].localeCompare(b[sortAry[0]])) // !!!CRAZY!!!
      }
      context.commit("set_thumbs_data", sortedData) // Evtl. nen bisschen übertrieben
    },

    //-----------------------------------------------
    call_carousels(context){
      context.commit('set_loader', 'main')
      new Promise((resolve, reject)=>{
        axios.get( "/api/carousels", this.getters.create_bearer_auth_header)
        .then((res)=>{
          // console.log(res.data)
          context.commit('set_carousels_data', res.data)
          resolve()
        })
        .catch((err)=>{
          // console.log(err.message)
          context.commit('set_err', err.message)
          reject()
        })
        .finally(()=>{
          context.commit('reset_loader', 'main')
        })
      })
    },

  },
  modules: {
  }
})
