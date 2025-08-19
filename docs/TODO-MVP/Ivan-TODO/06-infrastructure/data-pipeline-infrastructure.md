# 🔄 Data Pipeline Infrastructure - High-Performance Data Processing

**Priority**: CRITICAL  
**Complexity**: Very High  
**Timeline**: 4-5 days  
**Value**: Core foundation for all data-driven intelligence and real-time analysis

## 🎯 Objective

Build a robust data pipeline infrastructure that:
- Ingests data from 50+ global sources in real-time
- Processes millions of events per second with low latency
- Ensures data quality, consistency, and reliability
- Scales automatically based on data volume
- Provides both streaming and batch processing capabilities

## 🏗️ Data Pipeline Architecture

### Pipeline Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                         │
│     "50+ Sources → Real-time Streams → Unified Format"         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
    │MARKET │   │NEWS  │   │SOCIAL│
    │DATA   │   │FEEDS │   │MEDIA │
    └─────────┘   └─────────┘   └─────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
┌──────────────────────┼────────────────────────────────────────┐
│                STREAM PROCESSING LAYER                        │
│           "Real-time Transformation & Analysis"               │
└──────────────────────┬────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
    │CLEAN │   │ENRICH│   │ANALYZE│
    │VALIDATE│   │TRANSFORM│   │DETECT│
    └─────────┘   └─────────┘   └─────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
┌──────────────────────┼────────────────────────────────────────┐
│                 STORAGE LAYER                                 │
│        "Multi-tier Storage for Different Use Cases"          │
└────────────────────────────────────────────────────────────────┘
```

### Data Source Integration
```yaml
# Data source configuration
data_sources:
  market_data:
    primary_providers:
      polygon:
        type: websocket
        rate_limit: 1000_msgs_per_second
        data_types: [prices, trades, quotes, aggregates]
        latency_sla: <50ms
        
      alpha_vantage:
        type: rest_api
        rate_limit: 5_requests_per_minute
        data_types: [fundamentals, technicals, forex]
        batch_size: 100_symbols
        
      iex_cloud:
        type: websocket + rest
        rate_limit: 1000_requests_per_second
        data_types: [prices, news, dividends, earnings]
        
    secondary_providers:
      finnhub: [sentiment, earnings, recommendations]
      quandl: [economic_data, commodities]
      fred: [economic_indicators]
      
  news_sentiment:
    news_apis:
      newsapi: 1000_requests_per_day
      marketaux: 10000_requests_per_month
      benzinga: unlimited
      
    social_media:
      reddit: [r/investing, r/stocks, r/SecurityAnalysis]
      twitter: [financial_keywords, $cashtags]
      
  government_data:
    insider_trading:
      sec_edgar: daily_filings
      congress_trades: weekly_updates
      
    economic_data:
      bea: [gdp, inflation, employment]
      census: [demographic, economic]
      treasury: [yield_curves, debt]

# Data schemas
schemas:
  market_data_schema:
    price_tick:
      symbol: string
      timestamp: timestamp_ms
      price: decimal(10,4)
      volume: integer
      bid: decimal(10,4)
      ask: decimal(10,4)
      bid_size: integer
      ask_size: integer
      
  news_schema:
    article:
      id: uuid
      title: string
      content: text
      source: string
      published_at: timestamp
      sentiment_score: decimal(3,2)
      symbols_mentioned: array[string]
      categories: array[string]
```

## 🌊 Stream Processing Platform

### Apache Kafka Cluster Configuration
```yaml
# kafka/cluster-config.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: waardhaven-kafka-cluster
  namespace: data-processing
