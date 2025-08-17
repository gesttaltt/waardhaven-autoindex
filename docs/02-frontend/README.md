# Waardhaven AutoIndex Web Application

## Overview
The Waardhaven AutoIndex frontend is a Next.js 14 application that provides a modern, responsive interface for automated index fund management. It features real-time portfolio tracking, investment simulation, AI-driven strategy optimization, and comprehensive system monitoring.

**Coverage Status**: 85% Complete (3 new pages added in latest update)

## Features

### Core Functionality
- **Portfolio Dashboard**: Real-time visualization of index performance and allocations
- **Investment Simulation**: Test investment strategies with historical data
- **Multi-Currency Support**: Simulate investments in various currencies
- **Performance Analytics**: Comprehensive risk metrics and performance indicators
- **Strategy Configuration**: Adjust index composition strategies with live rebalancing

### System Operations ✨ NEW
- **Task Management**: Monitor and control background operations
- **System Diagnostics**: Health monitoring and cache management
- **Report Generation**: Automated portfolio reports with history tracking
- **Real-time Monitoring**: Live task progress and system status updates

### Technical Features
- **Real-time Data**: WebSocket-ready architecture for live updates
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Performance Optimized**: React memoization and lazy loading
- **Error Boundaries**: Graceful error handling throughout
- **Background Tasks**: Celery integration for async operations

## Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **State Management**: React Hooks

## Project Structure

```
apps/web/
├── app/
│   ├── components/          # Reusable UI components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   ├── shared/          # Shared components
│   │   ├── SmartRefresh.tsx # Smart data refresh component
│   │   └── StrategyConfig.tsx # Strategy configuration panel
│   ├── services/            # API service layer
│   │   └── api/            
│   │       ├── base.ts      # Base API service class
│   │       ├── portfolio.ts # Portfolio endpoints
│   │       ├── market.ts    # Market data endpoints
│   │       ├── background.ts # Background tasks ✨ NEW
│   │       ├── diagnostics.ts # System diagnostics ✨ NEW
│   │       └── benchmark.ts  # Benchmark data ✨ NEW
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript type definitions
│   ├── constants/          # Application constants
│   ├── utils/              # Utility functions
│   │   └── api.ts          # API client configuration
│   ├── dashboard/          # Dashboard page (with new navigation)
│   ├── tasks/              # Task management page ✨ NEW
│   ├── diagnostics/        # System diagnostics page ✨ NEW
│   ├── reports/            # Reports & analytics page ✨ NEW
│   ├── admin/              # Admin panel
│   ├── ai-insights/        # AI insights page
│   ├── login/              # Authentication pages
│   ├── register/           
│   └── layout.tsx          # Root layout
├── public/                 # Static assets
└── API_DOCUMENTATION.md    # API reference

```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

```bash
# Navigate to web directory
cd apps/web

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Add your environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## API Integration

The application integrates with the Waardhaven AutoIndex API. See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed endpoint documentation.

### Service Architecture
- **Base Service**: Abstract class with common HTTP methods and error handling
- **Portfolio Service**: Index data, allocations, and simulations
- **Market Service**: Benchmark data and market indicators
- **Background Service**: Task queue management and monitoring ✨ NEW
- **Diagnostics Service**: System health and cache operations ✨ NEW
- **Benchmark Service**: S&P 500 and performance comparisons ✨ NEW
- **Strategy API**: Strategy configuration and risk metrics
- **Market Data API**: Database status and refresh operations

### Authentication Flow
1. User logs in via `/login` page
2. JWT token stored in localStorage
3. Token automatically attached to all API requests
4. 401 responses trigger automatic logout

## Key Pages & Components

### Dashboard (`/dashboard`)
Main interface displaying:
- Portfolio performance chart with S&P 500 comparison
- Current allocations pie chart
- Investment simulator
- Risk metrics display
- Quick navigation to all system pages ✨ NEW

### Task Management (`/tasks`) ✨ NEW
Background operations center featuring:
- Active task queue visualization
- Real-time progress monitoring
- Task statistics dashboard
- Quick action buttons for common tasks
- Task history tracking

### System Diagnostics (`/diagnostics`) ✨ NEW
System health monitoring with:
- Database status indicators
- Cache performance metrics
- Data freshness tracking
- Cache management controls
- System action buttons

### Reports & Analytics (`/reports`) ✨ NEW
Report generation center offering:
- Multiple report types (performance, allocation, risk)
- Custom time period selection
- Report generation progress tracking
- Historical report archive
- Quick report templates

### Admin Panel (`/admin`)
Administrative interface for:
- Database status monitoring
- Smart refresh controls
- Strategy configuration
- Risk analytics

### Smart Refresh Component
Intelligent data refresh with:
- Multiple refresh modes (auto, full, minimal, cached)
- Rate limit protection
- Progress tracking
- Error recovery

### Strategy Configuration
Dynamic strategy adjustment with:
- Weight distribution controls
- Risk parameter tuning
- AI-assisted optimization
- Real-time rebalancing

## Performance Optimizations

- **Memoization**: Heavy calculations cached with `useMemo`
- **Lazy Loading**: Components loaded on demand
- **Data Caching**: 5-minute cache for frequently accessed data
- **Batched Updates**: Multiple API calls combined when possible
- **Debounced Inputs**: User input debounced to reduce API calls

## Error Handling

- **API Errors**: Graceful degradation with user-friendly messages
- **Network Failures**: Automatic retry with exponential backoff
- **Auth Errors**: Automatic redirect to login
- **Validation**: Client-side validation before API calls
- **Error Boundaries**: Prevent entire app crashes

## Testing

```bash
# Run tests (when implemented)
npm test

# Run tests in watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
Private - All rights reserved

## Support
For issues or questions, please contact the development team or open an issue in the repository.