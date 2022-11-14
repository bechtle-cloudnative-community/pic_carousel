import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '../store/index.js'

import HomeView from '../views/HomeView.vue'
import Login from '../views/Login.vue'


Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/carousels',
    name: 'carousels',
    component: function () {
      return import(/* webpackChunkName: "about" */ '../views/Carousels.vue')
    }
  },
  {
    path: '/images',
    name: 'images',
    component: function () {
      return import(/* webpackChunkName: "about" */ '../views/Images.vue')
    }
  },
  {
    path: '/users',
    name: 'Users',
    component: function () {
      return import('../views/Users.vue')
    }
    
  }
]

const router = new VueRouter({
  routes
})

router.beforeEach((to, from, next) =>{  
  let tab = store.getters.get_tab_by_lnk(to.path)
  // console.log(tab)
  store.dispatch('check_token')
  .then((res)=>{
    if(!tab.auth) next()
    else{
      if(res) next()
      else next("/login")
    }
  })

})

export default router
