import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import App from './App.jsx'
import BlogComponent from './appComponent/BlogComponent.jsx'
import AboutComponent from './appComponent/AboutComponent.jsx'

const appRoot = document.getElementById('react-root');
if (appRoot) {
  createRoot(appRoot).render(
    <StrictMode>
      <AboutComponent />
    </StrictMode>
  );
}

const blogRoot = document.getElementById('blog-page');
if (blogRoot) {
  createRoot(blogRoot).render(
    <StrictMode>
      <BlogComponent />
    </StrictMode>
  );
}
