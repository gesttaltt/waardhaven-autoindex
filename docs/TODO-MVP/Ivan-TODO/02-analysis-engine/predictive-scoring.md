# 🎯 Predictive Scoring & ML Models

**Priority**: CRITICAL  
**Complexity**: Very High  
**Timeline**: 5-7 days  
**Value**: Core intelligence for stock ranking and selection

## 🎯 Objective

Build ensemble ML models that:
- Score stocks based on multiple factors
- Predict price movements with high accuracy
- Rank investment opportunities
- Provide confidence intervals
- Explain predictions in plain language

## 🧠 Model Architecture

### Ensemble Components
```python
MODEL_ENSEMBLE = {
    'xgboost': {
        'type': 'Gradient Boosting',
        'weight': 0.30,
        'strengths': 'Tabular data, feature interactions',
        'update_frequency': 'Daily'
    },
    'lstm': {
        'type': 'Deep Learning',
        'weight': 0.25,
        'strengths': 'Time series patterns, sequences',
        'update_frequency': 'Weekly'
    },
    'random_forest': {
        'type': 'Ensemble Trees',
        'weight': 0.20,
        'strengths': 'Non-linear relationships, robust',
        'update_frequency': 'Daily'
    },
    'neural_network': {
        'type': 'Deep Neural Network',
        'weight': 0.15,
        'strengths': 'Complex patterns, high-dimensional',
        'update_frequency': 'Weekly'
    },
    'linear_regression': {
        'type': 'Statistical',
        'weight': 0.10,
        'strengths': 'Baseline, interpretability',
        'update_frequency': 'Daily'
    }
}
```

## 📊 Feature Engineering

### Feature Categories
```python
FEATURE_GROUPS = {
    'market_data': {
        'features': [
            'price_momentum_7d',
            'price_momentum_30d',
            'volume_ratio',
            'volatility_30d',
            'rsi_14',
            'macd_signal',
            'bollinger_position',
            'support_resistance_distance'
        ],
        'importance': 0.25
    },
    'insider_activity': {
        'features': [
            'insider_buy_count_30d',
            'insider_sell_count_30d',
            'insider_net_value',
            'congress_buy_count',
            'institutional_ownership_change',
            'insider_cluster_score'
        ],
        'importance': 0.20
    },
    'sentiment': {
        'features': [
            'news_sentiment_7d',
            'social_momentum',
            'reddit_mentions_growth',
            'twitter_sentiment',
            'analyst_consensus_change'
        ],
        'importance': 0.15
    },
    'fundamental': {
        'features': [
            'pe_ratio_vs_sector',
            'revenue_growth_yoy',
            'earnings_surprise_avg',
            'debt_to_equity',
            'free_cash_flow_yield'
        ],
        'importance': 0.15
    },
    'alternative': {
        'features': [
            'web_traffic_growth',
            'app_downloads_trend',
            'employee_growth_rate',
            'patent_filing_velocity',
            'satellite_activity_score'
        ],
        'importance': 0.10
    },
    'flow': {
        'features': [
            'options_flow_sentiment',
            'dark_pool_ratio',
            'smart_money_flow',
            'put_call_ratio',
            'unusual_options_activity'
        ],
        'importance': 0.15
    }
}
```

## 💾 Database Schema