spec:
  kafka:
    version: 3.6.0
    replicas: 6  # High availability
    
    listeners:
      - name: internal
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls
      - name: external
        port: 9094
        type: loadbalancer
        tls: true
        authentication:
          type: scram-sha-512
    
    config:
      # Replication and durability
      default.replication.factor: 3
      min.insync.replicas: 2
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      
      # Performance tuning
      num.network.threads: 8
      num.io.threads: 16
      socket.send.buffer.bytes: 102400
      socket.receive.buffer.bytes: 102400
      socket.request.max.bytes: 104857600
      
      # Log settings
      log.retention.hours: 168  # 7 days
      log.retention.bytes: 1073741824  # 1GB per partition
      log.segment.bytes: 268435456     # 256MB segments
      log.roll.hours: 24
      
      # Topic management
      auto.create.topics.enable: false
      delete.topic.enable: true
      
      # Compression
      compression.type: lz4
      
      # Security
      security.inter.broker.protocol: SASL_SSL
      sasl.mechanism.inter.broker.protocol: SCRAM-SHA-512
    
    # Storage configuration
    storage:
      type: jbod
      volumes:
        - id: 0
          type: persistent-claim
          size: 2000Gi
          storageClass: gp3-optimized
          deleteClaim: false
        - id: 1
          type: persistent-claim
          size: 2000Gi
          storageClass: gp3-optimized
          deleteClaim: false
    
    # Resource allocation
    resources:
      requests:
        memory: 16Gi
        cpu: 4000m
      limits:
        memory: 32Gi
        cpu: 8000m
    
    # JVM tuning
    jvmOptions:
      -Xms: 8g
      -Xmx: 16g
      -XX:+UseG1GC
      -XX:MaxGCPauseMillis: 20
      -XX:InitiatingHeapOccupancyPercent: 35
      -XX:+ExplicitGCInvokesConcurrent
      -Djava.awt.headless: true
    
    # Metrics
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: kafka-metrics-config.yml

---
# Topic definitions
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: market-data-raw
  namespace: data-processing
  labels:
    strimzi.io/cluster: waardhaven-kafka-cluster
spec:
  partitions: 24  # High parallelism for market data
  replicas: 3
  config:
    retention.ms: 604800000      # 7 days
    segment.ms: 3600000          # 1 hour segments
    compression.type: lz4
    cleanup.policy: delete
    min.insync.replicas: 2

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: market-data-processed
  namespace: data-processing
  labels:
    strimzi.io/cluster: waardhaven-kafka-cluster
spec:
  partitions: 12
  replicas: 3
  config:
    retention.ms: 2592000000     # 30 days
    segment.ms: 86400000         # 1 day segments
    compression.type: lz4
    cleanup.policy: delete

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: news-sentiment-stream
  namespace: data-processing
  labels:
    strimzi.io/cluster: waardhaven-kafka-cluster
spec:
  partitions: 8
  replicas: 3
  config:
    retention.ms: 2592000000     # 30 days
    compression.type: gzip       # Better compression for text
    cleanup.policy: delete

---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: insider-trading-events
  namespace: data-processing
  labels:
    strimzi.io/cluster: waardhaven-kafka-cluster
spec:
  partitions: 4
  replicas: 3
  config:
    retention.ms: 31536000000    # 1 year
    compression.type: gzip
    cleanup.policy: delete
```

### Apache Flink Stream Processing
```yaml
# flink/flink-cluster.yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: waardhaven-flink-cluster
  namespace: data-processing
spec:
  image: flink:1.18-scala_2.12-java11
  flinkVersion: v1_18
  imagePullPolicy: Always
  
  # Cluster configuration
  flinkConfiguration:
    # High availability
    high-availability: kubernetes
    high-availability.storageDir: s3://waardhaven-flink-ha/
    
    # State backend
    state.backend: rocksdb
    state.backend.incremental: true
    state.checkpoints.dir: s3://waardhaven-flink-checkpoints/
    state.savepoints.dir: s3://waardhaven-flink-savepoints/
    
    # Checkpointing
    execution.checkpointing.interval: 30s
    execution.checkpointing.min-pause: 10s
    execution.checkpointing.timeout: 600s
    execution.checkpointing.max-concurrent-checkpoints: 1
    execution.checkpointing.cleanup-mode: retain-on-cancellation
    
    # Memory configuration
    taskmanager.memory.process.size: 8g
    taskmanager.memory.flink.size: 6g
    taskmanager.memory.network.fraction: 0.2
    taskmanager.memory.managed.fraction: 0.4
    
    # Parallelism
    parallelism.default: 4
    taskmanager.numberOfTaskSlots: 4
    
    # Restart strategy
    restart-strategy: fixed-delay
    restart-strategy.fixed-delay.attempts: 3
    restart-strategy.fixed-delay.delay: 30s
    
    # Metrics
    metrics.reporter.prometheus.class: org.apache.flink.metrics.prometheus.PrometheusReporter
    metrics.reporter.prometheus.port: 9249
  
  # Service account
  serviceAccount: flink-service-account
  
  # JobManager configuration
  jobManager:
    replicas: 2  # HA setup
    resource:
      memory: 4Gi
      cpu: 2000m
    
    podTemplate:
      metadata:
        annotations:
          prometheus.io/scrape: "true"
          prometheus.io/port: "9249"
      spec:
        containers:
          - name: flink-main-container
            env:
              - name: AWS_REGION
                value: us-east-1
            resources:
              requests:
                memory: 3Gi
                cpu: 1000m
              limits:
                memory: 4Gi
                cpu: 2000m
  
  # TaskManager configuration
  taskManager:
    replicas: 6
    resource:
      memory: 8Gi
      cpu: 4000m
    
    podTemplate:
      metadata:
        annotations:
          prometheus.io/scrape: "true"
          prometheus.io/port: "9249"
      spec:
        containers:
          - name: flink-main-container
            env:
              - name: AWS_REGION
                value: us-east-1
            resources:
              requests:
                memory: 6Gi
                cpu: 2000m
              limits:
                memory: 8Gi
                cpu: 4000m

