import { ApiService } from './base';

export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
  symbols: string[];
  sentiment_score?: number;
  relevance_score?: number;
}

export interface EntitySentiment {
  symbol: string;
  name: string;
  sentiment_score: number;
  mention_count: number;
  articles: NewsArticle[];
}

export interface TrendingEntity {
  symbol: string;
  name: string;
  mention_count: number;
  sentiment_score: number;
  trend: 'up' | 'down' | 'stable';
}

class NewsService extends ApiService {
  async searchNews(params: {
    symbols?: string[];
    keywords?: string;
    sentimentMin?: number;
    sentimentMax?: number;
    publishedAfter?: string;
    publishedBefore?: string;
    limit?: number;
    offset?: number;
  }): Promise<NewsArticle[]> {
    const queryParams = new URLSearchParams();
    
    if (params.symbols?.length) {
      queryParams.append('symbols', params.symbols.join(','));
    }
    if (params.keywords) {
      queryParams.append('keywords', params.keywords);
    }
    if (params.sentimentMin !== undefined) {
      queryParams.append('sentiment_min', params.sentimentMin.toString());
    }
    if (params.sentimentMax !== undefined) {
      queryParams.append('sentiment_max', params.sentimentMax.toString());
    }
    if (params.publishedAfter) {
      queryParams.append('published_after', params.publishedAfter);
    }
    if (params.publishedBefore) {
      queryParams.append('published_before', params.publishedBefore);
    }
    if (params.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    if (params.offset) {
      queryParams.append('offset', params.offset.toString());
    }
    
    return this.get<NewsArticle[]>(`/api/v1/news/search?${queryParams.toString()}`);
  }

  async getEntitySentiment(symbol: string): Promise<EntitySentiment> {
    return this.get<EntitySentiment>(`/api/v1/news/sentiment/${symbol}`);
  }

  async getTrendingEntities(): Promise<TrendingEntity[]> {
    return this.get<TrendingEntity[]>('/api/v1/news/trending');
  }

  async refreshNews(): Promise<{ message: string }> {
    return this.post('/api/v1/news/refresh');
  }
}

export const newsService = new NewsService();