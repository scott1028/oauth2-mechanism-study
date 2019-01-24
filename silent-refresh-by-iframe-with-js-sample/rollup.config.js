export default {
  input: 'src/main.js',
  output: {
    name: 'initTokenRefresher',  // such as: [ $ => window.$, jQuery => window.jQuery ]
    file: 'dist.js',
    format: 'iife',  // only for the format of platform you can execute
  },
  // avaliable when append "-w"
  watch: {
    include: './**',
    exclude: ['node_modules/**', 'dist.js'],
  },
};
