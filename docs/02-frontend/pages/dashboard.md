# Dashboard Page

## Overview
Main dashboard displaying portfolio performance, allocations, and key metrics.

## Location
`apps/web/app/dashboard/page.tsx`

## Purpose
Central hub for users to monitor their investment portfolio and performance.

## Key Features

### Performance Chart
- Interactive line chart
- Historical performance
- Benchmark comparison
- Time period selection

### Portfolio Metrics
- Current value
- Total return
- Daily change
- Risk metrics

### Asset Allocation
- Pie chart visualization
- Current weights
- Asset details
- Rebalancing status

### Individual Assets
- Performance table
- Price changes
- Allocation percentages
- Trend indicators

## Components Used

### Charts
- Recharts library
- LineChart for performance
- PieChart for allocation
- ResponsiveContainer

### Data Display
- Metric cards
- Data tables
- Progress indicators
- Status badges

## Data Flow

1. **Initial Load**
   - Fetch user portfolio
   - Get performance data
   - Load allocations
   - Calculate metrics

2. **Real-time Updates**
   - Polling mechanism
   - WebSocket (planned)
   - Auto-refresh option

3. **User Interactions**
   - Time period selection
   - Chart interactions
   - Export options
   - Refresh triggers

## State Management

### Local State
- Selected time period
- Chart settings
- Loading states
- Error handling

### Data State
- Portfolio data
- Performance history
- Current allocations
- Market prices

## API Calls

### Endpoints Used
- GET /api/v1/index/performance
- GET /api/v1/index/allocations
- GET /api/v1/index/metrics
- GET /api/v1/benchmark/sp500

### Data Fetching
- useEffect hooks
- Async data loading
- Error boundaries
- Loading states

## UI/UX Features

### Responsive Design
- Mobile-friendly layout
- Tablet optimization
- Desktop view
- Breakpoint handling

### Interactive Elements
- Hover tooltips
- Click interactions
- Zoom capabilities
- Pan gestures

### Visual Indicators
- Color coding
- Trend arrows
- Performance badges
- Status lights

## Performance Optimization

### Rendering
- React.memo usage
- Lazy loading
- Virtual scrolling
- Component splitting

### Data Management
- Data caching
- Memoization
- Selective updates
- Batch operations

## Customization

### User Preferences
- Chart types
- Color themes
- Data density
- Update frequency

### Display Options
- Currency selection
- Percentage vs absolute
- Time zones
- Date formats

## Error Handling

### Data Errors
- API failures
- Missing data
- Invalid responses
- Timeout handling

### UI Errors
- Component errors
- Rendering issues
- State conflicts
- Recovery actions

## Accessibility

### ARIA Labels
- Chart descriptions
- Table headers
- Button labels
- Form inputs

### Keyboard Navigation
- Tab order
- Focus management
- Shortcuts
- Skip links

## Future Enhancements
- Real-time WebSocket updates
- Advanced charting options
- Custom date ranges
- Comparison tools
- Export functionality
- Print optimization

## Dependencies
- React 18
- Recharts
- Axios
- TailwindCSS

## Related Pages
- ai-insights: AI analysis
- admin: Admin controls
- login: Authentication