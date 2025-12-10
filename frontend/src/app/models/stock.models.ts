// src/app/models/stock.models.ts

export interface Stock {
  ticker: string;
  name: string;
  currency: string;
  price: number;
  day_change: number;
  last_updated: string;
  _id?: string;
}

export interface StockHistory {
  ticker: string;
  price: number;
  day_change: number;
  timestamp: string;
  _id?: string;
}

export interface MarketSummary {
  tickers: string[];
  average_price: number;
  average_day_change: number;
  top_gainer: Stock;
  top_loser: Stock;
}

export interface AICorrelation {
  ticker: string;
  stock_data: Stock;
  ai_analysis: string;
}

export interface TrendAnalysis {
  total: number;
  up: Stock[];
  down: Stock[];
  stable: Stock[];
}

export interface AIPrediction {
  ticker: string;
  price: number;
  prediction: string;
}