```sql
-- ML model definitions
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    model_name VARCHAR(100) UNIQUE NOT NULL,
    model_type VARCHAR(50),
    version VARCHAR(20),
    
    -- Performance metrics
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_roc DECIMAL(5,4),
    
    -- Training details
    training_date TIMESTAMP,
    training_samples INTEGER,
    feature_count INTEGER,
    
    -- Model artifacts
    model_path TEXT,
    feature_importance JSONB,
    hyperparameters JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stock predictions
CREATE TABLE stock_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    prediction_date TIMESTAMP NOT NULL,
    
    -- Predictions
    price_target_7d DECIMAL(10,2),
    price_target_30d DECIMAL(10,2),
    price_target_90d DECIMAL(10,2),
    
    -- Probabilities
    prob_increase_7d DECIMAL(5,4),
    prob_increase_30d DECIMAL(5,4),
    prob_increase_90d DECIMAL(5,4),
    
    -- Expected returns
    expected_return_7d DECIMAL(8,4),
    expected_return_30d DECIMAL(8,4),
    expected_return_90d DECIMAL(8,4),
    
    -- Scoring
    overall_score DECIMAL(5,4),
    confidence DECIMAL(5,4),
    
    -- Model details
    model_version VARCHAR(20),
    ensemble_agreement DECIMAL(5,4),
    
    -- Signal
    signal VARCHAR(20), -- strong_buy, buy, hold, sell, strong_sell
    signal_strength DECIMAL(5,4),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, prediction_date)
);

-- Feature store
CREATE TABLE feature_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    symbol VARCHAR(20) NOT NULL,
    feature_date DATE NOT NULL,
    
    -- Feature values (stored as JSONB for flexibility)
    market_features JSONB,
    insider_features JSONB,
    sentiment_features JSONB,
    fundamental_features JSONB,
    alternative_features JSONB,
    flow_features JSONB,
    
    -- Feature quality
    completeness DECIMAL(5,4),
    last_updated TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, feature_date)
);

-- Model performance tracking
CREATE TABLE model_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    model_name VARCHAR(100),
    evaluation_date DATE NOT NULL,
    
    -- Performance metrics
    predictions_made INTEGER,
    correct_direction INTEGER,
    
    -- Returns
    avg_predicted_return DECIMAL(8,4),
    avg_actual_return DECIMAL(8,4),
    
    -- Error metrics
    mae DECIMAL(8,4),
    rmse DECIMAL(8,4),
    mape DECIMAL(8,4),
    
    -- Breakdown by timeframe
    accuracy_7d DECIMAL(5,4),
    accuracy_30d DECIMAL(5,4),
    accuracy_90d DECIMAL(5,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🤖 Model Implementation

```python
# app/ml/predictive_scorer.py

import xgboost as xgb
import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