---
# Flink job for market data processing
apiVersion: flink.apache.org/v1beta1
kind: FlinkJob
metadata:
  name: market-data-processor
  namespace: data-processing
spec:
  deploymentName: waardhaven-flink-cluster
  
  # Job configuration
  job:
    jarURI: s3://waardhaven-flink-jobs/market-data-processor-1.0.jar
    entryClass: com.waardhaven.flink.MarketDataProcessor
    args:
      - --kafka.bootstrap.servers
      - waardhaven-kafka-cluster-kafka-bootstrap:9092
      - --checkpoint.interval
      - "30000"
      - --parallelism
      - "12"
    
    parallelism: 12
    upgradeMode: savepoint
    
    # State configuration
    state: running
    savepointTriggerNonce: 1
    
  # Resource allocation
  flinkConfiguration:
    parallelism.default: 12
    execution.checkpointing.interval: 30s
```

### Data Processing Jobs
```python
# flink_jobs/market_data_processor.py
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
import json
from datetime import datetime
import logging

class MarketDataProcessor:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.set_parallelism(12)
        self.env.enable_checkpointing(30000)  # 30 seconds
        
        # Kafka configuration
        self.kafka_props = {
            'bootstrap.servers': 'waardhaven-kafka-cluster-kafka-bootstrap:9092',
            'group.id': 'market-data-processor',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': 'false'
        }
        
    def setup_kafka_source(self):
        """Setup Kafka consumer for raw market data"""
        kafka_consumer = FlinkKafkaConsumer(
            topics=['market-data-raw'],
            deserialization_schema=SimpleStringSchema(),
            properties=self.kafka_props
        )
        kafka_consumer.set_start_from_latest()
        return kafka_consumer
    
    def setup_kafka_sink(self):
        """Setup Kafka producer for processed data"""
        kafka_producer = FlinkKafkaProducer(
            topic='market-data-processed',
            serialization_schema=SimpleStringSchema(),
            producer_config=self.kafka_props
        )
        return kafka_producer
    
    def process_market_data(self, data_stream):
        """Process raw market data"""
        
        def parse_and_validate(json_str):
            """Parse JSON and validate market data"""
            try:
                data = json.loads(json_str)
                
                # Validation rules
                required_fields = ['symbol', 'timestamp', 'price', 'volume']
                if not all(field in data for field in required_fields):
                    return None
                
                # Price validation
                if data['price'] <= 0 or data['volume'] < 0:
                    return None
                
                # Add processing metadata
                data['processed_at'] = datetime.utcnow().isoformat()
                data['pipeline_version'] = '1.0'
                
                # Normalize symbol format
                data['symbol'] = data['symbol'].upper().strip()
                
                # Convert timestamp to Unix milliseconds
                if isinstance(data['timestamp'], str):
                    dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    data['timestamp'] = int(dt.timestamp() * 1000)
                
                return json.dumps(data)
                
            except Exception as e:
                logging.error(f"Error processing market data: {e}")
                return None
        
        def enrich_with_technical_indicators(json_str):
            """Add technical indicators to market data"""
            try:
                data = json.loads(json_str)
                symbol = data['symbol']
                price = data['price']
                
                # Calculate simple moving averages (simplified)
                # In production, this would use a proper windowing function
                data['sma_20'] = self.calculate_sma(symbol, price, 20)
                data['rsi'] = self.calculate_rsi(symbol, price)
                data['bollinger_upper'] = self.calculate_bollinger_upper(symbol, price)
                data['bollinger_lower'] = self.calculate_bollinger_lower(symbol, price)
                
                return json.dumps(data)
                
            except Exception as e:
                logging.error(f"Error enriching data: {e}")
                return json_str
        
        # Processing pipeline
        processed_stream = (data_stream
                          .map(parse_and_validate)
                          .filter(lambda x: x is not None)
                          .map(enrich_with_technical_indicators)
                          .filter(lambda x: x is not None))
        
        return processed_stream
    
    def run(self):
        """Run the market data processing job"""
        
        # Setup source and sink
        kafka_source = self.setup_kafka_source()
        kafka_sink = self.setup_kafka_sink()
        
        # Create data stream
        raw_stream = self.env.add_source(kafka_source)
        
        # Process data
        processed_stream = self.process_market_data(raw_stream)
        
        # Write to sink
        processed_stream.add_sink(kafka_sink)
        
        # Execute job
        self.env.execute('Market Data Processing Job')

