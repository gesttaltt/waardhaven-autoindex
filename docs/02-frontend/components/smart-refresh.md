# SmartRefresh Component

## Overview
Intelligent data refresh component with automatic and manual refresh capabilities.

## Location
`apps/web/app/components/SmartRefresh.tsx`

## Purpose
Provides smart data refresh functionality with user controls and automatic updates.

## Features

### Auto-Refresh
- Configurable intervals
- Market hours awareness
- Pause/resume controls
- Resource optimization

### Manual Refresh
- On-demand updates
- Loading indicators
- Error handling
- Success feedback

### Smart Logic
- Activity detection
- Visibility API usage
- Network status check
- Battery awareness

## Component Props

### Required Props
- `onRefresh`: Callback function
- `interval`: Update frequency
- `enabled`: Auto-refresh toggle

### Optional Props
- `showControls`: Display UI controls
- `showStatus`: Status indicators
- `marketHoursOnly`: Market hours check
- `className`: Custom styling

## State Management

### Local State
- Refresh status
- Last update time
- Error state
- Loading state

### Context Integration
- Global refresh coordination
- Settings persistence
- User preferences

## UI Elements

### Controls
- Refresh button
- Auto-refresh toggle
- Interval selector
- Status display

### Indicators
- Loading spinner
- Success checkmark
- Error messages
- Last update time

## Smart Features

### Market Hours Detection
- Trading hours check
- Weekend handling
- Holiday calendar
- Time zone support

### Performance Optimization
- Debouncing
- Request batching
- Cache awareness
- Resource monitoring

### User Activity
- Idle detection
- Tab visibility
- Focus tracking
- Interaction monitoring

## Error Handling

### Network Errors
- Retry logic
- Offline detection
- Fallback behavior
- User notification

### API Errors
- Error display
- Retry options
- Manual override
- Debug information

## Accessibility

### ARIA Labels
- Button descriptions
- Status announcements
- Loading states
- Error messages

### Keyboard Support
- Tab navigation
- Enter/Space activation
- Escape cancellation
- Focus management

## Styling

### TailwindCSS Classes
- Responsive design
- Dark mode support
- Animation classes
- Custom themes

### Customization
- Color schemes
- Size variants
- Icon options
- Layout flexibility

## Performance

### Optimization
- React.memo usage
- useCallback hooks
- Conditional rendering
- Event cleanup

### Memory Management
- Timer cleanup
- Event listener removal
- State reset
- Reference management

## Testing

### Unit Tests
- Refresh logic
- Timer management
- Error scenarios
- User interactions

### Integration Tests
- API calls
- State updates
- UI feedback
- Error recovery

## Usage Example
```tsx
<SmartRefresh
  onRefresh={fetchData}
  interval={60000}
  enabled={true}
  showControls={true}
  marketHoursOnly={true}
/>
```

## Dependencies
- React hooks
- Axios/fetch
- Date utilities
- Icon library