class PredictiveScorer:
    """Main predictive scoring engine"""
    
    def __init__(self):
        self.models = {}
        self.feature_pipeline = FeatureEngineering()
        self.explainer = ModelExplainer()
        self.load_models()
        
    def load_models(self):
        """Load all ensemble models"""
        
        # XGBoost
        self.models['xgboost'] = xgb.XGBRegressor(
            n_estimators=1000,
            max_depth=6,
            learning_rate=0.01,
            subsample=0.8,
            colsample_bytree=0.8
        )
        
        # LSTM
        self.models['lstm'] = self.build_lstm_model()
        
        # Random Forest
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=500,
            max_depth=20,
            min_samples_split=10,
            n_jobs=-1
        )
        
        # Neural Network
        self.models['neural_network'] = self.build_nn_model()
        
    def build_lstm_model(self):
        """Build LSTM model for time series prediction"""
        
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(128, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(3)  # 7d, 30d, 90d predictions
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    async def score_stock(self, symbol: str) -> Dict:
        """Generate comprehensive score for a stock"""
        
        # Extract features
        features = await self.feature_pipeline.extract_features(symbol)
        
        if features is None:
            return {'error': 'Insufficient data for scoring'}
        
        # Get predictions from each model
        predictions = {}
        confidences = {}
        
        for model_name, model in self.models.items():
            try:
                pred = model.predict(features)
                predictions[model_name] = pred
                confidences[model_name] = self.calculate_confidence(model_name, features)
            except Exception as e:
                logger.error(f"Model {model_name} failed: {e}")
                
        # Calculate ensemble prediction
        ensemble_prediction = self.calculate_ensemble(predictions, confidences)
        
        # Generate signal
        signal = self.generate_signal(ensemble_prediction)
        
        # Create explanation
        explanation = await self.explainer.explain_prediction(
            symbol,
            features,
            predictions,
            signal
        )
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'overall_score': ensemble_prediction['score'],
            'confidence': ensemble_prediction['confidence'],
            'signal': signal,
            'predictions': {
                '7_day': ensemble_prediction['7d'],
                '30_day': ensemble_prediction['30d'],
                '90_day': ensemble_prediction['90d']
            },
            'model_agreement': self.calculate_agreement(predictions),
            'key_factors': self.identify_key_factors(features),
            'explanation': explanation
        }
    
    def calculate_ensemble(self, predictions: Dict, confidences: Dict) -> Dict:
        """Calculate weighted ensemble prediction"""
        
        weights = {
            'xgboost': 0.30,
            'lstm': 0.25,
            'random_forest': 0.20,
            'neural_network': 0.15,
            'linear': 0.10
        }
        
        # Weighted average
        weighted_pred = np.zeros(3)  # 7d, 30d, 90d
        total_weight = 0
        
        for model_name, pred in predictions.items():
            if model_name in weights:
                weight = weights[model_name] * confidences.get(model_name, 1.0)
                weighted_pred += pred * weight
                total_weight += weight
                
        if total_weight > 0:
            weighted_pred /= total_weight
            
        # Calculate overall score (0-100)
        score = self.calculate_score(weighted_pred)
        
        # Calculate confidence
        confidence = np.mean(list(confidences.values()))
        
        return {
            'score': score,
            'confidence': confidence,
            '7d': weighted_pred[0],
            '30d': weighted_pred[1],
            '90d': weighted_pred[2]
        }
    
    def generate_signal(self, prediction: Dict) -> Dict:
        """Generate trading signal from prediction"""
        
        score = prediction['score']
        confidence = prediction['confidence']
        
        # Signal thresholds
        if score >= 80 and confidence >= 0.7:
            signal = 'strong_buy'
            strength = 0.9
        elif score >= 65 and confidence >= 0.6:
            signal = 'buy'
            strength = 0.7
        elif score >= 45 and score < 65:
            signal = 'hold'
            strength = 0.5
        elif score >= 30 and confidence >= 0.6:
            signal = 'sell'
            strength = 0.7
        elif score < 30 and confidence >= 0.7:
            signal = 'strong_sell'
            strength = 0.9
        else:
            signal = 'hold'  # Default to hold if uncertain
            strength = 0.3
            
        return {
            'signal': signal,
            'strength': strength,
            'confidence': confidence
        }
```

## 🔬 Feature Engineering Pipeline

```python
class FeatureEngineering:
    """Feature extraction and engineering"""
    
    async def extract_features(self, symbol: str) -> np.ndarray:
        """Extract all features for a symbol"""
        
        features = {}
        
        # Market features
        market = await self.extract_market_features(symbol)
        features.update(market)
        
        # Insider features
        insider = await self.extract_insider_features(symbol)
        features.update(insider)
        
        # Sentiment features
        sentiment = await self.extract_sentiment_features(symbol)
        features.update(sentiment)
        
        # Flow features
        flow = await self.extract_flow_features(symbol)
        features.update(flow)
        
        # Alternative data features
        alternative = await self.extract_alternative_features(symbol)
        features.update(alternative)
        
        # Convert to array
        feature_array = self.dict_to_array(features)
        
        # Handle missing values
        feature_array = self.handle_missing_values(feature_array)
        
        # Scale features
        feature_array = self.scale_features(feature_array)
        
        return feature_array
    
    async def extract_market_features(self, symbol: str) -> Dict:
        """Extract market-based features"""
        
        # Get price data
        prices = await self.get_price_data(symbol, days=90)
        
        features = {}
        
        # Price momentum
        features['momentum_7d'] = (prices[-1] / prices[-8] - 1) * 100
        features['momentum_30d'] = (prices[-1] / prices[-31] - 1) * 100
        
        # Volatility
        returns = prices.pct_change()
        features['volatility_30d'] = returns[-30:].std() * np.sqrt(252)
        
        # Technical indicators
        features['rsi_14'] = self.calculate_rsi(prices, 14)
        features['macd_signal'] = self.calculate_macd_signal(prices)
        
        # Volume patterns
        volumes = await self.get_volume_data(symbol, days=30)
        features['volume_ratio'] = volumes[-1] / volumes[-30:].mean()
        features['volume_trend'] = self.calculate_trend(volumes)
        
        # Support/Resistance
        features['distance_from_support'] = self.distance_from_support(prices)
        features['distance_from_resistance'] = self.distance_from_resistance(prices)
        
        return features
    
    async def extract_insider_features(self, symbol: str) -> Dict:
        """Extract insider trading features"""
        
        features = {}
        
        # Get insider data
        insider_trades = await self.get_insider_trades(symbol, days=90)
        
        # Aggregate metrics
        features['insider_buys_30d'] = len([t for t in insider_trades if t['type'] == 'buy' and t['days_ago'] <= 30])
        features['insider_sells_30d'] = len([t for t in insider_trades if t['type'] == 'sell' and t['days_ago'] <= 30])
        features['insider_net_value'] = sum(t['value'] if t['type'] == 'buy' else -t['value'] for t in insider_trades)
        
        # Cluster detection
        features['insider_cluster_score'] = self.calculate_cluster_score(insider_trades)
        
        # Congressional trades
        congress_trades = await self.get_congress_trades(symbol, days=90)
        features['congress_buy_count'] = len([t for t in congress_trades if t['type'] == 'buy'])
        features['congress_sentiment'] = self.calculate_congress_sentiment(congress_trades)
        
        # Institutional changes
        inst_changes = await self.get_institutional_changes(symbol)
        features['inst_ownership_change'] = inst_changes.get('ownership_change_pct', 0)
        features['inst_buyers_sellers_ratio'] = inst_changes.get('buyers_sellers_ratio', 1)
        
        return features
