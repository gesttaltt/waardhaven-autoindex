# Frontend-Web Integration with Backend v1

## Documentation Overview

This documentation provides a comprehensive guide to the Waardhaven AutoIndex frontend-web application and its integration with the FastAPI backend. The frontend is built with Next.js 14, React 18, and TypeScript, following clean architecture principles and SOLID design patterns.

## Table of Contents

1. [Architecture Overview](./01-architecture-overview.md)
2. [API Integration Guide](./02-api-integration-guide.md)
3. [Authentication System](./03-authentication-system.md)
4. [Service Layer Documentation](./04-service-layer.md)
5. [Component Structure](./05-component-structure.md)
6. [State Management](./06-state-management.md)
7. [Routes and Pages](./07-routes-and-pages.md)
8. [Error Handling](./08-error-handling.md)
9. [Testing Guide](./09-testing-guide.md)
10. [Deployment Configuration](./10-deployment-configuration.md)
11. [Performance Optimization](./11-performance-optimization.md)
12. [Security Best Practices](./12-security-best-practices.md)
13. [Troubleshooting Guide](./13-troubleshooting-guide.md)
14. [Migration Guide](./14-migration-guide.md)
15. [API Endpoints Reference](./15-api-endpoints-reference.md)

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm 9+
- Backend API running on port 8000

### Installation
```bash
cd apps/web
npm install
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Environment Variables
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## Project Structure

```
apps/web/
├── app/
│   ├── core/                 # Clean architecture core
│   │   ├── domain/           # Business entities & interfaces
│   │   ├── application/      # Use cases
│   │   ├── infrastructure/   # External services
│   │   └── presentation/     # UI components & hooks
│   ├── services/             # API service layer
│   ├── components/           # Shared components
│   ├── providers/            # Context providers
│   └── [pages]/             # Next.js pages
├── public/                   # Static assets
└── package.json
```

## Key Features

- **Clean Architecture**: Separation of concerns with clear boundaries
- **SOLID Principles**: Maintainable and extensible codebase
- **Type Safety**: Full TypeScript implementation
- **Authentication**: JWT-based auth with Google OAuth support
- **Real-time Updates**: WebSocket support (when implemented)
- **Error Boundaries**: Graceful error handling
- **Performance**: Code splitting, lazy loading, and optimization

## Technology Stack

| Category | Technology | Version |
|----------|------------|---------|
| Framework | Next.js | 14.2.5 |
| UI Library | React | 18.3.1 |
| Language | TypeScript | 5.5.4 |
| Styling | Tailwind CSS | 3.4.7 |
| Charts | Recharts | 2.12.7 |
| HTTP Client | Native Fetch | - |
| State Management | React Query | 5.51.1 |
| Animation | Framer Motion | 12.23.12 |

## Development Workflow

1. **Feature Development**
   - Create feature branch
   - Implement following clean architecture
   - Add unit tests
   - Submit PR

2. **Code Standards**
   - Follow TypeScript strict mode
   - Use ESLint configuration
   - Maintain 80% test coverage
   - Document complex logic

3. **Review Process**
   - Code review required
   - CI/CD pipeline must pass
   - Manual testing verification

## Support

For issues or questions:
- GitHub Issues: [Project Repository]
- Documentation: This folder
- API Documentation: `/docs/api/`

## License

Proprietary - Waardhaven AutoIndex

---

Last Updated: 2025-01-18
Version: 1.0.0