if __name__ == "__main__":
    processor = MarketDataProcessor()
    processor.run()

# News sentiment processing job
class NewsSentimentProcessor:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.set_parallelism(8)
        
    def process_news_sentiment(self, news_stream):
        """Process news articles and extract sentiment"""
        
        def analyze_sentiment(json_str):
            """Analyze sentiment of news article"""
            try:
                article = json.loads(json_str)
                
                # Sentiment analysis (simplified - in production use proper NLP)
                title = article.get('title', '')
                content = article.get('content', '')
                
                # Extract mentioned symbols
                mentioned_symbols = self.extract_symbols(title + ' ' + content)
                
                # Calculate sentiment score
                sentiment_score = self.calculate_sentiment(title, content)
                
                # Categorize news
                category = self.categorize_news(title, content)
                
                result = {
                    'article_id': article.get('id'),
                    'symbols': mentioned_symbols,
                    'sentiment_score': sentiment_score,
                    'sentiment_category': self.categorize_sentiment(sentiment_score),
                    'news_category': category,
                    'published_at': article.get('published_at'),
                    'source': article.get('source'),
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                return json.dumps(result)
                
            except Exception as e:
                logging.error(f"Error analyzing sentiment: {e}")
                return None
        
        return news_stream.map(analyze_sentiment).filter(lambda x: x is not None)
    
    def extract_symbols(self, text):
        """Extract stock symbols from text"""
        import re
        
        # Find $SYMBOL patterns
        cashtag_pattern = r'\$([A-Z]{1,5})'
        cashtags = re.findall(cashtag_pattern, text.upper())
        
        # Find company name patterns (simplified)
        company_patterns = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'AMAZON': 'AMZN',
            'GOOGLE': 'GOOGL',
            'TESLA': 'TSLA'
        }
        
        mentioned_companies = []
        for company, symbol in company_patterns.items():
            if company in text.upper():
                mentioned_companies.append(symbol)
        
        return list(set(cashtags + mentioned_companies))
    
    def calculate_sentiment(self, title, content):
        """Calculate sentiment score (simplified)"""
        positive_words = ['bullish', 'gains', 'profit', 'growth', 'positive', 'up', 'rise']
        negative_words = ['bearish', 'losses', 'decline', 'negative', 'down', 'fall', 'crash']
        
        text = (title + ' ' + content).lower()
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count + negative_count == 0:
            return 0.0  # Neutral
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def categorize_sentiment(self, score):
        """Categorize sentiment score"""
        if score > 0.3:
            return 'positive'
        elif score < -0.3:
            return 'negative'
        else:
            return 'neutral'
    
    def categorize_news(self, title, content):
        """Categorize news type"""
        text = (title + ' ' + content).lower()
        
        if any(word in text for word in ['earnings', 'quarterly', 'revenue']):
            return 'earnings'
        elif any(word in text for word in ['merger', 'acquisition', 'deal']):
            return 'ma'
        elif any(word in text for word in ['fda', 'approval', 'drug']):
            return 'regulatory'
        elif any(word in text for word in ['guidance', 'forecast', 'outlook']):
            return 'guidance'
        else:
            return 'general'
