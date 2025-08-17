# StrategyConfig Component

## Overview
Interactive component for configuring investment strategy parameters.

## Location
`apps/web/app/components/StrategyConfig.tsx`

## Purpose
Provides user interface for strategy parameter adjustment and visualization.

## Features

### Parameter Controls
- Weight sliders
- Threshold inputs
- Frequency selectors
- Constraint settings

### Visualization
- Weight distribution pie chart
- Impact preview
- Historical comparison
- Risk indicators

### Validation
- Real-time validation
- Constraint checking
- Error messages
- Warning indicators

## Component Structure

### Main Sections
- Strategy weights
- Risk parameters
- Timing settings
- Advanced options

### Sub-components
- WeightSlider
- ThresholdInput
- FrequencySelector
- ConstraintEditor

## Props Interface

### Required Props
- `config`: Current configuration
- `onUpdate`: Update callback
- `constraints`: Validation rules

### Optional Props
- `showAdvanced`: Advanced options
- `readOnly`: View-only mode
- `showPreview`: Impact preview
- `theme`: UI theme

## State Management

### Local State
- Form values
- Validation errors
- Preview data
- UI state

### Form Handling
- Controlled inputs
- Debounced updates
- Validation triggers
- Reset functionality

## Strategy Parameters

### Weight Configuration
- Momentum weight (0-100%)
- Market cap weight (0-100%)
- Risk parity weight (0-100%)
- Sum constraint (=100%)

### Risk Settings
- Performance threshold
- Volatility target
- Max drawdown limit
- Concentration limit

### Timing Options
- Rebalance frequency
- Lookback period
- Signal delay
- Execution window

## Validation Logic

### Weight Validation
- Sum to 100%
- Minimum values
- Maximum values
- Step increments

### Parameter Validation
- Range checking
- Type validation
- Business rules
- Dependency checks

## UI Components

### Input Controls
- Range sliders
- Number inputs
- Select dropdowns
- Radio buttons

### Visual Feedback
- Progress bars
- Color coding
- Icons
- Tooltips

### Interactive Elements
- Drag handles
- Increment buttons
- Reset buttons
- Preview toggles

## Visualization

### Charts
- Weight distribution
- Impact analysis
- Risk metrics
- Performance projection

### Indicators
- Risk level
- Diversification score
- Expected return
- Confidence intervals

## User Experience

### Guidance
- Help tooltips
- Documentation links
- Examples
- Best practices

### Feedback
- Save confirmation
- Error explanations
- Success messages
- Loading states

## Accessibility

### ARIA Support
- Label associations
- Role definitions
- State descriptions
- Error announcements

### Keyboard Navigation
- Tab order
- Arrow key support
- Enter/Space activation
- Escape cancellation

## Responsive Design

### Mobile Layout
- Stacked controls
- Touch-friendly
- Simplified view
- Gesture support

### Desktop Layout
- Multi-column
- Advanced features
- Hover interactions
- Keyboard shortcuts

## Performance

### Optimization
- Debounced updates
- Memoization
- Lazy loading
- Virtual scrolling

### State Updates
- Batched changes
- Optimistic UI
- Async validation
- Cache usage

## Testing

### Component Tests
- Input validation
- State management
- Event handling
- Rendering logic

### Integration Tests
- API updates
- Data flow
- Error scenarios
- User workflows

## Dependencies
- React hooks
- Form library
- Chart library
- Validation utils