```

## 📈 Model Training Pipeline

```python
class ModelTrainingPipeline:
    """Train and update ML models"""
    
    def train_all_models(self):
        """Train all models in ensemble"""
        
        # Load training data
        X_train, y_train = self.load_training_data()
        X_val, y_val = self.load_validation_data()
        
        results = {}
        
        # Train XGBoost
        results['xgboost'] = self.train_xgboost(X_train, y_train, X_val, y_val)
        
        # Train LSTM
        results['lstm'] = self.train_lstm(X_train, y_train, X_val, y_val)
        
        # Train Random Forest
        results['random_forest'] = self.train_random_forest(X_train, y_train, X_val, y_val)
        
        # Train Neural Network
        results['neural_network'] = self.train_neural_network(X_train, y_train, X_val, y_val)
        
        # Optimize ensemble weights
        self.optimize_ensemble_weights(results)
        
        return results
    
    def train_xgboost(self, X_train, y_train, X_val, y_val):
        """Train XGBoost model with hyperparameter tuning"""
        
        # Hyperparameter search space
        param_grid = {
            'n_estimators': [500, 1000, 1500],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.7, 0.8, 0.9]
        }
        
        # Grid search with cross-validation
        model = xgb.XGBRegressor()
        grid_search = GridSearchCV(
            model,
            param_grid,
            cv=5,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Evaluate on validation set
        best_model = grid_search.best_estimator_
        val_pred = best_model.predict(X_val)
        
        metrics = {
            'mse': mean_squared_error(y_val, val_pred),
            'mae': mean_absolute_error(y_val, val_pred),
            'r2': r2_score(y_val, val_pred),
            'best_params': grid_search.best_params_
        }
        
        # Save model
        self.save_model(best_model, 'xgboost')
        
        return metrics
```

## 🎯 Prediction Explainer

```python
class ModelExplainer:
    """Explain model predictions in natural language"""
    
    async def explain_prediction(self, symbol: str, features: Dict, predictions: Dict, signal: Dict) -> str:
        """Generate human-readable explanation"""
        
        # Get feature importance
        important_features = self.get_important_features(features)
        
        # Identify key drivers
        positive_drivers = []
        negative_drivers = []
        
        for feature, value, importance in important_features:
            if value > 0 and importance > 0:
                positive_drivers.append(feature)
            elif value < 0 and importance > 0:
                negative_drivers.append(feature)
                
        # Build explanation
        explanation = f"Based on our analysis of {symbol}:\n\n"
        
        # Signal explanation
        explanation += f"📊 **Signal**: {signal['signal'].upper()} (Confidence: {signal['confidence']:.1%})\n\n"
        
        # Key positive factors
        if positive_drivers:
            explanation += "✅ **Positive Factors**:\n"
            for driver in positive_drivers[:3]:
                explanation += f"  • {self.humanize_feature(driver, features[driver])}\n"
            explanation += "\n"
            
        # Key negative factors
        if negative_drivers:
            explanation += "⚠️ **Risk Factors**:\n"
            for driver in negative_drivers[:3]:
                explanation += f"  • {self.humanize_feature(driver, features[driver])}\n"
            explanation += "\n"
            
        # Price targets
        explanation += "🎯 **Price Targets**:\n"
        explanation += f"  • 7 days: ${predictions['7_day']:.2f} ({predictions['7_day_return']:.1%})\n"
        explanation += f"  • 30 days: ${predictions['30_day']:.2f} ({predictions['30_day_return']:.1%})\n"
        explanation += f"  • 90 days: ${predictions['90_day']:.2f} ({predictions['90_day_return']:.1%})\n\n"
        
        # Additional context
        explanation += await self.add_context(symbol, signal)
        
        return explanation
    
    def humanize_feature(self, feature_name: str, value: float) -> str:
        """Convert feature name and value to human-readable text"""
        
        translations = {
            'insider_cluster_score': f"Insider cluster buying detected (score: {value:.1f})",
            'momentum_30d': f"30-day momentum is {value:.1f}%",
            'congress_buy_count': f"{int(value)} congressional purchases detected",
            'social_momentum': f"Social media momentum at {value:.1f}x normal",
            'inst_ownership_change': f"Institutional ownership {'increased' if value > 0 else 'decreased'} by {abs(value):.1f}%",
            'volume_ratio': f"Volume is {value:.1f}x average",
            'news_sentiment_7d': f"News sentiment is {'positive' if value > 0 else 'negative'} ({value:.2f})"
        }
        
        return translations.get(feature_name, f"{feature_name}: {value:.2f}")
```

## 🎨 Visualization

```typescript
// PredictiveScoringDashboard.tsx

const PredictiveScoringDashboard = () => {
  return (
    <div className="predictive-scoring">
      {/* Top Scored Stocks */}
      <Card>
        <CardHeader>
          <Title>🏆 Top Scoring Stocks</Title>
          <Badge>Live</Badge>
        </CardHeader>
        <CardBody>
          <TopScoredStocksTable 
            stocks={topStocks}
            showSignals={true}
            showConfidence={true}
          />
        </CardBody>
      </Card>
      
      {/* Model Performance */}
      <Card>
        <CardHeader>
          <Title>📊 Model Performance</Title>
        </CardHeader>
        <CardBody>
          <ModelPerformanceChart 
            models={modelMetrics}
            timeframe="30d"
          />
        </CardBody>
      </Card>
      
      {/* Feature Importance */}
      <Card>
        <CardHeader>
          <Title>🎯 Feature Importance</Title>
        </CardHeader>
        <CardBody>
          <FeatureImportanceChart 
            features={featureImportance}
            model="ensemble"
          />
        </CardBody>
      </Card>
      
      {/* Prediction Accuracy */}
      <Card>
        <CardHeader>
          <Title>✅ Prediction Accuracy</Title>
        </CardHeader>
        <CardBody>
          <AccuracyMetrics 
            accuracy7d={metrics.accuracy_7d}
            accuracy30d={metrics.accuracy_30d}
            accuracy90d={metrics.accuracy_90d}
          />
        </CardBody>
      </Card>
    </div>
  );
};
```

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Direction accuracy (7d) | >65% | 0% |
| Direction accuracy (30d) | >70% | 0% |
| Return prediction MAE | <5% | - |
| Model training time | <2 hours | - |
| Scoring latency | <100ms | - |

---

**Next**: Continue with sentiment aggregation system.