```

## 🗄️ Data Storage Architecture

### Time-Series Database (TimescaleDB)
```sql
-- TimescaleDB configuration for market data
-- Create hypertables for time-series data

-- Market data hypertable
CREATE TABLE market_data_ts (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    volume BIGINT NOT NULL,
    bid DECIMAL(12,4),
    ask DECIMAL(12,4),
    bid_size INTEGER,
    ask_size INTEGER,
    
    -- Technical indicators
    sma_20 DECIMAL(12,4),
    sma_50 DECIMAL(12,4),
    rsi DECIMAL(5,2),
    bollinger_upper DECIMAL(12,4),
    bollinger_lower DECIMAL(12,4),
    
    -- Processing metadata
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50),
    
    PRIMARY KEY (time, symbol)
);

-- Convert to hypertable (partitioned by time)
SELECT create_hypertable('market_data_ts', 'time', 'symbol', 4);

-- Add compression policy (compress data older than 7 days)
ALTER TABLE market_data_ts SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('market_data_ts', INTERVAL '7 days');

-- Add retention policy (keep data for 2 years)
SELECT add_retention_policy('market_data_ts', INTERVAL '2 years');

-- News sentiment hypertable
CREATE TABLE news_sentiment_ts (
    time TIMESTAMPTZ NOT NULL,
    article_id UUID NOT NULL,
    symbols VARCHAR(20)[] NOT NULL,
    sentiment_score DECIMAL(5,4),
    sentiment_category VARCHAR(10),
    news_category VARCHAR(20),
    source VARCHAR(100),
    
    PRIMARY KEY (time, article_id)
);

SELECT create_hypertable('news_sentiment_ts', 'time');

-- Insider trading hypertable
CREATE TABLE insider_trading_ts (
    time TIMESTAMPTZ NOT NULL,
    filing_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    insider_name VARCHAR(200),
    insider_title VARCHAR(100),
    transaction_type VARCHAR(20),
    shares BIGINT,
    price DECIMAL(10,4),
    total_value DECIMAL(15,2),
    
    PRIMARY KEY (time, filing_id)
);

SELECT create_hypertable('insider_trading_ts', 'time', 'symbol', 4);

-- Indexes for query performance
CREATE INDEX idx_market_data_symbol_time ON market_data_ts (symbol, time DESC);
CREATE INDEX idx_market_data_price ON market_data_ts (price) WHERE price IS NOT NULL;
CREATE INDEX idx_news_sentiment_symbols ON news_sentiment_ts USING GIN (symbols);
CREATE INDEX idx_insider_trading_symbol_time ON insider_trading_ts (symbol, time DESC);

-- Continuous aggregates for common queries
CREATE MATERIALIZED VIEW daily_market_summary
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS day,
    symbol,
    first(price, time) AS open_price,
    max(price) AS high_price,
    min(price) AS low_price,
    last(price, time) AS close_price,
    sum(volume) AS total_volume,
    count(*) AS tick_count
FROM market_data_ts
GROUP BY day, symbol;

