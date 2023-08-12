import { sveltekit } from '@sveltejs/kit/vite';
import fs from 'fs';

const config = {
	server: {
		host: 'match-e.com',
		port: 3000,
		https: {
			key: fs.readFileSync('/opt/homebrew/etc/httpd/server.key'),
			cert: fs.readFileSync('/opt/homebrew/etc/httpd/server.crt'),
		},
	},
	plugins: [sveltekit()]
};

export default config;
