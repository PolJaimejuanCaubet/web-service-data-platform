import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  Stock, 
  StockHistory, 
  MarketSummary, 
  AICorrelation, 
  TrendAnalysis,
  AIPrediction 
} from '../models/stock.models';

@Injectable({
  providedIn: 'root'
})
export class StockService {
  
  private apiUrl = 'http://localhost:8000/etl';

  constructor(private http: HttpClient) {}

  runETL(ticker: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${ticker}/run`, {});
  }

  getStockResults(ticker: string): Observable<Stock> {
    return this.http.get<Stock>(`${this.apiUrl}/${ticker}/results`);
  }

  getStockHistory(ticker: string): Observable<StockHistory[]> {
    return this.http.get<StockHistory[]>(`${this.apiUrl}/${ticker}/history`);
  }

  getMarketSummary(tickers: string[]): Observable<MarketSummary> {
    const params = new HttpParams().set('tickers', tickers.join(','));
    return this.http.get<MarketSummary>(`${this.apiUrl}/analytics/summary/`, { params });
  }

  getAICorrelation(ticker: string): Observable<AICorrelation> {
    return this.http.get<AICorrelation>(`${this.apiUrl}/analytics/correlation/${ticker}`);
  }

  getTrendAnalysis(tickers: string[]): Observable<TrendAnalysis> {
    const params = new HttpParams().set('tickers', tickers.join(','));
    return this.http.get<TrendAnalysis>(`${this.apiUrl}/analytics/trends`, { params });
  }

  getAnalyticsHistory(ticker: string): Observable<StockHistory[]> {
    return this.http.get<StockHistory[]>(`${this.apiUrl}/analytics/history/${ticker}`);
  }

  getAIPrediction(ticker: string): Observable<AIPrediction> {
    return this.http.get<AIPrediction>(`${this.apiUrl}/analytics/prediction/${ticker}`);
  }

  generateVideo(ticker: string): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/video-generation/${ticker}/run`, {}, {
      responseType: 'blob'
    });
  }
}