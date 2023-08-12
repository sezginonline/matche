import adapter from '@sveltejs/adapter-static';
 
export default {
  kit: {
    adapter: adapter({
      pages: '../www/spa',
      assets: '../www/spa',
      fallback: 'index.html',
      precompress: false,
      strict: true
    }),
    paths: {
			base: '/spa'
		},
  }
};
