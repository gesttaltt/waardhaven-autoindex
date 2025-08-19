# SmartRefresh Component

## Overview
Interactive component for intelligent market data refresh with multiple modes and real-time status display.

## Location
`apps/web/app/components/SmartRefresh.tsx`

## Features

### Core Functionality
- **Multi-mode refresh**: Auto, Minimal, Cached, and Full modes
- **Real-time status display**: Shows current database and refresh status
- **Error handling**: Graceful error display and recovery
- **Two display modes**: Simple button and detailed modal

### Refresh Modes

#### Auto Mode 🤖
- Intelligently chooses the best strategy based on API plan
- Default mode for most users
- Balances speed and completeness

#### Minimal Mode ⚡
- Fetches only priority assets
- Optimized for free tier API plans
- Reduces API calls to stay within rate limits

#### Cached Mode 💾
- Uses cached data only
- No external API calls
- Instant results from Redis cache

#### Full Mode 🔄
- Complete refresh of all data
- Includes rate limiting protection
- Most comprehensive but slowest

## Component Props

```typescript
interface SmartRefreshProps {
  onRefresh?: () => void;          // Callback when refresh starts
  onRefreshComplete?: () => void;  // Callback when refresh completes
  className?: string;               // Custom CSS classes for button
}
```

## Usage Examples

### Basic Usage
```tsx
import SmartRefresh from '@/components/SmartRefresh';

function Dashboard() {
  return (
    <SmartRefresh 
      onRefresh={() => console.log('Refresh started')}
      onRefreshComplete={() => console.log('Refresh complete')}
    />
  );
}
```

### Custom Styling
```tsx
<SmartRefresh 
  className="bg-gradient-to-r from-purple-600 to-pink-600"
/>
```

## Component States

### Simple Mode
- Single button with refresh action
- Settings gear icon to open detailed view
- Loading spinner during refresh
- Compact for dashboard integration

### Detailed Mode
- Full-screen modal overlay
- Current status display
- Mode selection grid
- Real-time feedback
- Error messages
- Help tips

## Status Information

### Database Status
- Tables row counts (assets, prices, indexes, etc.)
- Simulation readiness indicator
- Color-coded status (OK/EMPTY/ERROR)

### Refresh Status
- Asset count
- Latest data date
- Data age in days
- Update recommendation
- Stale data warnings

## API Integration

### Services Used
- `diagnosticsService.getRefreshStatus()` - Get current refresh status
- `diagnosticsService.getDatabaseStatus()` - Get database status
- `manualService.smartRefresh()` - Trigger smart refresh

### Response Handling
```typescript
interface RefreshResponse {
  message: string;
  mode?: string;
  features?: string[];
  note?: string;
}
```

## UI/UX Features

### Visual Feedback
- Loading spinners during operations
- Color-coded status indicators:
  - Green: OK/Ready
  - Yellow: Warning/Stale
  - Red: Error
  - Orange: Action needed
- Animated buttons with hover effects
- Gradient backgrounds for CTAs

### User Guidance
- Helpful tooltips and descriptions
- Mode recommendations based on API plan
- Performance tips in footer
- Clear error messages

## Error Handling

### Common Errors
- API connection failures
- Rate limit exceeded
- Database unavailable
- Network timeouts

### Error Display
- Red alert box with error details
- Maintains previous state
- Retry options available
- Console logging for debugging

## Performance Considerations

### Optimizations
- Parallel API calls for status loading
- Debounced status refresh (2-second delay)
- Conditional rendering for modal
- Efficient re-renders with state management

### Background Processing
- Refresh runs asynchronously
- UI remains responsive
- Progress indicated by spinner
- Can close modal during refresh

## Styling

### Tailwind Classes
- Dark theme optimized (gray-800/900 backgrounds)
- Responsive grid layouts
- Smooth transitions and animations
- Hover and active states
- Backdrop blur for modal

### Customization
- Accepts custom className prop
- Gradient button variants
- Icon-based visual hints
- Flexible layout options

## Dependencies

### External
- React (useState, useEffect)
- Next.js client component

### Internal
- `services/api` - API service layer
- Type definitions for responses

## Best Practices

### Usage Guidelines
1. Use "Minimal" mode for free API tiers
2. Schedule "Full" refreshes during off-hours
3. Monitor rate limits in production
4. Cache data when possible

### Integration Tips
1. Place prominently in dashboard
2. Provide visual feedback for all states
3. Handle errors gracefully
4. Log operations for debugging

## Related Components
- `Dashboard.tsx` - Main dashboard integration
- `services/api.ts` - API service definitions
- `DataStatus.tsx` - Status display component

## Notes
- Component auto-loads status on mount
- Modal can be closed during refresh
- Refresh continues in background
- Status updates automatically after completion