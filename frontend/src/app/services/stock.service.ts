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
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class StockService {
  
  private apiUrl = environment.apiUrl

  constructor(private http: HttpClient) {}

  runETL(ticker: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/etl/${ticker}/run`, {});
  }

  getStockResults(ticker: string): Observable<Stock> {
    return this.http.get<Stock>(`${this.apiUrl}/etl/${ticker}/results`);
  }

  getStockHistory(ticker: string): Observable<StockHistory[]> {
    return this.http.get<StockHistory[]>(`${this.apiUrl}/etl/${ticker}/history`);
  }

  getMarketSummary(tickers: string[]): Observable<MarketSummary> {
    const params = new HttpParams().set('tickers', tickers.join(','));
    return this.http.get<MarketSummary>(`${this.apiUrl}/etl/analytics/summary/`, { params });
  }

  getAICorrelation(ticker: string): Observable<AICorrelation> {
    return this.http.get<AICorrelation>(`${this.apiUrl}/etl/analytics/correlation/${ticker}`);
  }

  getTrendAnalysis(tickers: string[]): Observable<TrendAnalysis> {
    const params = new HttpParams().set('tickers', tickers.join(','));
    return this.http.get<TrendAnalysis>(`${this.apiUrl}/etl/analytics/trends`, { params });
  }

  getAnalyticsHistory(ticker: string): Observable<StockHistory[]> {
    return this.http.get<StockHistory[]>(`${this.apiUrl}/etl/analytics/history/${ticker}`);
  }

  getAIPrediction(ticker: string): Observable<AIPrediction> {
    return this.http.get<AIPrediction>(`${this.apiUrl}/etl/analytics/prediction/${ticker}`);
  }

  generateVideo(ticker: string): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/etl/video-generation/${ticker}/run`, {}, {
      responseType: 'blob'
    });
  }
}