-- Refresh policy for continuous aggregates
SELECT add_continuous_aggregate_policy('daily_market_summary',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

### Object Storage (S3) Configuration
```yaml
# s3/bucket-configuration.yaml
data_lake_buckets:
  raw_data:
    bucket: waardhaven-raw-data
    versioning: enabled
    encryption: AES256
    lifecycle_policies:
      - id: raw_data_lifecycle
        status: enabled
        transitions:
          - days: 30
            storage_class: STANDARD_IA
          - days: 90
            storage_class: GLACIER
          - days: 2555  # 7 years
            storage_class: DEEP_ARCHIVE
    
  processed_data:
    bucket: waardhaven-processed-data
    versioning: enabled
    encryption: AES256
    lifecycle_policies:
      - id: processed_data_lifecycle
        status: enabled
        transitions:
          - days: 90
            storage_class: STANDARD_IA
          - days: 365
            storage_class: GLACIER
    
  ml_models:
    bucket: waardhaven-ml-models
    versioning: enabled
    encryption: KMS
    lifecycle_policies:
      - id: model_lifecycle
        status: enabled
        transitions:
          - days: 180
            storage_class: STANDARD_IA

# Data partitioning strategy
partitioning_scheme:
  market_data:
    path: s3://waardhaven-raw-data/market-data/year={year}/month={month}/day={day}/hour={hour}/
    format: parquet
    compression: snappy
    
  news_data:
    path: s3://waardhaven-raw-data/news/year={year}/month={month}/day={day}/
    format: json
    compression: gzip
    
  insider_trading:
    path: s3://waardhaven-raw-data/insider-trading/year={year}/month={month}/
    format: parquet
    compression: snappy
```

## 🔄 Batch Processing (Apache Spark)

### Spark Cluster Configuration
```yaml
# spark/spark-cluster.yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: daily-aggregation-job
  namespace: data-processing
spec:
  type: Scala
  mode: cluster
  image: "waardhaven/spark:3.5.0"
  imagePullPolicy: Always
  mainClass: com.waardhaven.spark.DailyAggregationJob
  mainApplicationFile: "s3a://waardhaven-spark-jobs/daily-aggregation-1.0.jar"
  
  # Spark configuration
  sparkConf:
    # Spark SQL
    "spark.sql.adaptive.enabled": "true"
    "spark.sql.adaptive.coalescePartitions.enabled": "true"
    "spark.sql.adaptive.skewJoin.enabled": "true"
    
    # Memory management
    "spark.sql.execution.arrow.pyspark.enabled": "true"
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
    
    # S3 configuration
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem"
    "spark.hadoop.fs.s3a.aws.credentials.provider": "com.amazonaws.auth.WebIdentityTokenCredentialsProvider"
    "spark.hadoop.fs.s3a.multipart.size": "128MB"
    "spark.hadoop.fs.s3a.fast.upload": "true"
    
    # Optimization
    "spark.sql.files.maxPartitionBytes": "128MB"
    "spark.sql.files.openCostInBytes": "4194304"
    
  # Resource allocation
  driver:
    cores: 2
    memory: "4g"
    serviceAccount: spark-service-account
    
    # Node selection
    nodeSelector:
      workload-type: data-processing
    
    tolerations:
      - key: workload-type
        value: data-processing
        effect: NoSchedule
    
    env:
      - name: AWS_REGION
        value: us-east-1
  
  executor:
    cores: 4
    instances: 10
    memory: "8g"
    
    # Node selection
    nodeSelector:
      workload-type: data-processing
    
    tolerations:
      - key: workload-type
        value: data-processing
        effect: NoSchedule
    
    env:
      - name: AWS_REGION
        value: us-east-1
  
  # Dependencies
  deps:
    jars:
      - "s3a://waardhaven-spark-deps/postgresql-42.6.0.jar"
      - "s3a://waardhaven-spark-deps/aws-java-sdk-bundle-1.12.500.jar"
      - "s3a://waardhaven-spark-deps/hadoop-aws-3.3.4.jar"
  
  # Monitoring
  monitoring:
    enabled: true
    prometheus:
      jmxExporterJar: "/opt/spark/jars/jmx_prometheus_javaagent-0.17.2.jar"
      port: 8090
  
  # Schedule
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```

### Data Quality Framework
```python
# data_quality/great_expectations_config.py
import great_expectations as ge
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.checkpoint import SimpleCheckpoint

class DataQualityValidator:
    def __init__(self):
        self.context = ge.get_context()
        
    def setup_market_data_expectations(self):
        """Setup expectations for market data quality"""
        
        # Create expectation suite
        suite = self.context.create_expectation_suite(
            expectation_suite_name="market_data_quality",
            overwrite_existing=True
        )
        
        # Data completeness expectations
        suite.expect_column_to_exist("symbol")
        suite.expect_column_to_exist("timestamp")
        suite.expect_column_to_exist("price")
        suite.expect_column_to_exist("volume")
        
        # Data validity expectations
        suite.expect_column_values_to_not_be_null("symbol")
        suite.expect_column_values_to_not_be_null("timestamp")
        suite.expect_column_values_to_not_be_null("price")
        
        # Data range expectations
        suite.expect_column_values_to_be_between("price", min_value=0.01, max_value=10000)
        suite.expect_column_values_to_be_between("volume", min_value=0, max_value=1000000000)
        
        # Data format expectations
        suite.expect_column_values_to_match_regex("symbol", "^[A-Z]{1,5}$")
        
        # Data freshness expectations
        suite.expect_column_max_to_be_between(
            "timestamp",
            min_value="2020-01-01",
            max_value=datetime.now() + timedelta(hours=1)
        )
        
        # Statistical expectations
        suite.expect_column_mean_to_be_between("volume", min_value=1000, max_value=100000000)
        
        return suite
    
    def validate_batch(self, df, suite_name):
        """Validate a batch of data"""
        
        # Create runtime batch request
        batch_request = RuntimeBatchRequest(
            datasource_name="pandas_datasource",
            data_connector_name="default_runtime_data_connector_name",
            data_asset_name="market_data_batch",
            runtime_parameters={"batch_data": df},
            batch_identifiers={"default_identifier_name": f"batch_{datetime.now().isoformat()}"}
        )
        
        # Create checkpoint
        checkpoint = SimpleCheckpoint(
            f"batch_checkpoint_{suite_name}",
            self.context,
            batch_request=batch_request,
            expectation_suite_name=suite_name
        )
        
        # Run validation
        results = checkpoint.run()
        
        return results
    
    def setup_automated_validation(self):
        """Setup automated validation in data pipeline"""
        
        # Kafka consumer for real-time validation
        def validate_stream_data(message):
            try:
                data = json.loads(message.value())
                df = pd.DataFrame([data])
                
                results = self.validate_batch(df, "market_data_quality")
                
                if not results.success:
                    # Alert on validation failure
                    self.send_data_quality_alert(results)
                    
                return results.success
                
            except Exception as e:
                logging.error(f"Validation error: {e}")
                return False
        
        return validate_stream_data
```

## 📊 Data Pipeline Monitoring

### Pipeline Metrics Collection
```python
# monitoring/pipeline_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics definitions
MESSAGES_PROCESSED = Counter(
    'pipeline_messages_processed_total',
    'Total number of messages processed',
    ['pipeline', 'topic', 'status']
)

PROCESSING_LATENCY = Histogram(
    'pipeline_processing_latency_seconds',
    'Time spent processing messages',
    ['pipeline', 'stage']
)

QUEUE_DEPTH = Gauge(
    'pipeline_queue_depth',
    'Number of messages in queue',
    ['pipeline', 'queue']
)

DATA_QUALITY_SCORE = Gauge(
    'pipeline_data_quality_score',
    'Data quality score (0-1)',
    ['pipeline', 'dataset']
)

class PipelineMonitor:
    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name
        
    def record_message_processed(self, topic, status='success'):
        """Record a processed message"""
        MESSAGES_PROCESSED.labels(
            pipeline=self.pipeline_name,
            topic=topic,
            status=status
        ).inc()
    
    def record_processing_time(self, stage, duration):
        """Record processing time for a stage"""
        PROCESSING_LATENCY.labels(
            pipeline=self.pipeline_name,
            stage=stage
        ).observe(duration)
    
    def update_queue_depth(self, queue_name, depth):
        """Update queue depth metric"""
        QUEUE_DEPTH.labels(
            pipeline=self.pipeline_name,
            queue=queue_name
        ).set(depth)
    
    def update_data_quality(self, dataset, score):
        """Update data quality score"""
        DATA_QUALITY_SCORE.labels(
            pipeline=self.pipeline_name,
            dataset=dataset
        ).set(score)

# Usage in processing jobs
class MonitoredProcessor:
    def __init__(self):
        self.monitor = PipelineMonitor('market-data-processor')
    
    def process_message(self, message):
        start_time = time.time()
        
        try:
            # Process the message
            result = self.do_processing(message)
            
            # Record success
            self.monitor.record_message_processed('market-data', 'success')
            
            return result
            
        except Exception as e:
            # Record failure
            self.monitor.record_message_processed('market-data', 'error')
            raise
            
        finally:
            # Record processing time
            duration = time.time() - start_time
            self.monitor.record_processing_time('processing', duration)
```

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Data ingestion rate | 1M events/second | - |
| Processing latency (p95) | <5 seconds | - |
| Data quality score | >99% | - |
| Pipeline uptime | >99.9% | - |
| Storage cost efficiency | 20% reduction annually | - |

---

**Next**: Continue with security and compliance framework.