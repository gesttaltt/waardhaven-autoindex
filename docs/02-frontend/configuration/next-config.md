# Next.js Configuration

## Overview
Next.js configuration and setup for the frontend application.

## Configuration Files

### next.config.js
Main configuration file for Next.js application.

#### Current Settings
- React strict mode: enabled
- SWC minification: enabled
- Image optimization: configured
- Environment variables: defined
- API routes: configured

#### Build Configuration
```javascript
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['cdn.example.com'],
  },
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL,
  }
}
```

### tsconfig.json
TypeScript configuration for type checking.

#### Compiler Options
- Target: ES2020
- Module: ESNext
- Strict mode: enabled
- JSX: preserve
- Path aliases: configured

### tailwind.config.js
TailwindCSS configuration for styling.

#### Customizations
- Color palette
- Font families
- Breakpoints
- Custom utilities
- Dark mode support

### postcss.config.js
PostCSS configuration for CSS processing.

#### Plugins
- Tailwind CSS
- Autoprefixer
- CSS optimization
- Purge unused styles

## Environment Variables

### Development (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Waardhaven AutoIndex
NEXT_PUBLIC_GA_ID=UA-XXXXXXXXX
```

### Production (.env.production)
```
NEXT_PUBLIC_API_URL=https://api.waardhaven.com
NEXT_PUBLIC_APP_NAME=Waardhaven AutoIndex
NEXT_PUBLIC_GA_ID=UA-XXXXXXXXX
```

## App Router Configuration

### Directory Structure
```
app/
├── layout.tsx       # Root layout
├── page.tsx         # Home page
├── globals.css      # Global styles
├── dashboard/       # Dashboard route
├── login/          # Auth routes
└── api/            # API routes
```

### Routing Strategy
- File-based routing
- Dynamic routes
- Nested layouts
- Route groups
- Parallel routes

## Performance Optimizations

### Image Optimization
- Next/Image component
- Lazy loading
- Responsive images
- WebP format
- CDN integration

### Code Splitting
- Automatic splitting
- Dynamic imports
- Route-based chunks
- Component lazy loading
- Bundle analysis

### Caching Strategy
- Static generation
- ISR (Incremental Static Regeneration)
- Client-side caching
- API response caching
- CDN caching

## Build Process

### Development Build
```bash
npm run dev
# Starts development server
# Hot module replacement
# Fast refresh enabled
```

### Production Build
```bash
npm run build
# Creates optimized build
# Generates static pages
# Minifies code
# Optimizes images
```

### Export Static Site
```bash
npm run export
# Generates static HTML
# For static hosting
# No server required
```

## Deployment Configuration

### Vercel Deployment
- Automatic deployments
- Preview environments
- Environment variables
- Custom domains
- Edge functions

### Docker Deployment
- Multi-stage builds
- Optimized images
- Environment injection
- Health checks
- Volume mounts

## SEO Configuration

### Metadata
- Title templates
- Meta descriptions
- Open Graph tags
- Twitter cards
- Canonical URLs

### Sitemap
- Dynamic generation
- Route inclusion
- Priority settings
- Update frequency
- XML format

## Security Configuration

### Headers
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer Policy
- Permissions Policy

### CORS Settings
- Allowed origins
- Credential support
- Method restrictions
- Header whitelist

## Monitoring Setup

### Analytics
- Google Analytics
- Custom events
- Page views
- User tracking
- Conversion goals

### Error Tracking
- Sentry integration
- Error boundaries
- Source maps
- User context
- Performance monitoring

## Development Tools

### ESLint Configuration
- Next.js rules
- TypeScript rules
- Custom rules
- Auto-fix setup
- Pre-commit hooks

### Prettier Setup
- Format on save
- Consistent style
- Integration with ESLint
- Editor config
- Git hooks