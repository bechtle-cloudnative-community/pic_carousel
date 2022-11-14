const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: [
    'vuetify'
  ],
  devServer: {
    proxy: {
      '/auth': {
        target: 'http://localhost:5000',
        //pathRewrite: {'^/api' : ''}
      },
      '/api': {
        target: 'http://localhost:5000',
        //pathRewrite: {'^/api' : ''}
      }
    }
  }
})
